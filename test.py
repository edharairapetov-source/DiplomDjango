from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from analysis.models import SimulationRecord

class QuantLabTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        
    def test_dashboard_requires_login(self):
        # Замените 'dashboard', если в urls.py имя другое
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302) # Редирект на логин

    def test_simulation_record_creation(self):
        record = SimulationRecord.objects.create(
            user=self.user,
            tickers="AAPL, TSLA",
            expected_return=0.15,
            risk=0.05,
            sharpe_ratio=3.0
        )
        self.assertEqual(record.user.username, 'testuser')
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
from django.test import TestCase
#from .your_module import run_analysis
#from analysis_code import run_analysis_clean
#from analysis.analysis_code import run_analysis_clean
#from analysis_code import run_analysis_clean as run_analysis
from analysis.analysis_code import run_analysis_clean as run_analysis
class AnalyticsIntegrationTest(TestCase):
    def test_full_analysis_flow(self):
        # 1. Подготовка данных
        params = {
            "tickers": ["AAPL", "MSFT"],
            "period": "1mo", # короткий период для скорости
            "corr_threshold": 0.5
        }
        
        # 2. Выполнение
        results = run_analysis(**params)
        
        # 3. Проверки (Assertions)
        self.assertIn('graph_url', results)
        self.assertEqual(len(results['weights']), 2)
        self.assertIsInstance(results['backtest_sharpe'], float)
        self.assertTrue(results['graph_url'].startswith('data:image/png;base64'))
        
    def test_eval_security(self):
        # Проверка защиты от инъекций в формулу
        params = {"formula_str": "__import__('os').remove('db.sqlite3')"}
        results = run_analysis(**params)
        # Ожидаем, что код не упал, а вернул fallback значение
        self.assertEqual(results['gnn_prediction']['pred_0'], 0.0)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class BISystemIntegrationTest(TestCase):
    def setUp(self):
        # Создаем тестового юзера для BI-системы
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client = Client()

    def test_full_dashboard_flow(self):
        """Проверка цепочки: Вход -> Дашборд -> Расчет"""
        # 1. Проверяем редирект анонима (Система безопасности)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)

        # 2. Логинимся
        self.client.login(username='testuser', password='password123')

        # 3. Проверяем доступ к Quant Lab (Системная навигация)
        # ВАЖНО: убедись, что 'quant_lab' или 'quant_lab7' есть в urls.py
        try:
            url = reverse('quant_lab7')
        except:
            url = reverse('quant_lab')
            
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # 4. Имитируем POST-запрос (Манипуляция данными)
        # Передаем параметры, которые ожидает твоя функция run_analysis_clean
        data = {
            'n_stocks': 5,
            'mu': 0.1,
            'sigma': 0.2,
            'tickers': 'AAPL,MSFT',
            'stress_test': 'none'
        }
        response = self.client.post(url, data)
        
        # Проверяем, что после расчета мы остались на странице и получили результаты
        self.assertEqual(response.status_code, 200)
        # Проверяем наличие ключей для визуализации в контексте
        self.assertIn('history', response.context)     



















from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from analysis.models import QuantAnalysis

class PortfolioSystemTest2(TestCase):
    def setUp(self):
        # 1. Создаем окружение: юзер и клиент
        self.user = User.objects.create_user(username='quant_boss', password='password123')
        self.client = Client()

    def test_full_analysis_cycle(self):
        """Системный тест: Логин -> Ввод данных -> Проверка БД -> Проверка Контекста"""
        
        # А. Проверка безопасности (редирект анонима)
        response = self.client.get(reverse('quant_lab'))
        self.assertEqual(response.status_code, 302)

        # Б. Авторизация
        self.client.login(username='quant_boss', password='password123')

        # В. Отправка данных для расчета (Имитация действий пользователя)
        payload = {
            'n_stocks': 15,
            'mu': 0.12,
            'sigma': 0.25,
            'tickers': 'AAPL,TSLA,BTC-USD'
        }
        response = self.client.post(reverse('quant_lab'), data=payload)

        # Г. Проверка результата (Системная интеграция)
        self.assertEqual(response.status_code, 200)
        
        # Проверяем, что запись реально появилась в Базе Данных
        self.assertTrue(QuantAnalysis.objects.filter(user=self.user, n_stocks=15).exists())
        
        # Проверяем, что данные для графиков ушли в шаблон
        self.assertIn('chart_json', response.context)
        self.assertContains(response, "0.12") # Проверка, что доходность отобразилась на странице
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from analysis.models import QuantAnalysis

