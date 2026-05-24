import json
from unittest.mock import patch
import pandas as pd
import numpy as np
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import QuantAnalysis, QuantLab3Result

class QuantAppFunctionalTests(TestCase):

    def setUp(self):
        """Настройка окружения перед каждым тестом"""
        self.client = Client()
        self.user_password = "testpassword123"
        self.user = User.objects.create_user(
            username="testuser", 
            password=self.user_password
        )
        self.dashboard_url = reverse('dashboard')
        self.quant_lab_url = reverse('quant_lab')
        self.live_yf_url = reverse('live_yfinance')

    # --- ТЕСТЫ ДОСТУПА ---

    def test_dashboard_requires_login(self):
        """Проверка, что неавторизованных пользователей редиректит на логин"""
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_dashboard_accessible_after_login(self):
        """Проверка доступа к дашборду после авторизации"""
        self.client.login(username="testuser", password=self.user_password)
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analysis/dashboard.html')

    # --- ТЕСТЫ ЛОГИКИ АНАЛИЗА (MOCKING YFINANCE) ---

    @patch('yfinance.download')
    def test_quant_lab_post_success(self, mock_yf):
        """Тест проведения анализа в Quant Lab с имитацией данных Yahoo Finance"""
        self.client.login(username="testuser", password=self.user_password)
        
        # Создаем фейковые данные для yfinance
        dates = pd.date_range(start="2024-01-01", periods=10)
        mock_data = pd.DataFrame(
            np.random.uniform(100, 200, size=(10, 2)),
            index=dates,
            columns=['AAPL', 'MSFT']
        )
        mock_yf.return_value = mock_data

        payload = {
            'tickers': 'AAPL,MSFT',
            'stress_test': 'none',
            'n_stocks': 2,
            'mu': 0.1,
            'sigma': 0.2
        }

        response = self.client.post(self.quant_lab_url, data=payload)

        # Проверяем успешный ответ
        self.assertEqual(response.status_code, 200)
        # Проверяем, создалась ли запись в базе данных
        self.assertTrue(QuantAnalysis.objects.filter(user=self.user).exists())
        # Проверяем наличие метрик в контексте
        self.assertIn('var', response.context)
        self.assertIn('frontier_img', response.context)

    # --- ТЕСТЫ API (JSON) ---

    @patch('yfinance.download')
    def test_live_yfinance_api(self, mock_yf):
        """Тест API эндпоинта для живых данных"""
        # Настройка мока для 1-минутных данных
        mock_df = pd.DataFrame({
            'Open': [150.0], 'High': [155.0], 'Low': [149.0], 
            'Close': [152.0], 'Volume': [1000]
        }, index=[pd.Timestamp.now()])
        mock_yf.return_value = mock_df

        response = self.client.get(self.live_yf_url, {'ticker': 'AAPL'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['ticker'], 'AAPL')
        self.assertIn('close', data)
        self.assertEqual(data['close'][0], 152.0)

    # --- ТЕСТЫ ОШИБОК ---

    @patch('yfinance.download')
    def test_quant_lab_invalid_tickers(self, mock_yf):
        """Тест обработки ошибки, если yfinance не нашел тикеры"""
        self.client.login(username="testuser", password=self.user_password)
        
        # Возвращаем пустой DataFrame
        mock_yf.return_value = pd.DataFrame()

        response = self.client.post(self.quant_lab_url, {'tickers': 'INVALID_TICKER'})
        
        # Проверяем, что ошибка отображается пользователю
        self.assertIn('error', response.context)

    def test_registration_flow(self):
        """Тест процесса регистрации нового пользователя"""
        registration_url = reverse('register')
        payload = {
            'username': 'newuser',
            'password1': 'newpassword123',
            'password2': 'newpassword123'
        }
        # Примечание: UserCreationForm использует поля по умолчанию, 
        # проверьте имена полей в вашем шаблоне (обычно password1, password2)
        response = self.client.post(registration_url, data=payload)
        self.assertEqual(response.status_code, 200) # Вернет 200, если форма невалидна или 302 при успехе
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        # --- ДОПОЛНИТЕЛЬНЫЕ МАТЕМАТИЧЕСКИЕ ТЕСТЫ ---

    @patch('yfinance.download')
    def test_stress_test_impact_on_var(self, mock_yf):
        """
        Проверка: Value at Risk (VaR) должен увеличиваться 
        при выборе сценария 'Black Monday' (-20% шок).
        """
        self.client.login(username="testuser", password=self.user_password)
        
        # Генерируем стабильный растущий тренд
        dates = pd.date_range(start="2024-01-01", periods=100)
        mock_data = pd.DataFrame({
            'AAPL': np.linspace(100, 110, 100),
            'MSFT': np.linspace(200, 220, 100)
        }, index=dates)
        mock_yf.return_value = mock_data

        # 1. Запрос без стресс-теста
        res_normal = self.client.post(self.quant_lab_url, {
            'tickers': 'AAPL,MSFT', 'stress_test': 'none', 'n_stocks': 2
        })
        var_normal = res_normal.context['var']

        # 2. Запрос со стресс-тестом (Black Monday)
        res_stress = self.client.post(self.quant_lab_url, {
            'tickers': 'AAPL,MSFT', 'stress_test': 'black_monday', 'n_stocks': 2
        })
        var_stress = res_stress.context['var']

        # Математическая проверка: VaR при шоке должен быть выше (хуже)
        self.assertGreater(abs(var_stress), abs(var_normal), 
                           "VaR должен расти при наложении стресс-сценария")

    def test_portfolio_optimization_math(self):
        """
        Проверка логики расчета долей (Weights). 
        Сумма весов в портфеле всегда должна быть равна 1.0 (100%).
        """
        self.client.login(username="testuser", password=self.user_password)
        
        # Предположим, у нас есть метод доступа к результатам последнего анализа
        # (или мы берем их из базы данных после POST-запроса)
        response = self.client.post(self.quant_lab_url, {
            'tickers': 'AAPL,MSFT,GOOG', 'stress_test': 'none', 'n_stocks': 3
        })
        
        last_result = QuantLab3Result.objects.filter(user=self.user).latest('id')
        weights = json.loads(last_result.weights_json) # Если веса хранятся в JSON
        
        total_weight = sum(weights.values())
        
        # Проверка с допуском на точность float
        self.assertAlmostEqual(total_weight, 1.0, places=4, 
                               msg="Сумма весов портфеля должна быть равна 100%")
        
        
        
        
        
        
        
        
        
        
        
        
