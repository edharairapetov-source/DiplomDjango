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
       
        self.client = Client()
        self.user_password = "testpassword123"
        self.user = User.objects.create_user(
            username="testuser", 
            password=self.user_password
        )
        self.dashboard_url = reverse('dashboard')
        self.quant_lab_url = reverse('quant_lab')
        self.live_yf_url = reverse('live_yfinance')

   

    def test_dashboard_requires_login(self):
        
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_dashboard_accessible_after_login(self):
       
        self.client.login(username="testuser", password=self.user_password)
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analysis/dashboard.html')

    

    @patch('yfinance.download')
    def test_quant_lab_post_success(self, mock_yf):
        
        self.client.login(username="testuser", password=self.user_password)
        
       
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

       
        self.assertEqual(response.status_code, 200)
        
        self.assertTrue(QuantAnalysis.objects.filter(user=self.user).exists())
       
        self.assertIn('var', response.context)
        self.assertIn('frontier_img', response.context)

    

    @patch('yfinance.download')
    def test_live_yfinance_api(self, mock_yf):
       
       
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

   

    @patch('yfinance.download')
    def test_quant_lab_invalid_tickers(self, mock_yf):
       
        self.client.login(username="testuser", password=self.user_password)
        
       
        mock_yf.return_value = pd.DataFrame()

        response = self.client.post(self.quant_lab_url, {'tickers': 'INVALID_TICKER'})
        
       
        self.assertIn('error', response.context)

    def test_registration_flow(self):
       
        registration_url = reverse('register')
        payload = {
            'username': 'newuser',
            'password1': 'newpassword123',
            'password2': 'newpassword123'
        }
       
        response = self.client.post(registration_url, data=payload)
        self.assertEqual(response.status_code, 200) 
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
      
    @patch('yfinance.download')
    def test_stress_test_impact_on_var(self, mock_yf):
       
        self.client.login(username="testuser", password=self.user_password)
        
        
        dates = pd.date_range(start="2024-01-01", periods=100)
        mock_data = pd.DataFrame({
            'AAPL': np.linspace(100, 110, 100),
            'MSFT': np.linspace(200, 220, 100)
        }, index=dates)
        mock_yf.return_value = mock_data

       
        res_normal = self.client.post(self.quant_lab_url, {
            'tickers': 'AAPL,MSFT', 'stress_test': 'none', 'n_stocks': 2
        })
        var_normal = res_normal.context['var']

      
        res_stress = self.client.post(self.quant_lab_url, {
            'tickers': 'AAPL,MSFT', 'stress_test': 'black_monday', 'n_stocks': 2
        })
        var_stress = res_stress.context['var']

        
        self.assertGreater(abs(var_stress), abs(var_normal), 
                           "VaR должен расти при наложении стресс-сценария")

    def test_portfolio_optimization_math(self):
       
        self.client.login(username="testuser", password=self.user_password)
        
        
        response = self.client.post(self.quant_lab_url, {
            'tickers': 'AAPL,MSFT,GOOG', 'stress_test': 'none', 'n_stocks': 3
        })
        
        last_result = QuantLab3Result.objects.filter(user=self.user).latest('id')
        weights = json.loads(last_result.weights_json) # Если веса хранятся в JSON
        
        total_weight = sum(weights.values())
        
       
        self.assertAlmostEqual(total_weight, 1.0, places=4, 
                               msg="Сумма весов портфеля должна быть равна 100%")
        
        
        
        
        
        
        
        
        
        
        
        
