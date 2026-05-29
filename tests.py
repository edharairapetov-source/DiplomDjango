import json
import numpy as np
import pandas as pd
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
from .models import QuantAnalysis, QuantAnalysisbi, SimulationRecord

class QuantAppTests(TestCase):
    def setUp(self):
        
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.login_url = reverse('login')  
        self.dashboard_url = reverse('dashboard')
        self.quant_lab7_url = reverse('quant_lab7')
        self.live_yf_url = reverse('live_yfinance')

   

    def test_dashboard_requires_login(self):
        """Проверка, что dashboard защищен декоратором @login_required."""
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)  

    def test_register_view_get(self):
       
        url = reverse('register')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analysis/register.html')

    

    @patch('analysis.views.run_analysis_clean')
    def test_dashboard_post_success(self, mock_run_analysis):
        
        self.client.login(username='testuser', password='password123')
        
        
        mock_run_analysis.return_value = {
            "expected_return": 0.15,
            "risk": 0.05,
            "sharpe_ratio": 3.0,
            "technical_indicators": {"SMA_5": 100}
        }

        data = {
            "n_stocks": 5,
            "corr_threshold": 0.5,
            "tickers": "AAPL,MSFT"
        }
        
        response = self.client.post(self.dashboard_url, data)
        
        self.assertEqual(response.status_code, 200)
        
        self.assertTrue(SimulationRecord.objects.filter(user=self.user).exists())

  

    def test_quant_lab7_calculation_logic(self):
        
        self.client.login(username='testuser', password='password123')
        
        post_data = {
            "n_stocks": "2",
            "mu": "0.1",
            "sigma": "0.2"
        }
        
        response = self.client.post(self.quant_lab7_url, post_data)
        
        self.assertEqual(response.status_code, 200)
        
        self.assertIn('var', response.context)
        self.assertIn('hit_rate', response.context)
        
        self.assertEqual(QuantAnalysis.objects.count(), 1)

    

    @patch('yfinance.download')
    def test_live_yfinance_api_success(self, mock_yf):
       
       
        mock_df = pd.DataFrame({
            'Open': [150.0], 'High': [155.0], 'Low': [149.0], 
            'Close': [152.0], 'Volume': [1000]
        }, index=pd.DatetimeIndex(['2023-01-01 10:00:00']))
        
        mock_yf.return_value = mock_df

        response = self.client.get(self.live_yf_url, {'ticker': 'AAPL'})
        
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data['ticker'], 'AAPL')
        self.assertEqual(json_data['close'], [152.0])

    @patch('yfinance.download')
    def test_live_yfinance_api_error(self, mock_yf):
        """Тест обработки ошибки, если yfinance вернул пустые данные."""
        mock_yf.return_value = pd.DataFrame()
        
        response = self.client.get(self.live_yf_url, {'ticker': 'INVALID'})
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    

    def test_unified_quant_bi_pro_stats(self):
        
        self.client.login(username='testuser', password='password123')
        
        
        QuantAnalysisbi.objects.create(user=self.user, mu=10, var_value=0.5, power_bi_metrics=10, n_stocks=5)
        QuantAnalysisbi.objects.create(user=self.user, mu=20, var_value=0.7, power_bi_metrics=20, n_stocks=5)

        url = reverse('unified_quant_bi_pro')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(response.context['bi_stats']['avg_mu'], 15.0)
       
        history_json = json.loads(response.context['history_json'])
        self.assertEqual(len(history_json), 2)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
import json
import numpy as np
import pandas as pd
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
from analysis.models import QuantAnalysis, QuantAnalysisbi, SimulationRecord

class QuantAppTests(TestCase):
    def setUp(self):
       
        self.client = Client()
        
        self.user = User.objects.create_user(username='testuser', password='password123')
        
       
        self.dashboard_url = reverse('dashboard')
        self.register_url = reverse('register')
        self.quant_lab_url = reverse('quant_lab')
        self.live_yf_url = reverse('live_yfinance')
        self.bi_url = reverse('unified_quant_bi_pro')

   

    def test_dashboard_requires_login(self):
       
        response = self.client.get(self.dashboard_url)
       
        self.assertEqual(response.status_code, 302)

    def test_register_view_get(self):
       
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)

   

    @patch('analysis.views.run_analysis_clean')
    def test_dashboard_post_success(self, mock_run_analysis):
       
        self.client.login(username='testuser', password='password123')
        
        mock_run_analysis.return_value = {
            "expected_return": 0.15,
            "risk": 0.05,
            "sharpe_ratio": 3.0,
            "technical_indicators": {"SMA_5": 100}
        }

        data = {"n_stocks": 5, "corr_threshold": 0.5, "tickers": "AAPL,MSFT"}
        response = self.client.post(self.dashboard_url, data)
        
        self.assertEqual(response.status_code, 200)

    def test_quant_lab_calculation_logic(self):
       
        self.client.login(username='testuser', password='password123')
        
        post_data = {
            "n_stocks": "2",
            "mu": "0.1",
            "sigma": "0.2"
        }
        
        response = self.client.post(self.quant_lab_url, post_data)
        
        self.assertEqual(response.status_code, 200)
        
        self.assertIn('var', response.context)
        self.assertIn('hit_rate', response.context)

   

    @patch('yfinance.download')
    def test_live_yfinance_api_success(self, mock_yf):
      
        mock_df = pd.DataFrame({
            'Open': [150.0], 'High': [155.0], 'Low': [149.0], 
            'Close': [152.0], 'Volume': [1000]
        }, index=pd.DatetimeIndex(['2023-01-01 10:00:00']))
        
        mock_yf.return_value = mock_df

        response = self.client.get(self.live_yf_url, {'ticker': 'AAPL'})
        
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data['ticker'], 'AAPL')
        self.assertIn('close', json_data)

    

    def test_unified_quant_bi_pro_stats(self):
        
        self.client.login(username='testuser', password='password123')
        
        
        QuantAnalysisbi.objects.create(user=self.user, mu=10, var_value=0.5, power_bi_metrics=10, n_stocks=5)
        QuantAnalysisbi.objects.create(user=self.user, mu=20, var_value=0.7, power_bi_metrics=20, n_stocks=5)

        response = self.client.get(self.bi_url)

        self.assertEqual(response.status_code, 200)
       
        self.assertEqual(response.context['bi_stats']['avg_mu'], 15.0)
