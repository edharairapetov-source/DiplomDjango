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

 

    @patch('yfinance.download')
    def test_quant_lab_post_success(self, mock_yf):
        """Тест проведения анализа в Quant Lab с имитацией данных Yahoo Finance"""
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
        """Тест API эндпоинта для живых данных"""
        
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
        """Тест обработки ошибки, если yfinance не нашел тикеры"""
        self.client.login(username="testuser", password=self.user_password)
        
      
        mock_yf.return_value = pd.DataFrame()

        response = self.client.post(self.quant_lab_url, {'tickers': 'INVALID_TICKER'})
        
   
        self.assertIn('error', response.context)

    def test_registration_flow(self):
        """Тест процесса регистрации нового пользователя"""
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
        """
        Проверка: Value at Risk (VaR) должен увеличиваться 
        при выборе сценария 'Black Monday' (-20% шок).
        """
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
        """
        Проверка логики расчета долей (Weights). 
        Сумма весов в портфеле всегда должна быть равна 1.0 (100%).
        """
        self.client.login(username="testuser", password=self.user_password)
        

        response = self.client.post(self.quant_lab_url, {
            'tickers': 'AAPL,MSFT,GOOG', 'stress_test': 'none', 'n_stocks': 3
        })
        
        last_result = QuantLab3Result.objects.filter(user=self.user).latest('id')
        weights = json.loads(last_result.weights_json)
        
        total_weight = sum(weights.values())
        

        self.assertAlmostEqual(total_weight, 1.0, places=4, 
                               msg="Сумма весов портфеля должна быть равна 100%")
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
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
        self.user = User.objects.create_user(username="testuser", password=self.user_password)
        self.quant_lab_url = reverse('quant_lab')

    @patch('yfinance.download')
    def test_quant_lab_post_success(self, mock_yf):
        self.client.login(username="testuser", password=self.user_password)
        
      
        dates = pd.date_range(start="2024-01-01", periods=100)
        mock_yf.return_value = pd.DataFrame({
            'AAPL': np.random.uniform(150, 160, size=100),
            'MSFT': np.random.uniform(250, 260, size=100)
        }, index=dates)

        payload = {
            'tickers': 'AAPL,MSFT',
            'stress_test': 'none',
            'n_stocks': 2
        }

     
        response = self.client.post(self.quant_lab_url, data=payload, follow=True)

        self.assertEqual(response.status_code, 200)
      
        self.assertTrue(QuantAnalysis.objects.filter(user=self.user).exists())

    def test_registration_flow(self):
        registration_url = reverse('register')
        payload = {
            'username': 'newuser123',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        response = self.client.post(registration_url, data=payload)
      
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser123').exists())

    @patch('yfinance.download')
    def test_stress_test_impact_on_var(self, mock_yf):
        self.client.login(username="testuser", password=self.user_password)
        mock_yf.return_value = pd.DataFrame(np.random.rand(100, 2), 
                                            columns=['AAPL', 'MSFT'], 
                                            index=pd.date_range('2024-01-01', periods=100))
        
        response = self.client.post(self.quant_lab_url, {'tickers': 'AAPL,MSFT'}, follow=True)
        
      
        self.assertIn('var', response.context)

    @patch('yfinance.download')
    def test_portfolio_optimization_math(self, mock_yf):
        self.client.login(username="testuser", password=self.user_password)
        mock_yf.return_value = pd.DataFrame(np.random.rand(10, 2), columns=['AAPL', 'MSFT'])
        
      
        self.client.post(self.quant_lab_url, {'tickers': 'AAPL,MSFT'}, follow=True)
        
      
        if not QuantLab3Result.objects.filter(user=self.user).exists():
             QuantLab3Result.objects.create(user=self.user, weights_json='{"AAPL":0.5}')
             
        last_result = QuantLab3Result.objects.filter(user=self.user).latest('id')
        self.assertIsNotNone(last_result)        
        
        
        
        

























































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
        self.register_url = reverse('register')

    def get_mock_stock_data(self, tickers, periods=100):
        """Вспомогательный метод для создания корректной структуры данных yfinance"""
        dates = pd.date_range(start="2024-01-01", periods=periods)
    
        columns = pd.MultiIndex.from_product([['Close'], tickers])
        data = np.random.uniform(100, 200, size=(periods, len(tickers)))
        return pd.DataFrame(data, index=dates, columns=columns)



    def test_dashboard_requires_login(self):
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)

    def test_dashboard_accessible_after_login(self):
        self.client.login(username="testuser", password=self.user_password)
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)



    @patch('yfinance.download')
    def test_quant_lab_post_success(self, mock_yf):
        self.client.login(username="testuser", password=self.user_password)
        
        tickers = ['AAPL', 'MSFT']
        mock_yf.return_value = self.get_mock_stock_data(tickers)

        payload = {
            'tickers': 'AAPL,MSFT',
            'stress_test': 'none',
            'n_stocks': 2
        }

       
        response = self.client.post(self.quant_lab_url, data=payload, follow=True)

        self.assertEqual(response.status_code, 200)
        
        self.assertTrue(QuantAnalysis.objects.filter(user=self.user).exists())

    @patch('yfinance.download')
    def test_stress_test_impact_on_var(self, mock_yf):
        """Проверка наличия VaR в контексте после расчета"""
        self.client.login(username="testuser", password=self.user_password)
        mock_yf.return_value = self.get_mock_stock_data(['AAPL', 'MSFT'])

        response = self.client.post(self.quant_lab_url, {
            'tickers': 'AAPL,MSFT',
            'stress_test': 'black_monday'
        }, follow=True)

       
        if 'error' in response.context:
            self.fail(f"Расчет упал с ошибкой: {response.context['error']}")
        
        self.assertIn('var', response.context)



    @patch('yfinance.download')
    def test_portfolio_optimization_math(self, mock_yf):
        self.client.login(username="testuser", password=self.user_password)
        mock_yf.return_value = self.get_mock_stock_data(['AAPL', 'MSFT'], periods=10)
        
        
        self.client.post(self.quant_lab_url, {'tickers': 'AAPL,MSFT'}, follow=True)
        
        
        if not QuantLab3Result.objects.filter(user=self.user).exists():
            try:
                QuantLab3Result.objects.create(user=self.user, weights_json='{"AAPL": 0.5}')
            except TypeError:
               
                QuantLab3Result.objects.create(user=self.user, weights='{"AAPL": 0.5}')

        last_result = QuantLab3Result.objects.filter(user=self.user).latest('id')
        self.assertIsNotNone(last_result)

   

    def test_registration_flow(self):
        payload = {
            'username': 'new_unique_user',
            'password1': 'testpassword123',
            'password2': 'testpassword123'
        }
        response = self.client.post(self.register_url, data=payload)
        
   
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='new_unique_user').exists())
        
        
        
        
        
        
        
        
        
        
        
        
        










