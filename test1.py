
from django.test import TestCase
from django.contrib.auth.models import User
from analysis.models import QuantAnalysis, SimulationRecord # Убрали точку!
from django.test import TestCase, Client  # Добавьте Client сюда
import json
from unittest.mock import patch
import numpy as np
from django.urls import reverse

class QuantLabTests(TestCase):

    def setUp(self):
        # Создаем пользователя для тестирования защищенных views
        self.username = "testuser"
        self.password = "password123"
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.client = Client()

    # --- ТЕСТЫ ДОСТУПА И РЕГИСТРАЦИИ ---

    def test_register_view_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analysis/register.html')

    def test_dashboard_requires_login(self):
        # Проверяем, что без логина кидает на страницу авторизации
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)

    # --- ТЕСТЫ QUANT LAB (Расчеты) ---

    def test_quant_lab_post_calculation(self):
        self.client.login(username=self.username, password=self.password)
        
        # Данные формы
        data = {
            "n_stocks": 5,
            "mu": 0.15,
            "sigma": 0.25
        }
        
        response = self.client.post(reverse('quant_lab7'), data)
        
        self.assertEqual(response.status_code, 200)
        # Проверяем, что в контексте появились результаты расчетов
        self.assertIn('var', response.context)
        self.assertIn('cvar', response.context)
        
        # Проверяем, что запись создалась в БД
        self.assertEqual(QuantAnalysis.objects.filter(user=self.user).count(), 1)
        record = QuantAnalysis.objects.first()
        self.assertEqual(record.n_stocks, 3)

    # --- ТЕСТЫ API (Yahoo Finance) ---

    @patch('yfinance.download')
    def test_live_yfinance_api(self, mock_download):
        # Имитируем ответ от yfinance, чтобы не делать реальных запросов
        import pandas as pd
        mock_df = pd.DataFrame(
            {
                "Open": [100.0], "High": [105.0], "Low": [95.0], 
                "Close": [102.0], "Volume": [1000]
            },
            index=pd.DatetimeIndex(['2023-01-01 10:00:00'])
        )
        mock_download.return_value = mock_df

        response = self.client.get(reverse('live_yfinance'), {'ticker': 'AAPL'})
        
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data['ticker'], 'AAPL')
        self.assertEqual(json_data['close'], [102.0])

    # --- ТЕСТ PYTHON КОНСОЛИ ---

    def test_python_console_execution(self):
        # Проверяем выполнение кода в консоли
        code = "result = 2 + 2\nprint('Hello Test')"
        response = self.client.post(reverse('python_console'), {'code': code})
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Hello Test', response.context['output'])
        self.assertIn('Result:\n4', response.context['output'])

    def test_python_console_numpy(self):
        # Проверяем работу с финансовыми функциями в консоли
        code = "import numpy as np\nprices = [100, 105, 110]\nr = returns(prices)\nresult = len(r)"
        response = self.client.post(reverse('python_console'), {'code': code})
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Result:\n2', response.context['output'])