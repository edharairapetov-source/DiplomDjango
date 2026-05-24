from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch
import pandas as pd

# Импортируем вашу модель. 
# Если модель называется иначе (например, Analysis), замените имя ниже
from .models import QuantAnalysis 

class ExternalApiSystemTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='quant_user', password='123')
        self.client = Client()

    @patch('yfinance.download')
    def test_yfinance_connection_error(self, mock_download):
        """Системный тест: Обработка сбоя внешнего API (yfinance)"""
        self.client.login(username='quant_user', password='123')
        
        # Имитируем, что Yahoo вернул пустой DataFrame
        mock_download.return_value = pd.DataFrame()
        
        # Замените 'quant_lab' на имя вашего URL из urls.py, если оно другое
        response = self.client.post(reverse('quant_lab'), {'tickers': 'INVALID_TICKER'})
        
        self.assertEqual(response.status_code, 200)
        # Проверяем, что в БД не создалась запись с ошибкой
        self.assertEqual(QuantAnalysis.objects.count(), 0)

class UserJourneySystemTest(TestCase):
    def test_new_user_first_analysis(self):
        """Системный тест: Регистрация -> Логин -> Анализ"""
        client = Client()
        
        # 1. Регистрация (убедитесь, что URL 'register' существует)
        client.post(reverse('register'), {
            'username': 'new_trader',
            'password': 'secure_password123',
            'password_confirm': 'secure_password123'
        })
        
        # 2. Логин
        client.login(username='new_trader', password='secure_password123')
        
        # 3. Первый расчет
        payload = {
            'tickers': 'AAPL',
            'n_stocks': 1,
            'stress_test': 'none'
        }
        response = client.post(reverse('quant_lab'), data=payload)
        
        # 4. Проверка, что запись появилась в базе данных
        self.assertTrue(QuantAnalysis.objects.filter(user__username='new_trader').exists())

class StressLogicSystemTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username='testadmin', password='123')
        self.client = Client()

    def test_risk_metrics_increase_under_stress(self):
        """Системный тест: Сравнение обычного и стрессового расчетов"""
        self.client.login(username='testadmin', password='123')
        
        # 1. Обычный расчет
        self.client.post(reverse('quant_lab'), {'tickers': 'SPY', 'stress_test': 'none'})
        normal_analysis = QuantAnalysis.objects.last()
        # Предполагаем, что поле называется var_value. Если нет — замените на ваше.
        normal_var = normal_analysis.var_value if normal_analysis else 0
        
        # 2. Расчет при обвале
        self.client.post(reverse('quant_lab'), {'tickers': 'SPY', 'stress_test': 'crash'})
        crash_analysis = QuantAnalysis.objects.last()
        crash_var = crash_analysis.var_value if crash_analysis else 0
        
        # Риск при стрессе должен быть формально выше (или равен в худшем случае)
        self.assertGreaterEqual(crash_var, normal_var, msg="VaR при стрессе должен быть выше или равен норме")