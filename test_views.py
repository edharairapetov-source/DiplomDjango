from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class MlTradingViewTestCase(TestCase):

    def setUp(self):
        
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.url = reverse('python_console')  

    def test_ml_trading_view_status_code(self):
       
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_ml_trading_view_template(self):
      
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'ml_trading.html') 

    def test_ml_trading_view_context(self):
       
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.url)
        self.assertIn('results', response.context) 
        self.assertIsInstance(response.context['results'], dict)  

    def test_ml_trading_view_redirect_if_not_logged_in(self):
      
        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next=/ml-trading/')