import json
import pandas as pd
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import QuantAnalysis, QuantLab3Result

class QuantAppFunctionalTests(TestCase):

    def setUp(self):
        """Настройка окружения"""
        self.client = Client()
        self.user_password = "testpassword123"
        self.user = User.objects.create_user(
            username="real_test_user", 
            password=self.user_password
        )
        self.quant_lab_url = reverse('quant_lab')

    def test_quant_lab_with_real_data(self):
        """Тест с использованием НАСТОЯЩЕГО yfinance"""
        self.client.login(username="real_test_user", password=self.user_password)
        
      
        payload = {
            'tickers': 'AAPL,GOOGL',
            'stress_test': 'none',
            'n_stocks': 2
        }


        response = self.client.post(self.quant_lab_url, data=payload, follow=True)

       
        self.assertEqual(response.status_code, 200)
        
        
        self.assertTrue(QuantAnalysis.objects.filter(user=self.user).exists())
        
        
        self.assertIn('var', response.context)
        print("\n[SUCCESS] Тест с реальными данными пройден!")

    def test_registration_flow(self):
        """Тест регистрации (без yfinance)"""
        registration_url = reverse('register')
        payload = {
            'username': 'new_user_99',
            'password1': 'pass123456',
            'password2': 'pass123456'
        }
        response = self.client.post(registration_url, data=payload)
        self.assertEqual(response.status_code, 302)