class PortfolioSystemTest3(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='quant_user', password='password123')
        self.client = Client()

    def test_full_analysis_cycle(self):
        self.client.login(username='quant_user', password='password123')
        
        # Убедись, что 'quant_lab' — это name в твоем urls.py
        url = reverse('quant_lab') 
        
        # Данные, которые твоя функция quant_lab ожидает в request.POST
        payload = {
            'n_stocks': 15,
            'mu': 0.12,
            'sigma': 0.25,
            'tickers': 'AAPL,MSFT'
        }
        
        response = self.client.post(url, data=payload)
        
        # Если статус не 200, тест покажет ошибку
        self.assertEqual(response.status_code, 200, msg=f"Ошибка сервера: {response.content.decode()[:500]}")

        # ПРОВЕРКА СОХРАНЕНИЯ:
        # Если здесь падает, значит QuantAnalysis.objects.create(...) не сработал во views.py
        exists = QuantAnalysis.objects.filter(user=self.user, n_stocks=15).exists()
        self.assertTrue(exists, msg="Запись не была создана в базе данных! Проверь .create() во views.py")
        
        
        
    
    
    def test_bi_visualization_data(self):
        """Проверяем, что система отдает данные для Chart.js"""
        self.client.login(username='quant_user', password='password123')
        response = self.client.post(reverse('quant_lab'), {'n_stocks': 5, 'mu': 0.1, 'sigma': 0.2})
        
        # Проверяем наличие ключа, который мы используем для графиков
        self.assertIn('chart_json', response.context, msg="В контексте нет данных 'chart_json' для графиков!")
        
        
        
        
        
        
        
        
        
        
        
        
        
        
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from analysis.models import QuantAnalysis

class PortfolioSystemTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testadmin', password='123')
        self.client = Client()

    def test_full_analysis_cycle(self):
        """Системный тест: Вход -> Запрос к yfinance -> Сохранение в БД"""
        self.client.login(username='testadmin', password='123')
        
        # Отправляем 2 тикера. n_stocks в базе должен стать равным 2.
        payload = {
            'tickers': 'AAPL, MSFT',
            'stress_test': 'none'
        }
        
        response = self.client.post(reverse('quant_lab'), data=payload)
        
        # 1. Проверяем, что сервер не упал (код 200)
        self.assertEqual(response.status_code, 200)

        # 2. Проверяем, что в базе появилась запись именно для этого юзера
        # Мы ищем n_stocks=2, так как отправили 2 тикера
        exists = QuantAnalysis.objects.filter(user=self.user, n_stocks=2).exists()
        
        self.assertTrue(exists, msg="Запись не создана. Возможно, yfinance не скачал данные или ошибка в create()")

    def test_stress_scenario_logic(self):
        """Проверка, что стресс-тест влияет на сохраняемые данные"""
        self.client.login(username='testadmin', password='123')
        
        # Отправляем сценарий обвала
        self.client.post(reverse('quant_lab'), data={'tickers': 'AAPL', 'stress_test': 'crash'})
        
        last_analysis = QuantAnalysis.objects.filter(user=self.user).last()
        # Проверяем, что расчеты были проведены (объект существует)
        self.assertIsNotNone(last_analysis)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
     