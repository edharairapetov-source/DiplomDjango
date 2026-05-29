
from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.contrib.auth.models import User

class DashboardUITest(StaticLiveServerTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='password123')
        self.browser = webdriver.Chrome() 

    def tearDown(self):
        self.browser.quit()

    def test_login_and_calculate(self):
        
        self.browser.get(self.live_server_url + reverse('login'))
        
       
        username_input = self.browser.find_element("name", "username")
        password_input = self.browser.find_element("name", "password")
        username_input.send_keys("admin")
        password_input.send_keys("password123")
        self.browser.find_element("xpath", "//button[@type='submit']").click()

        
        self.browser.get(self.live_server_url + reverse('quant_lab'))

        
        tickers_input = self.browser.find_element("name", "tickers")
        tickers_input.clear()
        tickers_input.send_keys("TSLA, NVDA")
        
        self.browser.find_element("xpath", "//button[contains(text(), 'Calculate')]").click()

       
        assert "TSLA" in self.browser.page_source
       
        canvas = self.browser.find_element("tag name", "canvas")
        assert canvas.is_displayed()
