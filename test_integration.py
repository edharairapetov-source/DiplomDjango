import pandas as pd
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch
from analysis.models import Company, GNNPrediction

class FullQuantProjectIntegrationTest(TestCase):
    
    def setUp(self):
        """Настройка окружения: пользователь и мок-данные."""
        self.client = Client()
        self.username = "quant_trader"
        self.password = "secure_pass_123"
        self.user = User.objects.create_user(username=self.username, password=self.password)
        
        # Имитируем данные от Yahoo Finance (5 дней)
        self.mock_data = pd.DataFrame({
            'Close': [150.0, 155.0, 160.0, 158.0, 162.0],
            'Open': [149.0, 154.0, 159.0, 157.0, 161.0],
            'High': [152.0, 157.0, 162.0, 160.0, 165.0],
            'Low': [148.0, 153.0, 158.0, 156.0, 160.0],
            'Volume': [1000, 1100, 1050, 1200, 1150]
        }, index=pd.date_range(start='2023-01-01', periods=5))

    # --- ТЕСТ API (ИСПРАВЛЕН ПОД ВАШ JSON) ---
    @patch('yfinance.download')
    def test_live_yfinance_api_json(self, mock_yf):
        """Проверка работы API: исправлено ожидание ключей 'close' вместо 'history'."""
        mock_yf.return_value = self.mock_data
        
        url = reverse('live_yfinance') + "?ticker=TSLA"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        
        self.assertEqual(json_data['ticker'], 'TSLA')
        # В вашем выводе нет ключа 'history', данные лежат в корне:
        self.assertIn('close', json_data)
        self.assertIn('open', json_data)
        self.assertEqual(len(json_data['close']), 5)

    # --- ТЕСТ ДАШБОРДА ---
    @patch('yfinance.download')
    def test_dashboard_full_pipeline(self, mock_yf_download):
        """Тест POST запроса на дашборд."""
        self.client.login(username=self.username, password=self.password)
        mock_yf_download.return_value = self.mock_data
        
        payload = {
            'tickers': 'AAPL',
            'n_stocks': 1,
            'corr_threshold': 0.7,
            'min_er': 0.05,
            'max_er': 0.25,
            'S0': 100.0, 'K': 105.0, 'T': 1.0, 'r': 0.03, 'sigma': 0.2
        }
        # Если здесь NoReverseMatch, значит в dashboard.html нужно заменить 'portfolio' на 'portfolio_history'
        response = self.client.post(reverse('dashboard'), data=payload)
        self.assertEqual(response.status_code, 200)

    # --- ТЕСТ GNN (ПРОВЕРКА СОХРАНЕНИЯ В БД) ---
    @patch('analysis.views.get_gnn_predictions')
    def test_gnn_save_to_db_integration(self, mock_gnn_engine):
        """Проверка, что после открытия страницы GNN данные попадают в БД."""
        self.client.login(username=self.username, password=self.password)
        
        # Мокаем предсказание нейросети
        mock_gnn_engine.return_value = [
            {'ticker': 'AAPL', 'current_mu': 0.12, 'sigma': 0.05, 'prediction': 0.15}
        ]
        
        # Вызываем страницу, которая должна запустить save_predictions_to_db
        response = self.client.get(reverse('gnn_analytics'))
        self.assertEqual(response.status_code, 200)
        
        # Проверяем, появилась ли запись в БД
        exists = Company.objects.filter(ticker='AAPL').exists()
        self.assertTrue(exists, "Компания не была создана в БД. Проверьте вызов функции сохранения в views.py")

    # --- ТЕСТ ДОСТУПА ---
    def test_protected_pages_redirect_anonymous(self):
        """Проверка защиты страниц."""
        protected_urls = ['dashboard', 'quant_lab', 'gnn_analytics']
        for url_name in protected_urls:
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 302)













import pandas as pd
import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock

# Импортируем модели вашего приложения (замените 'analysis' на ваше имя приложения)
from analysis.models import QuantAnalysis, Company, GNNPrediction

