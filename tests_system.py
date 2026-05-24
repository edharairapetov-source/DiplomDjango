from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch
import pandas as pd


from .models import QuantAnalysis 

class ExternalApiSystemTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='quant_user', password='123')
        self.client = Client()

    @patch('yfinance.download')
    def test_yfinance_connection_error(self, mock_download):
        """Системный тест: Обработка сбоя внешнего API (yfinance)"""
        self.client.login(username='quant_user', password='123')
        
        
        mock_download.return_value = pd.DataFrame()
        
       
        response = self.client.post(reverse('quant_lab'), {'tickers': 'INVALID_TICKER'})
        
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(QuantAnalysis.objects.count(), 0)

class UserJourneySystemTest(TestCase):
    def test_new_user_first_analysis(self):
        """Системный тест: Регистрация -> Логин -> Анализ"""
        client = Client()
        
     
        client.post(reverse('register'), {
            'username': 'new_trader',
            'password': 'secure_password123',
            'password_confirm': 'secure_password123'
        })
        
        
        client.login(username='new_trader', password='secure_password123')
        
        
        payload = {
            'tickers': 'AAPL',
            'n_stocks': 1,
            'stress_test': 'none'
        }
        response = client.post(reverse('quant_lab'), data=payload)
        
        
        self.assertTrue(QuantAnalysis.objects.filter(user__username='new_trader').exists())

class StressLogicSystemTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username='testadmin', password='123')
        self.client = Client()

    def test_risk_metrics_increase_under_stress(self):
        """Системный тест: Сравнение обычного и стрессового расчетов"""
        self.client.login(username='testadmin', password='123')
        
       
        self.client.post(reverse('quant_lab'), {'tickers': 'SPY', 'stress_test': 'none'})
        normal_analysis = QuantAnalysis.objects.last()
        
        normal_var = normal_analysis.var_value if normal_analysis else 0

        self.client.post(reverse('quant_lab'), {'tickers': 'SPY', 'stress_test': 'crash'})
        crash_analysis = QuantAnalysis.objects.last()
        crash_var = crash_analysis.var_value if crash_analysis else 0
        
     
        self.assertGreaterEqual(crash_var, normal_var, msg="VaR при стрессе должен быть выше или равен норме")
        
        
        
        
        
        
        
        
        
        
        
        
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch
import pandas as pd


from .models import QuantAnalysis 

class FullSystemDatabaseTest(TestCase):
    def setUp(self):
        """Подготовка: создаем пользователя в тестовой БД"""
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client = Client()

    @patch('yfinance.download')
    def test_complete_flow_to_database(self, mock_download):
        """
        СИСТЕМНЫЙ ТЕСТ: 
        Ввод данных -> Расчет -> Проверка записи в БД
        """
       
        data = {
            'Close': [150.0, 155.0, 160.0],
            'Open': [149.0, 154.0, 159.0]
        }
        mock_download.return_value = pd.DataFrame(data)

       
        self.client.login(username='testuser', password='password123')

       
        payload = {
            'tickers': 'AAPL',
            'n_stocks': 1,
            'stress_test': 'none'
        }
        
        response = self.client.post(reverse('quant_lab'), data=payload)

       
        self.assertEqual(QuantAnalysis.objects.count(), 1, "Запись не была создана в БД!")

       
        analysis_entry = QuantAnalysis.objects.first()
        self.assertEqual(analysis_entry.user, self.user)
        
        print(f"\n[УСПЕХ] Запись в БД создана. ID: {analysis_entry.id}, Тикер: {payload['tickers']}")

    def test_database_is_empty_on_fail(self):
        """Проверка целостности: если данные неверны, в БД ничего не должно попасть"""
        self.client.login(username='testuser', password='password123')
        

        self.client.post(reverse('quant_lab'), data={'tickers': ''})
        

        self.assertEqual(QuantAnalysis.objects.count(), 0, "В БД попала пустая или ошибочная запись!")