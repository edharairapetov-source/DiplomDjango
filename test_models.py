



from django.test import TestCase
from django.contrib.auth.models import User
from analysis.models import QuantAnalysis

class QuantAnalysisModelTestCase(TestCase):
    def setUp(self):
        
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.analysis = QuantAnalysis.objects.create(
            user=self.user,
            n_stocks=5,
            mu=0.15,
            sigma=0.05,
            var_value=0.02,
            cvar_value=0.04,
            hit_rate=0.75
        )

    def test_quant_analysis_creation(self):
       
        self.assertEqual(self.analysis.n_stocks, 5)
        self.assertEqual(self.analysis.mu, 0.15)
        self.assertEqual(self.user.username, 'testuser')

    def test_ordering(self):
        
        import time
       
        QuantAnalysis.objects.create(user=self.user, n_stocks=1, mu=0, sigma=0, var_value=0, cvar_value=0, hit_rate=0)
        time.sleep(0.01) 
        
        # Создаем вторую запись
        new_analysis = QuantAnalysis.objects.create(user=self.user, n_stocks=5, mu=0, sigma=0, var_value=0, cvar_value=0, hit_rate=0)
        
        latest = QuantAnalysis.objects.first()
        self.assertEqual(latest.id, new_analysis.id)
