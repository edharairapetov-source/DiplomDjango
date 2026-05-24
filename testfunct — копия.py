import pandas as pd
from django import test
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
from .models import QuantAnalysis, Company, GNNPrediction

class QuantAppFunctionalTest(test.TestCase):
    """
    Полное функциональное тестирование Django-приложения.
    Покрывает: Аутентификацию, Лабораторию (аналитику), 
    API котировок и GNN-прогнозы.
    """

    def setUp(self):
        # 1. Создаем тестового пользователя
        self.username = "test_quant_user"
        self.password = "secure_password_123"
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.client = test.Client()

    # --- Тесты Аутентификации ---

    def test_registration_flow(self):
        """Проверка регистрации нового пользователя"""
        response = self.client.post(reverse('register'), {
            'username': 'new_user',
            'password': 'Password123!',
            'password_confirm': 'Password123!'
        })
        # Проверяем редирект на логин после успешной регистрации
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='new_user').exists())

    def test_dashboard_access_restricted(self):
        """Проверка защиты дашборда от анонимных пользователей"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    # --- Тесты Функционала Аналитики (Quant Lab) ---

    @patch('analysis.views.run_analysis_clean') # Замените 'analysis' на имя вашего приложения
    def test_dashboard_calculation_and_save(self, mock_analysis):
        """Проверка выполнения расчетов и сохранения в БД QuantAnalysis"""
        self.client.login(username=self.username, password=self.password)
        
        # Имитируем успешный результат работы движка аналитики
        mock_analysis.return_value = {
            'final_metrics': {'VaR': 0.05, 'Expected Return': 0.12},
            'plot_data': 'base64_string'
        }

        payload = {
            "n_stocks": "12",
            "corr_threshold": "0.5",
            "min_er": "0.02",
            "max_er": "0.15",
            "S0": "100",
            "K": "105",
            "T": "1",
            "r": "0.05",
            "sigma": "0.2"
        }
        
        response = self.client.post(reverse('dashboard'), payload)
        
        self.assertEqual(response.status_code, 200)
        # Проверяем, что данные сохранились в модель QuantAnalysis
        self.assertTrue(QuantAnalysis.objects.filter(user=self.user).exists())
        last_calc = QuantAnalysis.objects.filter(user=self.user).latest('id')
        self.assertEqual(last_calc.n_stocks, 12)

    # --- Тесты GNN и Интеграции ---

    @patch('analysis.views.get_gnn_predictions')
    def test_gnn_view_and_db_persistence(self, mock_gnn):
        """Тест получения GNN прогнозов и записи в базу Company/GNNPrediction"""
        self.client.login(username=self.username, password=self.password)
        
        # Имитируем данные от GNN движка
        mock_gnn.return_value = [
            {'ticker': 'AAPL', 'current_mu': 0.1, 'sigma': 0.2, 'prediction': 0.15},
            {'ticker': 'TSLA', 'current_mu': 0.05, 'sigma': 0.4, 'prediction': -0.02}
        ]

        response = self.client.post(reverse('gnn_predictions_view'), {'run_gnn': 'true'})
        
        self.assertEqual(response.status_code, 200)
        # Проверка создания объектов в БД (логика save_predictions_to_db)
        self.assertTrue(Company.objects.filter(ticker='AAPL').exists())
        self.assertTrue(GNNPrediction.objects.filter(company__ticker='TSLA').exists())

    # --- Тесты API и JSON ответов ---

    @patch('yfinance.download')
    def test_live_yfinance_api_response(self, mock_yf):
        """Тестирование AJAX-запроса к yfinance"""
        # Создаем фейковый DataFrame, который ожидает ваш код
        df = pd.DataFrame({
            'Open': [100.0], 'High': [110.0], 'Low': [90.0], 
            'Close': [105.0], 'Volume': [1000]
        }, index=[pd.Timestamp.now()])
        mock_yf.return_value = df

        response = self.client.get(reverse('live_yfinance'), {'ticker': 'MSFT'})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['ticker'], 'MSFT')
        self.assertIn('price', response.json())

    def test_logout(self):
        """Проверка выхода из системы"""
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)