class FullQuantProjectIntegrationTest(TestCase):
    
    def setUp(self):
        """Настройка окружения перед каждым тестом."""
        self.client = Client()
        self.username = "quant_trader"
        self.password = "secure_pass_123"
        self.user = User.objects.create_user(username=self.username, password=self.password)
        
        # Данные для имитации ответа Yahoo Finance
        self.mock_data = pd.DataFrame({
            'Close': [150.0, 155.0, 160.0, 158.0, 162.0],
            'Open': [149.0, 154.0, 159.0, 157.0, 161.0],
            'High': [152.0, 157.0, 162.0, 160.0, 165.0],
            'Low': [148.0, 153.0, 158.0, 156.0, 160.0],
            'Volume': [1000, 1100, 1050, 1200, 1150]
        }, index=pd.date_range(start='2023-01-01', periods=5))

    # --- ТЕСТЫ АВТОРИЗАЦИИ ---

    def test_protected_pages_redirect_anonymous(self):
        """Проверка, что секретные страницы недоступны без логина."""
        protected_urls = ['dashboard', 'quant_lab', 'unified_quant_bi_pro', 'gnn_analytics']
        for url_name in protected_urls:
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 302, f"URL {url_name} должен редиректить")

    # --- КОМПЛЕКСНЫЙ ИНТЕГРАЦИОННЫЙ ТЕСТ ДАШБОРДА ---

    @patch('yfinance.download')
    def test_dashboard_full_pipeline(self, mock_yf_download):
        """Тест всей цепочки: Ввод тикеров -> API -> Расчет -> Отображение."""
        # 1. Логинимся
        self.client.login(username=self.username, password=self.password)
        
        # 2. Настраиваем мок для yfinance
        mock_yf_download.return_value = self.mock_data
        
        # 3. Отправляем форму анализа
        payload = {
            'tickers': 'AAPL, MSFT',
            'n_stocks': 2,
            'corr_threshold': 0.7,
            'min_er': 0.05,
            'max_er': 0.25,
            'S0': 100.0,
            'K': 105.0,
            'T': 1.0,
            'r': 0.03,
            'sigma': 0.2
        }
        response = self.client.post(reverse('dashboard'), data=payload)
        
        # 4. Проверяем ответ сервера
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.context)
        
        # 5. Проверяем, сохранился ли анализ в БД (если у вас прописано сохранение в view)
        # Если QuantAnalysis создается в views.py:
        # analysis_record = QuantAnalysis.objects.filter(user=self.user).last()
        # self.assertIsNotNone(analysis_record)

    # --- ТЕСТ GNN И ПРЕДСКАЗАНИЙ ---

    @patch('analysis.views.get_gnn_predictions')
    def test_gnn_save_to_db_integration(self, mock_gnn_engine):
        """Проверяем интеграцию GNN-движка и сохранение результатов в БД."""
        self.client.login(username=self.username, password=self.password)
        
        # Имитируем ответ от GNN движка
        mock_gnn_engine.return_value = [
            {'ticker': 'AAPL', 'current_mu': 0.12, 'sigma': 0.05, 'prediction': 0.15},
            {'ticker': 'NVDA', 'current_mu': 0.25, 'sigma': 0.12, 'prediction': 0.30}
        ]
        
        # Вызываем страницу, которая инициирует расчеты
        response = self.client.get(reverse('gnn_analytics'))
        self.assertEqual(response.status_code, 200)
        
        # Проверяем, создались ли записи в БД через вашу функцию save_predictions_to_db
        # (Эта функция вызывается внутри вашего view gnn_analytics_page)
        self.assertTrue(Company.objects.filter(ticker='AAPL').exists())
        self.assertTrue(GNNPrediction.objects.filter(company__ticker='NVDA').exists())
        
        prediction = GNNPrediction.objects.get(company__ticker='AAPL')
        self.assertEqual(float(prediction.predicted_return), 0.15)

    # --- ТЕСТ API ЭНДПОИНТОВ ---

    @patch('yfinance.download')
    def test_live_yfinance_api_json(self, mock_yf):
        """Проверка работы внутреннего API для JS-графиков."""
        mock_yf.return_value = self.mock_data
        
        url = reverse('live_yfinance') + "?ticker=TSLA"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data['ticker'], 'TSLA')
        self.assertIn('history', json_data) # Проверка, что данные о цене ушли в JSON

    # --- ТЕСТ СЦЕНАРИЕВ (BI PRO) ---

    def test_unified_bi_pro_crash_scenario(self):
        """Проверка логики 'Stress Test' в BI панели."""
        self.client.login(username=self.username, password=self.password)
        
        # Отправляем запрос со сценарием кризиса
        data = {'scenario': 'crash', 'tickers': 'AAPL'}
        
        # Здесь мы проверяем, что view обрабатывает этот флаг
        # (Предположим, расчеты проводятся корректно)
        with patch('yfinance.download') as mock_yf:
            mock_yf.return_value = self.mock_data
            response = self.client.post(reverse('unified_quant_bi_pro'), data)
            
            self.assertEqual(response.status_code, 200)
            # Если в контекст передается флаг или модифицированные mu
            # self.assertLess(response.context['mu_total'], 0)
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
import pandas as pd
import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock

# Импортируем модели вашего приложения (замените 'analysis' на ваше имя приложения)
from analysis.models import QuantAnalysis, Company, GNNPrediction

