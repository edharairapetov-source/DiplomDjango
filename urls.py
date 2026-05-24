# analysis/urls.py
from django.urls import path
from . import views
# urls.py
#from . import views as analysis_views
from .views import ml_trading_view

from .views import quant_lab3, register, dashboard_bi_view
from django.urls import path
from .views import dashboard, live_yfinance, quant_lab

from django.urls import path

from .views import analysis_list_view

from .views import get_analytics_dashboard

urlpatterns = [
    path('', views.main_index, name='home'),
    
    #path('gnn-analytics/', gnn_analytics_page, name='gnn_analytics'),
    path('analysis/gnn-analytics/', views.gnn_analytics_page, name='gnn_analytics'),
    
    path("", dashboard, name="dashboard"),
    path("api/yf/", live_yfinance, name="live_yfinance"),
    
    path("quant-lab/", quant_lab, name="quant_lab"),
    
    path("python-console/", views.python_console, name="python_console"),
    path("no-code/", views.no_code_console, name="no_code_console"),
    path("unified_quant_bi_pro/", views.unified_quant_bi_pro, name="unified_quant_bi_pro"),
    path("watchlist/", views.watchlist, name="watchlist"),
    
    
    path('', views.dashboard25, name='dashboard'),  # Home / dashboard
    path('watchlist/', views.watchlist, name='watchlist'),
    path('monte_carlo/', views.monte_carlo, name='monte_carlo'),
    #path('portfolio/', views.portfolio, name='portfolio'),
    path('alerts/', views.alerts, name='alerts'),
    #path('live_data/', views.live_yfinance, name='live_data'),
    #path('python_console/', views.python_console, name='python_console'),
    path('dashboard/', views.dashboard, name='dashboard'),




    path('trade-input/', views.trade_analytics_page, name='trade_input'),
    path('trade-results/', views.trade_analytics_page, name='trade_results'),
    path('trends/', views.trade_trends_page, name='trade_trends'),
    #path('dashboard/', analysis_views.dashboard, name='dashboard'),

    path('', views.dashboard, name='home'),  # Главная страница по адресу /

    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='logout'),
    
    path('register/', views.register, name='register'),
    
    path("ml-trading/", ml_trading_view, name="mltrading"),
    
    path('simulation/', views.simulation_view, name='simulation_view'),
    
    path('analysis/technical/', views.technical_analysis_view, name='technical_analysis'),
    
    path('history/', views.history_view, name='portfolio_history'),
    
    #path('dashboardfr/', get_analytics_dashboard, name='dashboardfre'),
    path('analysis/', analysis_list_view, name='analysis_list'),
    
    path("analysis/results/", views.analysis_results, name="analysis_results"),
    
    path('fvg/', views.fvg_monitor, name='fvg_monitor'),
    
    path("analysis/archive/", views.analysis_results, name="analysis_archive"),
    
    path('bi-dashboard/', views.bi_dashboard, name='bi_dashboard'),
    
    path('access-denied/', views.access_denied_view, name='access_denied'),
    
    path('dashboard-bi/', dashboard_bi_view, name='dashboard_bi')

]
