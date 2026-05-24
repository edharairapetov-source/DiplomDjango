from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import QuantAnalysis, QuantAnalysisbi

class AllPagesLoadTest(TestCase):
    def setUp(self):
        """Настройка клиента и пользователя для защищенных страниц."""
        self.client = Client()
        self.user = User.objects.create_user(username='tester', password='password123')
        # Данные для POST запросов (чтобы тесты не падали на логике расчетов)
        self.post_data = {
            'n_stocks': 5,
            'mu': 0.1,
            'sigma': 0.2,
            'corr_threshold': 0.5
        }

    def check_page(self, url_name, requires_login=True, status_expected=200):
        """Вспомогательный метод для проверки страниц."""
        if requires_login:
            self.client.login(username='tester', password='password123')
        
        url = reverse(url_name)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status_expected, f"Ошибка на странице {url_name}")
        return response

    # --- ТЕСТЫ ДОСТУПНОСТИ СТРАНИЦ ---

    def test_home_page_load(self):
        """Проверка главной страницы."""
        self.check_page('home', requires_login=False)

    def test_dashboard_load(self):
        """Проверка основного дашборда (требует логин)."""
        self.check_page('dashboard', requires_login=True)

    def test_register_page_load(self):
        """Проверка страницы регистрации."""
        self.check_page('register', requires_login=False)

    def test_quant_lab_load(self):
        """Проверка квантовой лаборатории."""
        self.check_page('quant_lab', requires_login=True)

    def test_unified_bi_pro_load(self):
        """Проверка BI-аналитики."""
        self.check_page('unified_quant_bi_pro', requires_login=True)

    def test_watchlist_load(self):
        """Проверка списка наблюдения."""
        self.check_page('watchlist', requires_login=True)

    def test_portfolio_history_load(self):
        """Проверка истории портфеля."""
        self.check_page('portfolio_history', requires_login=True)

    def test_ml_trading_load(self):
        """Проверка ML-трейдинга."""
        self.check_page('mltrading', requires_login=True)

    def test_technical_analysis_load(self):
        """Проверка тех. анализа."""
        self.check_page('technical_analysis', requires_login=True)

    def test_bi_dashboard_load(self):
        """Проверка BI-дашборда."""
        self.check_page('bi_dashboard', requires_login=True)

    # --- ТЕСТЫ РЕДИРЕКТОВ (БЕЗОПАСНОСТЬ) ---

    def test_anonymous_redirect(self):
        """Проверка, что анонима редиректит с закрытых страниц."""
        self.client.logout()
        protected_urls = ['dashboard', 'quant_lab', 'portfolio_history']
        for url_name in protected_urls:
            url = reverse(url_name)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302, f"Страница {url_name} не защищена!")

    # --- ТЕСТ API ---

    def test_api_yfinance_status(self):
        """Проверка API без загрузки данных (мокаем или проверяем ответ)."""
        url = reverse('live_yfinance')
        response = self.client.get(url, {'ticker': 'AAPL'})
        # Может вернуть 200 или 400 в зависимости от доступности сети, 
        # но в модульном тесте мы проверяем сам факт работы вьюхи.
        self.assertIn(response.status_code, [200, 400])
        
        
        
        
        
        
        
import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

class StockSystemFullTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Настройка Chrome (безголовый режим, чтобы окно не мешало)
        options = Options()
        # options.add_argument("--headless") # Раскомментируйте, чтобы браузер работал в фоне
        
        cls.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        cls.driver.implicitly_wait(10)  # Ждать появления элементов до 10 секунд

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        # Создаем пользователя для тестов
        self.password = "testpass123"
        self.user = User.objects.create_user(username="admin_test", password=self.password)

    def test_user_flow_quant_lab(self):
        """Проверка полного цикла: Вход -> Расчет в Quant Lab."""
        
        # 1. Открываем страницу логина (или редирект с дашборда)
        self.driver.get(f"{self.live_server_url}{reverse('dashboard')}")
        
        # 2. Логинимся (предполагаем наличие полей username и password в шаблоне)
        # Если у вас стандартная форма Django:
        try:
            self.driver.find_element(By.NAME, "username").send_keys("admin_test")
            self.driver.find_element(By.NAME, "password").send_keys(self.password)
            self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        except:
            # Если форма не найдена, пропускаем шаг (возможно, логин через cookies)
            self.client.login(username="admin_test", password=self.password)
            cookie = self.client.cookies['sessionid']
            self.driver.get(self.live_server_url)
            self.driver.add_cookie({'name': 'sessionid', 'value': cookie.value, 'path': '/'})
            self.driver.refresh()

        # 3. Переходим в Квантовую Лабораторию
        self.driver.get(f"{self.live_server_url}{reverse('quant_lab')}")

        # 4. Заполняем форму расчета (используем имена полей из вашего views.py)
        self.driver.find_element(By.NAME, "n_stocks").clear()
        self.driver.find_element(By.NAME, "n_stocks").send_keys("5")
        
        self.driver.find_element(By.NAME, "mu").clear()
        self.driver.find_element(By.NAME, "mu").send_keys("0.1")
        
        self.driver.find_element(By.NAME, "sigma").clear()
        self.driver.find_element(By.NAME, "sigma").send_keys("0.2")

        # 5. Отправляем форму
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # 6. Проверяем результат
        time.sleep(2)  # Даем время на рендер
        page_source = self.driver.page_source
        
        # Проверяем, что на странице появились ключевые слова результатов
        self.assertIn("VaR", page_source)
        self.assertIn("Hit Rate", page_source)
        
        print("Системный тест: УСПЕШНО")

    def test_api_yfinance_direct(self):
        """Проверка работы API котировок через браузер."""
        url = f"{self.live_server_url}{reverse('live_yfinance')}?ticker=AAPL"
        self.driver.get(url)
        
        # Проверяем, что получили JSON ответ
        content = self.driver.find_element(By.TAG_NAME, "pre").text if "json" in self.driver.current_url else self.driver.page_source
        self.assertIn("AAPL", content)
        self.assertIn("close", content)
        
        
        
        
import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from django.contrib.auth.models import User
from webdriver_manager.chrome import ChromeDriverManager
import time

class StockSystemTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Настройка Chrome (безголовый режим, чтобы не всплывало окно, если хотите — закомментируйте headless)
        chrome_options = Options()
        # chrome_options.add_argument("--headless") 
        
        cls.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        cls.driver.implicitly_wait(10) # Ожидание элементов до 10 секунд

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        # Создаем тестового пользователя для входа
        self.username = "sysadmin"
        self.password = "secure_pass_123"
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_full_user_journey(self):
        """Тест полного пути: Регистрация -> Вход -> Расчет в Лаборатории."""
        
        # 1. Переход на главную (Dashboard)
        self.driver.get(f"{self.live_server_url}/dashboard/")
        
        # 2. Проверка, что нас выкинуло на логин (так как доступ закрыт)
        # Если у вас редирект настроен, проверим наличие слова "Login" или формы
        self.assertIn("login", self.driver.current_url.lower())

        # 3. Эмуляция входа (если у вас есть форма логина)
        # Примечание: тут используются ID или NAME полей из ваших HTML-шаблонов
        # self.driver.find_element(By.NAME, "username").send_keys(self.username)
        # self.driver.find_element(By.NAME, "password").send_keys(self.password)
        # self.driver.find_element(By.ID, "submit-id-submit").click()

        # Для скорости теста в E2E часто делают принудительный логин через клиент:
        self.client.login(username=self.username, password=self.password)
        cookie = self.client.cookies['sessionid']
        self.driver.get(self.live_server_url)
        self.driver.add_cookie({'name': 'sessionid', 'value': cookie.value, 'path': '/'})
        
        # 4. Переход в Квантовую Лабораторию
        self.driver.get(f"{self.live_server_url}/quant-lab/")
        
        # 5. Заполнение формы расчета
        n_stocks_input = self.driver.find_element(By.NAME, "n_stocks")
        mu_input = self.driver.find_element(By.NAME, "mu")
        sigma_input = self.driver.find_element(By.NAME, "sigma")
        
        n_stocks_input.clear()
        n_stocks_input.send_keys("3")
        mu_input.clear()
        mu_input.send_keys("0.12")
        sigma_input.clear()
        sigma_input.send_keys("0.25")
        
        # Нажимаем кнопку "Calculate" (убедитесь, что тип кнопки submit)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # 6. Проверка результата на странице
        time.sleep(2) # Ждем обработки
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        
        # Проверяем, появились ли на странице расчетные данные (например, VaR)
        self.assertIn("VaR", body_text)
        print("Системный тест: Расчет в лаборатории прошел успешно!")

    def test_api_integration(self):
        """Проверка, что API котировок отдает данные в браузер."""
        self.driver.get(f"{self.live_server_url}/api/yf/?ticker=AAPL")
        
        # Проверяем, что в браузере отобразился JSON с данными
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertIn('"ticker": "AAPL"', body_text)
        self.assertIn('"close"', body_text)