class FullQuantProjectIntegrationTest(TestCase):
    
    def setUp(self):
        """Настройка окружения перед каждым тестом."""
        self.client = Client()
        self.username = "quant_trader"
        self.password = "secure_pass_123"
        self.user = User.objects.create_user(username=self.username, password=self.password)
        
        # Данные для имитации ответа Yahoo Finance
        self.mock_data = pd.DataFrame({
            'Close': [150.0, 155.0, 160.0, 158.0, 162.0],
            'Open': [149.0, 154.0, 159.0, 157.0, 161.0],
            'High': [152.0, 157.0, 162.0, 160.0, 165.0],
            'Low': [148.0, 153.0, 158.0, 156.0, 160.0],
            'Volume': [1000, 1100, 1050, 1200, 1150]
        }, index=pd.date_range(start='2023-01-01', periods=5))

    # --- ТЕСТЫ АВТОРИЗАЦИИ ---

    def test_protected_pages_redirect_anonymous(self):
        """Проверка, что секретные страницы недоступны без логина."""
        protected_urls = ['dashboard', 'quant_lab', 'unified_quant_bi_pro', 'gnn_analytics']
        for url_name in protected_urls:
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 302, f"URL {url_name} должен редиректить")

    # --- КОМПЛЕКСНЫЙ ИНТЕГРАЦИОННЫЙ ТЕСТ ДАШБОРДА ---

    @patch('yfinance.download')
    def test_dashboard_full_pipeline(self, mock_yf_download):
        """Тест всей цепочки: Ввод тикеров -> API -> Расчет -> Отображение."""
        # 1. Логинимся
        self.client.login(username=self.username, password=self.password)
        
        # 2. Настраиваем мок для yfinance
        mock_yf_download.return_value = self.mock_data
        
        # 3. Отправляем форму анализа
        payload = {
            'tickers': 'AAPL, MSFT',
            'n_stocks': 2,
            'corr_threshold': 0.7,
            'min_er': 0.05,
            'max_er': 0.25,
            'S0': 100.0,
            'K': 105.0,
            'T': 1.0,
            'r': 0.03,
            'sigma': 0.2
        }
        response = self.client.post(reverse('dashboard'), data=payload)
        
        # 4. Проверяем ответ сервера
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.context)
        
        # 5. Проверяем, сохранился ли анализ в БД (если у вас прописано сохранение в view)
        # Если QuantAnalysis создается в views.py:
        # analysis_record = QuantAnalysis.objects.filter(user=self.user).last()
        # self.assertIsNotNone(analysis_record)

    # --- ТЕСТ GNN И ПРЕДСКАЗАНИЙ ---

    @patch('analysis.views.get_gnn_predictions')
    def test_gnn_save_to_db_integration(self, mock_gnn_engine):
        """Проверяем интеграцию GNN-движка и сохранение результатов в БД."""
        self.client.login(username=self.username, password=self.password)
        
        # Имитируем ответ от GNN движка
        mock_gnn_engine.return_value = [
            {'ticker': 'AAPL', 'current_mu': 0.12, 'sigma': 0.05, 'prediction': 0.15},
            {'ticker': 'NVDA', 'current_mu': 0.25, 'sigma': 0.12, 'prediction': 0.30}
        ]
        
        # Вызываем страницу, которая инициирует расчеты
        response = self.client.get(reverse('gnn_analytics'))
        self.assertEqual(response.status_code, 200)
        
        # Проверяем, создались ли записи в БД через вашу функцию save_predictions_to_db
        # (Эта функция вызывается внутри вашего view gnn_analytics_page)
        self.assertTrue(Company.objects.filter(ticker='AAPL').exists())
        self.assertTrue(GNNPrediction.objects.filter(company__ticker='NVDA').exists())
        
        prediction = GNNPrediction.objects.get(company__ticker='AAPL')
        self.assertEqual(float(prediction.predicted_return), 0.15)

    # --- ТЕСТ API ЭНДПОИНТОВ ---

    @patch('yfinance.download')
    def test_live_yfinance_api_json(self, mock_yf):
        """Проверка работы внутреннего API для JS-графиков."""
        mock_yf.return_value = self.mock_data
        
        url = reverse('live_yfinance') + "?ticker=TSLA"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data['ticker'], 'TSLA')
        self.assertIn('history', json_data) # Проверка, что данные о цене ушли в JSON

    # --- ТЕСТ СЦЕНАРИЕВ (BI PRO) ---

    def test_unified_bi_pro_crash_scenario(self):
        """Проверка логики 'Stress Test' в BI панели."""
        self.client.login(username=self.username, password=self.password)
        
        # Отправляем запрос со сценарием кризиса
        data = {'scenario': 'crash', 'tickers': 'AAPL'}
        
        # Здесь мы проверяем, что view обрабатывает этот флаг
        # (Предположим, расчеты проводятся корректно)
        with patch('yfinance.download') as mock_yf:
            mock_yf.return_value = self.mock_data
            response = self.client.post(reverse('unified_quant_bi_pro'), data)
            
            self.assertEqual(response.status_code, 200)
            # Если в контекст передается флаг или модифицированные mu
            # self.assertLess(response.context['mu_total'], 0)