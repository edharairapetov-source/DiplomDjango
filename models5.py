from django.db import models
from django.contrib.auth.models import User


from django.db import models
import json



from django.db import models
import json

# Portfolio / Dashboard history
class AnalysisOutcome(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    tickers = models.TextField(default="[]")  # JSON list of tickers
    weights = models.TextField(default="[]")
    expected_return = models.FloatField(default=0.0)
    risk = models.FloatField(default=0.0)
    sharpe_ratio = models.FloatField(default=0.0)

    bs_sample = models.TextField(default="[]")
    bs_mean = models.FloatField(default=0.0)
    bs_std = models.FloatField(default=0.0)

    jd_sample = models.TextField(default="[]")
    jd_mean = models.FloatField(default=0.0)
    jd_std = models.FloatField(default=0.0)

    gnn_prediction = models.TextField(default="[]")
    backtest_equity_curve = models.TextField(default="[]")
    backtest_final_value = models.FloatField(default=0.0)
    backtest_sharpe = models.FloatField(default=0.0)
    backtest_drawdown = models.FloatField(default=0.0)

    def get_tickers(self):
        return json.loads(self.tickers)

    def get_weights(self):
        return json.loads(self.weights)

    def get_bs_sample(self):
        return json.loads(self.bs_sample)

    def get_jd_sample(self):
        return json.loads(self.jd_sample)

    def get_equity_curve(self):
        return json.loads(self.backtest_equity_curve)

    def get_gnn_prediction(self):
        return json.loads(self.gnn_prediction)


# Watchlist
class WatchlistItem(models.Model):
    ticker = models.CharField(max_length=10, unique=True)
    added_at = models.DateTimeField(auto_now_add=True)


# Alerts
class Alert(models.Model):
    ticker = models.CharField(max_length=10)
    threshold = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    triggered = models.BooleanField(default=False)

class AnalysisOutcome2(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)

    graph_url = models.TextField()
    weights = models.TextField()
    expected_return = models.FloatField()
    risk = models.FloatField()

    bs_sample = models.TextField()
    bs_mean = models.FloatField()
    bs_std = models.FloatField()

    jd_sample = models.TextField()
    jd_mean = models.FloatField()
    jd_std = models.FloatField()

    gnn_prediction = models.TextField()
    
    backtest_equity_curve = models.TextField(default="[]")  # Default empty list as a string
    backtest_final_value = models.FloatField(default=0.0)  # Default value of 0.0
    backtest_sharpe = models.FloatField(default=0.0)  # Default value of 0.0
    backtest_drawdown = models.FloatField(default=0.0)  # Default value of 0.0
    def get_weights(self):
        return json.loads(self.weights)

    def get_bs_sample(self):
        return json.loads(self.bs_sample)

    def get_jd_sample(self):
        return json.loads(self.jd_sample)

    def get_equity_curve(self):
        return json.loads(self.backtest_equity_curve)

    def get_gnn_prediction(self):
        return json.loads(self.gnn_prediction)








from django.db import models
from django.contrib.auth.models import User

class WatchlistAlert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticker = models.CharField(max_length=10)
    threshold_percent = models.FloatField(default=0.0)  # alert threshold as %
    last_price = models.FloatField(null=True, blank=True)
    triggered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ticker} @ {self.threshold_percent}%"





























from django.db import models

class SimulationRecord(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    final_value = models.FloatField()
    sharpe_ratio = models.FloatField()
    # You can also store the weights as JSON if needed
    # weights = models.JSONField() 

    class Meta:
        ordering = ['-timestamp']












class PortfolioAnalysis(models.Model):
#class AnalysisOutcome(models.Model):
    """Объединенная модель для всех результатов анализа"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analyses')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Используем JSONField вместо TextField + json.loads
    tickers = models.JSONField(default=list)
    weights = models.JSONField(default=dict)
    
    # Основные метрики
    expected_return = models.FloatField(default=0.0)
    risk = models.FloatField(default=0.0)
    sharpe_ratio = models.FloatField(default=0.0)

    # Данные симуляций (тоже в JSON для гибкости)
    simulation_data = models.JSONField(default=dict) 
    # Сюда можно упаковать bs_sample, jd_sample и gnn_prediction
    
    backtest_data = models.JSONField(default=dict)
    # Сюда: equity_curve, final_value, drawdown
    
    
    

    
    
    
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Анализ портфеля"

class WatchlistItem(models.Model):
    """Теперь у каждого пользователя свой список наблюдения"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticker = models.CharField(max_length=10)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'ticker') # Нельзя добавить один тикер дважды одному юзеру