from django.db import models
from django.contrib.auth.models import User

class Alert(models.Model):
    ticker = models.CharField(max_length=10)
    threshold = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    triggered = models.BooleanField(default=False)


class AnalysisOutcome(models.Model):
    

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analyses')
    timestamp = models.DateTimeField(auto_now_add=True)


    tickers = models.JSONField(default=list)
    weights = models.JSONField(default=dict)

  
    expected_return = models.FloatField(default=0.0)
    risk = models.FloatField(default=0.0)
    sharpe_ratio = models.FloatField(default=0.0)

    # Симуляции
    simulation_data = models.JSONField(default=dict)
    backtest_data = models.JSONField(default=dict)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Анализ портфеля"

    def __str__(self):
        return f"{self.user.username} - {self.timestamp}"


class WatchlistItem(models.Model):
    

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticker = models.CharField(max_length=10)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'ticker')

    def __str__(self):
        return f"{self.user.username} - {self.ticker}"


class WatchlistAlert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticker = models.CharField(max_length=10)
    threshold_percent = models.FloatField(default=0.0)
    last_price = models.FloatField(null=True, blank=True)
    triggered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ticker} @ {self.threshold_percent}%"


class SimulationRecord2(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    final_value = models.FloatField()
    sharpe_ratio = models.FloatField()

    class Meta:
        ordering = ['-timestamp']
        
        
        
        
        
        
        
        
        

from django.db import models
from django.contrib.auth.models import User

class Simulation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    timestamp = models.DateTimeField(auto_now_add=True)
    tickers = models.TextField()  
    expected_return = models.FloatField()
    risk = models.FloatField()
    sharpe_ratio = models.FloatField()

    def __str__(self):
        return f"{self.user.username} - {self.timestamp}"
    
    
    
    
    
    
    
from django.db import models
from django.contrib.auth.models import User

class SimulationRecord(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
   
    tickers = models.TextField()
    expected_return = models.FloatField()
    risk = models.FloatField()
    sharpe_ratio = models.FloatField()

    def __str__(self):
        return f"Sim {self.timestamp} - {self.user.username}"
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

from django.db import models
from django.contrib.auth.models import User

class QuantAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

   
    n_stocks = models.IntegerField()
    mu = models.FloatField()
    sigma = models.FloatField()

    
    var_value = models.FloatField()
    cvar_value = models.FloatField()
    hit_rate = models.FloatField()
    
   
    frontier_img = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp'] 
        
        
        
        



from django.db import models
from django.contrib.auth.models import User
class QuantAnalysisbi(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    power_bi_metrics = models.FloatField(null=True, blank=True)
    
    n_stocks = models.IntegerField()
    mu = models.FloatField()
    sigma = models.FloatField()



    @property
    def elastic_status(self):
        """Эластичное поле: меняет статус в зависимости от доходности"""
        if self.mu > 15:
            return " High Yield"
        elif self.mu > 0:
            return " Stable"
        return " Risk"

    @property
    def risk_score(self):
        """Динамический расчет соотношения риск/доходность"""
        if self.var_value == 0: return 0
        return round(self.mu / self.var_value, 2)
    
    var_value = models.FloatField(null=True, blank=True)
    cvar_value = models.FloatField(null=True, blank=True)
    hit_rate = models.FloatField(null=True, blank=True)
    
    frontier_img = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
class QuantAnalysisbi2(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    cvar_value = models.FloatField(null=True, blank=True)
    
    hit_rate = models.FloatField(null=True, blank=True) 
    cvar_value = models.FloatField(null=True, blank=True)
    
    n_stocks = models.IntegerField()
    mu = models.FloatField()
    sigma = models.FloatField()

   
    var_value = models.FloatField()
    cvar_value = models.FloatField()
    hit_rate = models.FloatField()
    
    
    frontier_img = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp'] 
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
from django.db import models


from django.db import models

from django.db import models

class AnalysisResult(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    analysis_start_date = models.DateField(null=True, blank=True)
    analysis_end_date = models.DateField(null=True, blank=True)

    
    expected_return = models.FloatField(default=0.0)
    risk = models.FloatField(default=0.0)
    alpha_analysis = models.JSONField(default=dict)
    ml_alpha_analysis = models.JSONField(default=dict)

   
    bs_mean = models.FloatField(default=0.0)
    bs_std = models.FloatField(default=0.0)
    jd_mean = models.FloatField(default=0.0)
    jd_std = models.FloatField(default=0.0)

    
    backtest_final_value = models.FloatField(default=0.0)
    backtest_sharpe = models.FloatField(default=0.0)
    backtest_drawdown = models.FloatField(default=0.0)

    
    weights = models.JSONField(default=dict)
    gnn_prediction = models.JSONField(default=dict)

    class Meta:
        ordering = ['-created_at']

class AnalysisResultважно2(models.Model):
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего обновления")

    
    analysis_start_date = models.DateField(null=True, blank=True, verbose_name="Начало периода анализа")
    analysis_end_date = models.DateField(null=True, blank=True, verbose_name="Конец периода анализа")

    
    expected_return = models.FloatField()
    risk = models.FloatField()

    
    bs_mean = models.FloatField()
    bs_std = models.FloatField()
    jd_mean = models.FloatField()
    jd_std = models.FloatField()

    
    backtest_final_value = models.FloatField()
    backtest_sharpe = models.FloatField()
    backtest_drawdown = models.FloatField()

   
    weights = models.JSONField()
    gnn_prediction = models.JSONField()
    alpha_analysis = models.JSONField()
    ml_alpha_analysis = models.JSONField()

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Результат анализа"
        verbose_name_plural = "Результаты анализа"

    def __str__(self):
        
        period = f"{self.analysis_start_date} -> {self.analysis_end_date}" if self.analysis_start_date else "No period"
        return f"Analysis {self.id} | {period} (Created: {self.created_at.strftime('%Y-%m-%d %H:%M')})"

class AnalysisResultшьзщкефте(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)

    expected_return = models.FloatField()

    risk = models.FloatField()

    bs_mean = models.FloatField()

    bs_std = models.FloatField()

    jd_mean = models.FloatField()

    jd_std = models.FloatField()

    backtest_final_value = models.FloatField()

    backtest_sharpe = models.FloatField()

    backtest_drawdown = models.FloatField()

    weights = models.JSONField()

    gnn_prediction = models.JSONField()

    alpha_analysis = models.JSONField()

    ml_alpha_analysis = models.JSONField()

    def __str__(self):
        return f"Analysis {self.id} ({self.created_at})"
    
    
    
from django.db import models
from django.conf import settings

class AnalysisResult2(models.Model):
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='analysis_results',
        verbose_name="Пользователь"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    expected_return = models.FloatField()
    risk = models.FloatField()
    
    
    bs_mean = models.FloatField()
    bs_std = models.FloatField()
    jd_mean = models.FloatField()
    jd_std = models.FloatField()
    
    
    backtest_final_value = models.FloatField()
    backtest_sharpe = models.FloatField()
    backtest_drawdown = models.FloatField()
    
    
    weights = models.JSONField()
    gnn_prediction = models.JSONField()
    alpha_analysis = models.JSONField()
    ml_alpha_analysis = models.JSONField()

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Результат анализа"
        verbose_name_plural = "Результаты анализов"

    def __str__(self):
        return f"Analysis {self.id} for {self.user.username} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
from django.db import models


class AnalysisArchive(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)

    expected_return = models.FloatField()

    risk = models.FloatField()

    bs_mean = models.FloatField()

    bs_std = models.FloatField()

    jd_mean = models.FloatField()

    jd_std = models.FloatField()

    backtest_final_value = models.FloatField()

    backtest_sharpe = models.FloatField()

    backtest_drawdown = models.FloatField()

    weights = models.JSONField()

    gnn_prediction = models.JSONField()

    alpha_analysis = models.JSONField()

    ml_alpha_analysis = models.JSONField()

    def __str__(self):
        return f"Analysis {self.id} ({self.created_at})"
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
from django.db import models
from django.contrib.auth.models import User

class BIDashboardReport(models.Model):
    #user = models.ForeignKey(User, on_valid=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
   
    total_simulations = models.IntegerField()
    avg_return = models.FloatField()
    avg_risk_var = models.FloatField()
    market_comparison = models.FloatField() # Alpha (разница с S&P 500)
    
    
    chart_data_json = models.JSONField() 
    
    
    active_fvg_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Report {self.timestamp.strftime('%Y-%m-%d')} for {self.user.username}"
    






























from django.db import models
from django.contrib.auth.models import User

class QuantLab3Result(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Дата запуска")
    
   
    tickers = models.TextField(verbose_name="Тикеры (через запятую)")
    n_stocks = models.IntegerField(default=0)
    corr_threshold = models.FloatField(default=0.6)
    
   
    expected_return = models.FloatField(null=True, blank=True)
    risk = models.FloatField(null=True, blank=True)
    sharpe_ratio = models.FloatField(null=True, blank=True)
    
    
    raw_results = models.JSONField(null=True, blank=True, verbose_name="Полные данные (JSON)")

    def __str__(self):
        return f"Lab 3 - {self.user.username} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name = "Результат Квант Лаб 3"
        verbose_name_plural = "Результаты Квант Лаб 3"








































































from django.db import models

class Company(models.Model):
    """Информация о компании"""
    ticker = models.CharField(max_length=10, unique=True, verbose_name="Тикер")
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Название")
    sector = models.CharField(max_length=100, blank=True, null=True, verbose_name="Сектор")
    
    class Meta:
        verbose_name = "Компания"
        verbose_name_plural = "Компании"

    def __str__(self):
        return self.ticker

class GNNPrediction(models.Model):
    """История прогнозов нейросети"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='predictions')
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата прогноза")
    
    
    current_mu = models.FloatField(verbose_name="Текущая доходность (Mu)")
    current_sigma = models.FloatField(verbose_name="Текущая волатильность")
    
    
    predicted_return = models.FloatField(verbose_name="Прогноз GNN")
    
   
    confidence_score = models.FloatField(default=1.0)

    class Meta:
        ordering = ['-date']
        verbose_name = "Прогноз GNN"
        verbose_name_plural = "Прогнозы GNN"

    def __str__(self):
        return f"{self.company.ticker} - {self.date.strftime('%Y-%m-%d')}"
from django.db import models

class StockTicker(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    last_price = models.FloatField()
    prediction = models.FloatField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.symbol
    
    
    
    
    
from django.db import models
from django.contrib.auth.models import User

class GNNAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    tickers_input = models.TextField()  
    formula = models.CharField(max_length=100)
  
    results_json = models.JSONField() 

    def __str__(self):
        return f"Analysis by {self.user.username} - {self.date.strftime('%Y-%m-%d %H:%M')}"
    
    
    
    
    
    
    
    
    
    
    

    
    
    
    
    
from django.db import migrations, models
from django.contrib.auth.models import User

class TradeAnalysisRecord(models.Model):
   
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

   
    tickers = models.CharField(max_length=255) 
    capital = models.FloatField(default=10000.0)
    risk_pct = models.FloatField(default=1.0)

   
    win_rate = models.FloatField()
    profit_factor = models.FloatField()
    sharpe_ratio = models.FloatField()
    max_drawdown = models.FloatField()
    
  
    risk_based_size = models.FloatField()
    atr_based_size = models.FloatField()

    class Meta:
        ordering = ['-timestamp'] 

    def __str__(self):
        return f"{self.tickers} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
