from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class MlTradingViewTestCase(TestCase):

    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.url = reverse('python_console')  # Путь к твоей странице анализа

    def test_ml_trading_view_status_code(self):
        # Проверка, что страница доступна (200 OK)
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_ml_trading_view_template(self):
        # Проверка, что используется правильный шаблон
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'ml_trading.html')  # Убедись, что указываешь правильный путь

    def test_ml_trading_view_context(self):
        # Проверка наличия нужных данных в контексте
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.url)
        self.assertIn('results', response.context)  # Убедись, что данные действительно передаются в контекст
        self.assertIsInstance(response.context['results'], dict)  # Проверка типа данных в контексте

    def test_ml_trading_view_redirect_if_not_logged_in(self):
        # Проверка перенаправления для пользователей, не вошедших в систему
        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next=/ml-trading/')
