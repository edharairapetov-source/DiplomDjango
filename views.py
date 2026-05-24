# views.py
from django.shortcuts import render
from .analysis_code import run_analysis_clean

from .models import QuantAnalysis
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required









def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  
    else:
        form = UserCreationForm()
    return render(request, 'analysis/register.html', {'form': form})
@login_required
def dashboard(request):
    results = None

    if request.method == "POST":
        results = run_analysis_clean(
            n_stocks=int(request.POST.get("n_stocks", 10)),
            corr_threshold=float(request.POST.get("corr_threshold", 0.6)),

           
            min_expected_return=float(request.POST.get("min_er", 0.01)),
            max_expected_return=float(request.POST.get("max_er", 0.2)),

           
            S0=float(request.POST.get("S0", 100)),
            T=float(request.POST.get("T", 1.0)),
            r=float(request.POST.get("r", 0.05)),
            sigma=float(request.POST.get("sigma", 0.2)),
            I=int(request.POST.get("I", 1000)),

     
            lambda_jump=float(request.POST.get("lambda_jump", 0.3)),
            mu_jump=float(request.POST.get("mu_jump", -0.3)),
            delta_jump=float(request.POST.get("delta_jump", 0.1)),

            
            formula_str=request.POST.get("gnn_formula", "pred"),
        )



 
        tech_indicators = results.get("technical_indicators", {})
        results["SMA_5"] = tech_indicators.get("SMA_5")
        results["SMA_10"] = tech_indicators.get("SMA_10")
        results["SMA_20"] = tech_indicators.get("SMA_20")
        results["forward_return"] = tech_indicators.get("forward_return")
    
    
   
        results = run_analysis_clean(n_stocks=n_stocks, corr_threshold=corr_threshold)

       
        SimulationRecord.objects.create(
            user=request.user,  
            tickers=tickers_str,
            expected_return=results.get("expected_return", 0),
            risk=results.get("risk", 0),
            sharpe_ratio=results.get("sharpe_ratio", 0)
        )

    
    history = SimulationRecord.objects.filter(user=request.user).order_by('-timestamp')[:20]

    return render(request, "analysis/dashboard.html", {
        "results": results,
        "history": history,
        "live_data": live_data
    })
    
    results = run_analysis_clean(n_stocks=n_stocks, corr_threshold=corr_threshold)
        
    Simulation.objects.create(
            user=request.user,
            tickers=request.POST.get("tickers", ""),
            expected_return=results.get("expected_return", 0),
            risk=results.get("risk", 0),
            sharpe_ratio=results.get("sharpe_ratio", 0)
        )

    
    history = Simulation.objects.filter(user=request.user).order_by('-timestamp')

    return render(request, "analysis/dashboard.html", {
        "results": results,
        "history": history
    })
        
   # return render(request, "analysis/dashboard.html", {
       # "results": results,
      #  "user_analyses": user_analyses
   # })







from django.shortcuts import render
from django.http import JsonResponse
from .analysis_code import run_analysis_clean
import yfinance as yf
import pandas as pd

from .simulations import generate_price_series




import yfinance as yf
from django.http import JsonResponse
from django.core.cache import cache

def live_yfinance(request):
    ticker = request.GET.get("ticker", "AAPL")
    period = request.GET.get("period", "1d")
    interval = request.GET.get("interval", "1m")
    
    cache_key = f"yf_{ticker}_{period}_{interval}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return JsonResponse(cached_data)

    try:
        df = yf.download(tickers=ticker, period=period, interval=interval, progress=False)

        if df.empty or df.isnull().all().all():
            return JsonResponse({"error": "Yahoo returned no data"}, status=400)

    
        if hasattr(df.columns, "levels") and len(df.columns.levels) == 2:
            df.columns = df.columns.get_level_values(0)

        required_cols = {"Open", "High", "Low", "Close", "Volume"}
        if not required_cols.issubset(df.columns):
            return JsonResponse({"error": f"Missing columns: {df.columns.tolist()}"}, status=500)

        response_data = {
            "ticker": ticker,
            "time": df.index.strftime("%H:%M").tolist(),
            "open": df["Open"].round(2).tolist(),
            "high": df["High"].round(2).tolist(),
            "low": df["Low"].round(2).tolist(),
            "close": df["Close"].round(2).tolist(),
            "volume": df["Volume"].tolist()
        }

        
        cache.set(cache_key, response_data, 60)

        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)





def live_yfinance2(request):
    ticker = request.GET.get("ticker", "AAPL")
    period = request.GET.get("period", "1d")
    interval = request.GET.get("interval", "1m")

    try:
        df = yf.download(tickers=ticker, period=period, interval=interval, progress=False)
        if df.empty:
            return JsonResponse({"error": "No data"}, status=400)

        
        if hasattr(df.columns, "levels") and len(df.columns.levels) == 2:
            df.columns = df.columns.get_level_values(0)

        required = {"Open", "High", "Low", "Close", "Volume"}
        if not required.issubset(df.columns):
            return JsonResponse({"error": f"Missing columns: {df.columns.tolist()}"}, status=500)

        return JsonResponse({
            "ticker": ticker,
            "time": df.index.strftime("%H:%M").tolist(),
            "open": df["Open"].round(2).tolist(),
            "high": df["High"].round(2).tolist(),
            "low": df["Low"].round(2).tolist(),
            "close": df["Close"].round(2).tolist(),
            "volume": df["Volume"].tolist()
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



SIMULATION_HISTORY = []
@login_required
def dashboard(request):
    results = None
    if request.method == "POST":
        n_stocks = int(request.POST.get("n_stocks", 10))
        corr_threshold = float(request.POST.get("corr_threshold", 0.6))

        results = run_analysis_clean(n_stocks=n_stocks, corr_threshold=corr_threshold)

       
        SIMULATION_HISTORY.append({
            "date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
            "stocks": n_stocks,
            "return": round(results.get("expected_return", 0), 4),
            "risk": round(results.get("risk", 0), 4),
            "sharpe": round(results.get("sharpe_ratio", 0), 4)
        })

    return render(request, "analysis/dashboard.html", {
        "results": results,
        "history": SIMULATION_HISTORY
    })

from django.shortcuts import render
import yfinance as yf
from .analysis_code import run_analysis_clean
from datetime import datetime


SIMULATION_HISTORY = []
@login_required
def dashboard(request):
    live_data = live_yfinance;
    results = None

    if request.method == "POST":
        tickers = request.POST.get("tickers", "AAPL,MSFT,GOOGL").split(",")
        n_stocks = int(request.POST.get("n_stocks", len(tickers)))
        corr_threshold = float(request.POST.get("corr_threshold", 0.6))

        
        data = yf.download(tickers, period="1mo", interval="1d")['Close']
        live_data = data.to_dict()

        results = run_analysis_clean(n_stocks=n_stocks, corr_threshold=corr_threshold)
        results['tickers'] = tickers
        results['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

      
        SIMULATION_HISTORY.append(results)

    return render(request, "analysis/dashboard.html", {
        "results": results,
        "live_data": live_data,
        "history": SIMULATION_HISTORY
    })























from .quant_tests import var_cvar, hit_rate
from .efficient_frontier import efficient_frontier, plot_frontier
import numpy as np

import numpy as np
import yfinance as yf
from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import QuantAnalysis  # ОБЯЗАТЕЛЬНО
import numpy as np


# from .simulations import generate_price_series
# from .quant_tests import var_cvar, hit_rate
# from .efficient_frontier import efficient_frontier, plot_frontier

#@login_required

import numpy as np
import yfinance as yf
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import QuantAnalysis

@login_required
def quant_lab7(request):
  
    history = QuantAnalysis.objects.filter(user=request.user).order_by('-timestamp')
    context = {"history": history}

    if request.method == "POST":
        try:
            
            n_stocks = int(request.POST.get("n_stocks") or 10)
            mu = float(request.POST.get("mu") or 0.1)
            sigma = float(request.POST.get("sigma") or 0.2)

            
            days = 252
            dt = 1/days
           
            stoch_returns = np.exp((mu - 0.5 * sigma**2) * dt + 
                                   sigma * np.sqrt(dt) * np.random.standard_normal((days, n_stocks)))
            prices = np.where(np.arange(days)[:, None] == 0, 100, 0).astype(float)
            for t in range(1, days):
                prices[t] = prices[t-1] * stoch_returns[t]
            
          
            returns_pct = (prices[1:] / prices[:-1]) - 1
            port_returns = returns_pct.mean(axis=1)

         
            conf_level = 0.05
            sorted_returns = np.sort(port_returns)
            current_var = np.percentile(sorted_returns, conf_level * 100)
            current_cvar = sorted_returns[sorted_returns <= current_var].mean()
            
           
            current_hit_rate = np.sum(port_returns > 0) / len(port_returns)

           
            current_frontier_img = "" 
            try:
                # 
                mu_vec = returns_pct.mean(axis=0)
                cov = np.cov(returns_pct.T)
                # risk_pts, ret_pts = efficient_frontier(mu_vec, cov)
                # current_frontier_img = plot_frontier(risk_pts, ret_pts)
            except:
                current_frontier_img = "frontier_placeholder.png"

           
            QuantAnalysis.objects.create(
                user=request.user,
                n_stocks=n_stocks,
                mu=mu,
                sigma=sigma,
                var_value=round(abs(current_var), 4),  # Сохраняем как положительное число риска
                cvar_value=round(abs(current_cvar), 4),
                hit_rate=round(current_hit_rate, 4),
                frontier_img=current_frontier_img
            )

           
            context.update({
                "var": round(abs(current_var), 4),
                "cvar": round(abs(current_cvar), 4),
                "hit_rate": round(current_hit_rate * 100, 2), # в процентах
                "frontier_img": current_frontier_img,
                "success": True
            })

        except Exception as e:
            context["error"] = f"Ошибка в расчетах: {e}"

    return render(request, "analysis/quant_lab.html", context)

@login_required

def quant_lab6(request):
    
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'SPY'] 
    
   
    data = yf.download(tickers, period="2y")['Close']
    
   
    # log_returns = ln(P_t / P_{t-1})
    log_returns = np.log(data / data.shift(1)).dropna()
    
    
    # Умножаем на 252 (торговые дни в году) для годовых значений
    mu_annual = log_returns.mean() * 252
    cov_annual = log_returns.cov() * 252
    
   
    num_portfolios = 5000
    results = np.zeros((3, num_portfolios))
    
    for i in range(num_portfolios):
      
        weights = np.array(np.random.random(len(tickers)))
        weights /= np.sum(weights) # сумма весов всегда 1 (100%)
        
       
        portfolio_return = np.sum(weights * mu_annual)
        portfolio_std_dev = np.sqrt(np.dot(weights.T, np.dot(cov_annual, weights)))
        
        results[0,i] = portfolio_return
        results[1,i] = portfolio_std_dev
       
        results[2,i] = (portfolio_return - 0.02) / portfolio_std_dev

    
    max_sharpe_idx = np.argmax(results[2])
    best_ret = results[0, max_sharpe_idx]
    best_risk = results[1, max_sharpe_idx]

   
    QuantAnalysis.objects.create(
        user=request.user,
        mu=round(best_ret, 4),
        sigma=round(best_risk, 4),
        var_value=round(best_risk * 1.65, 4), # Параметрический VaR 95%
        hit_rate=round(len(log_returns[log_returns.mean(axis=1) > 0]) / len(log_returns), 4)
    )
    
    return render(request, "analysis/quant_lab.html", {'best_ret': best_ret})








import json
import numpy as np
import yfinance as yf
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Max, Count
from .models import QuantAnalysisbi

@login_required
def unified_quant_bi_pro(request):
    
    error_msg = None
    show_results = False
    current_run = None
    stress_label = "✅ БАЗОВЫЙ СЦЕНАРИЙ" 
    tickers_str = request.POST.get("tickers", "AAPL,MSFT,SPY")

    if request.method == "POST":
        stress_scenario = request.POST.get("stress_test", "none") 
        tickers_list = [t.strip().upper() for t in tickers_str.split(",")]

        try:
          
            df = yf.download(tickers_list, period="1y", progress=False)['Close']
            if df.empty:
                raise ValueError("Данные по тикерам не найдены")
            
            returns = df.dropna().pct_change().dropna()
            
            
            mu_raw = returns.mean().values * 252
            cov_raw = returns.cov().values * 252

           
            if stress_scenario == "crash":
                mu_raw -= 0.30
                cov_raw *= 2.0
                stress_label = "⚠️ КРАХ РЫНКА (-30%)"
            elif stress_scenario == "vol_spike":
                cov_raw *= 3.0
                stress_label = "⚡️ ШОК ВОЛАТИЛЬНОСТИ (3x)"
            else:
                stress_label = "✅ БАЗОВЫЙ СЦЕНАРИЙ"

            avg_mu = np.mean(mu_raw)
            avg_sigma = np.sqrt(np.mean(np.diag(cov_raw)))
            
            
            var_calc = round(abs(avg_mu - (1.65 * avg_sigma)), 4)
            cvar_calc = round(abs(avg_mu - (2.06 * avg_sigma)), 4)
            hit_calc = round((returns > 0).mean().mean() * 100, 2)

     
            pbi_value_snapshot = round(avg_mu * 100, 2)

           
            current_run = QuantAnalysisbi.objects.create(
                user=request.user,
                n_stocks=len(tickers_list),
                mu=round(avg_mu * 100, 2),
                sigma=round(avg_sigma, 4),
                var_value=var_calc,
                cvar_value=cvar_calc,
                hit_rate=hit_calc,
                
                power_bi_metrics=pbi_value_snapshot 
            )
            show_results = True

        except Exception as e:
            error_msg = f"Ошибка данных: {str(e)}"

   
    history = QuantAnalysisbi.objects.filter(user=request.user).order_by('-timestamp')
    
    bi_stats = history.aggregate(
        avg_mu=Avg('mu'),
        max_var=Max('var_value'),
       
        pbi_avg_yield=Avg('power_bi_metrics'), 
        total=Count('id')
    )

    chart_list = list(reversed(history[:15]))
    history_json = json.dumps([
        {
            "date": h.timestamp.strftime("%H:%M"), 
            "mu": float(h.mu or 0), 
            "var": float(h.var_value or 0),
          
            "pbi_val": float(h.power_bi_metrics or 0) 
        } for h in chart_list
    ])

    context = {
        "current": current_run,
        "history": history,
        "bi_stats": bi_stats,
        "show_results": show_results,
        "stress_label": stress_label,
        "tickers": tickers_str,
        "history_json": history_json,
        "error": error_msg
    }

    return render(request, "analysis/unified_quant_bi_pro.html", context)


def unified_quant_bi_pro5(request):
  
    error_msg = None
    show_results = False
    current_run = None
    stress_label = "✅ БАЗОВЫЙ СЦЕНАРИЙ" # Добавили значение по умолчанию
    tickers_str = request.POST.get("tickers", "AAPL,MSFT,SPY")

    if request.method == "POST":
        stress_scenario = request.POST.get("stress_test", "none") # Получаем сценарий из формы
        tickers_list = [t.strip().upper() for t in tickers_str.split(",")]

        try:
            
            df = yf.download(tickers_list, period="1y", progress=False)['Close']
            if df.empty:
                raise ValueError("Данные по тикерам не найдены")
            
            returns = df.dropna().pct_change().dropna()
            
           
            mu_raw = returns.mean().values * 252
            cov_raw = returns.cov().values * 252

           
            if stress_scenario == "crash":
                mu_raw -= 0.30
                cov_raw *= 2.0
                stress_label = " КРАХ РЫНКА (-30%)"
            elif stress_scenario == "vol_spike":
                cov_raw *= 3.0
                stress_label = "️ ШОК ВОЛАТИЛЬНОСТИ (3x)"
            else:
                stress_label = " БАЗОВЫЙ СЦЕНАРИЙ"

            avg_mu = np.mean(mu_raw)
            avg_sigma = np.sqrt(np.mean(np.diag(cov_raw)))
            
            
            var_calc = round(abs(avg_mu - (1.65 * avg_sigma)), 4)
            cvar_calc = round(abs(avg_mu - (2.06 * avg_sigma)), 4)
            hit_calc = round((returns > 0).mean().mean() * 100, 2)

           
            current_run = QuantAnalysisbi.objects.create(
                user=request.user,
                n_stocks=len(tickers_list),
                mu=round(avg_mu * 100, 2),
                sigma=round(avg_sigma, 4),
                var_value=var_calc,
                cvar_value=cvar_calc,
                hit_rate=hit_calc
            )
            show_results = True

        except Exception as e:
            error_msg = f"Ошибка данных: {str(e)}"

   
    history = QuantAnalysisbi.objects.filter(user=request.user).order_by('-timestamp')
    
    bi_stats = history.aggregate(
        avg_mu=Avg('mu'),
        max_var=Max('var_value'),
        total=Count('id')
    )

    chart_list = list(reversed(history[:15]))
    history_json = json.dumps([
        {
            "date": h.timestamp.strftime("%H:%M"), 
            "mu": float(h.mu or 0), 
            "var": float(h.var_value or 0)
        } for h in chart_list
    ])

    context = {
        "current": current_run,
        "history": history,
        "bi_stats": bi_stats,
        "show_results": show_results,
        "stress_label": stress_label, 
        "tickers": tickers_str,
        "history_json": history_json,
        "error": error_msg
    }

    return render(request, "analysis/unified_quant_bi_pro.html", context)
def unified_quant_bi_pro2(request):
    error_msg = None
    show_results = False
    current_run = None
    stress_label = "Анализ готов"
    tickers_str = request.POST.get("tickers", "AAPL,MSFT,SPY")

    if request.method == "POST":
        stress_scenario = request.POST.get("stress_test", "none")
        tickers_list = [t.strip().upper() for t in tickers_str.split(",")]

        try:
           
            df = yf.download(tickers_list, period="1y", progress=False)['Close']
            if len(tickers_list) == 1: df = df.to_frame()
            
            returns = df.dropna().pct_change().dropna()
            
           
            mu_raw = returns.mean().values * 252
            cov_raw = returns.cov().values * 252
            
            
            if stress_scenario == "crash":
                mu_raw -= 0.30
                cov_raw *= 2.0
                stress_label = "️ КРАХ РЫНКА (-30%)"
            elif stress_scenario == "vol_spike": 
                cov_raw *= 3.0
                stress_label = "️ ШОК ВОЛАТИЛЬНОСТИ (3x)"
            else:
                stress_label = " БАЗОВЫЙ СЦЕНАРИЙ"

           
            avg_mu = np.mean(mu_raw)
            avg_sigma = np.sqrt(np.mean(np.diag(cov_raw)))

            
            var_calc = avg_mu - (1.65 * avg_sigma)
            
            cvar_calc = avg_mu - (2.06 * avg_sigma)
            
           
            current_run = QuantAnalysisbi.objects.create(
                user=request.user,
                n_stocks=len(tickers_list),
                mu=round(avg_mu * 100, 2),
                sigma=round(avg_sigma, 4),
                var_value=round(abs(var_calc), 4),
                cvar_value=round(abs(cvar_calc), 4) # Теперь поле заполнено!
            )
            show_results = True

        except Exception as e:
            error_msg = f"Ошибка данных: {str(e)}"

    
    history = QuantAnalysisbi.objects.filter(user=request.user).order_by('-timestamp')
    bi_stats = history.aggregate(
        avg_mu=Avg('mu'),
        max_var=Max('var_value'),
        total=Count('id')
    )

    chart_list = list(reversed(history[:15]))
    history_json = json.dumps([
        {
            "date": h.timestamp.strftime("%H:%M"), 
            "mu": float(h.mu), 
            "var": float(h.var_value)
        } for h in chart_list
    ])

    context = {
        "current": current_run,
        "history": history,
        "bi_stats": bi_stats,
        "show_results": show_results,
        "stress_label": stress_label,
        "tickers": tickers_str,
        "history_json": history_json,
        "error": error_msg
    }

    return render(request, "analysis/unified_quant_bi_pro.html", context)
def unified_quant_bi_pro3(request):
    error_msg = None
    show_results = False
    current_run = None
    stress_label = "Анализ готов"
    tickers_str = request.POST.get("tickers", "AAPL,MSFT,SPY")

   
    if request.method == "POST":
        stress_scenario = request.POST.get("stress_test", "none")
        tickers_list = [t.strip().upper() for t in tickers_str.split(",")]

        try:
            
            
           
            df = yf.download(tickers_list, period="1y", progress=False)['Close']
            if len(tickers_list) == 1: df = df.to_frame()
            
            returns = df.dropna().pct_change().dropna()
            
           
            mu_raw = returns.mean().values * 252
            cov_raw = returns.cov().values * 252
            
           
            if stress_scenario == "crash":
                mu_raw -= 0.30
                cov_raw *= 2.0
                stress_label = "⚠ КРАХ РЫНКА (-30%)"
            elif stress_scenario == "vol_spike":
                cov_raw *= 3.0
                stress_label = "️ ШОК ВОЛАТИЛЬНОСТИ (3x)"
            else:
                stress_label = " БАЗОВЫЙ СЦЕНАРИЙ"

            avg_mu = np.mean(mu_raw)
            avg_sigma = np.sqrt(np.mean(np.diag(cov_raw)))
            
            cvar_calc = avg_mu - (2.06 * avg_sigma)

            current_run = QuantAnalysisbi.objects.create(
              user=request.user,
               n_stocks=len(tickers_list),
              mu=round(avg_mu * 100, 2),
              sigma=round(avg_sigma, 4),
              var_value=round(abs(var_calc), 4),
              cvar_value=round(abs(cvar_calc), 4)  # Добавляем это поле
                   )

        except Exception as e:
            error_msg = f"Ошибка данных: {str(e)}"

   
    history = QuantAnalysis.objects.filter(user=request.user).order_by('-timestamp')
    bi_stats = history.aggregate(
        avg_mu=Avg('mu'),
        max_var=Max('var_value'),
        total=Count('id')
    )

    
    chart_list = list(reversed(history[:15]))
    history_json = json.dumps([
        {
            "date": h.timestamp.strftime("%H:%M"), 
            "mu": float(h.mu), 
            "var": float(h.var_value)
        } for h in chart_list
    ])

    context = {
        "current": current_run,
        "history": history,
        "bi_stats": bi_stats,
        "show_results": show_results,
        "stress_label": stress_label,
        "tickers": tickers_str,
        "history_json": history_json,
        "error": error_msg
    }

    return render(request, "analysis/unified_quant_bi_pro.html", context)
import json
import numpy as np
import yfinance as yf
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Max, Count
from .models import QuantAnalysis

@login_required
def unified_quant_bi_pro2(request):
   
    history = QuantAnalysis.objects.filter(user=request.user).order_by('-timestamp')
    bi_stats = history.aggregate(
        avg_mu=Avg('mu'),
        max_var=Max('var_value'),
        total=Count('id')
    )

    context = {
        "history": history,
        "bi_stats": bi_stats,
        "stress_label": "Анализ готов",
        "show_results": False
    }

   
    if request.method == "POST":
        tickers_str = request.POST.get("tickers", "AAPL,MSFT,SPY")
        stress_scenario = request.POST.get("stress_test", "none")
        tickers_list = [t.strip().upper() for t in tickers_str.split(",")]

        try:
            df = yf.download(tickers_list, period="1y", progress=False)['Close']
            if len(tickers_list) == 1: df = df.to_frame()
            returns = df.dropna().pct_change().dropna()
            
            mu = returns.mean().values * 252
            cov = returns.cov().values * 252
            
           
            if stress_scenario == "crash":
                mu -= 0.30
                cov *= 2.0
                context["stress_label"] = "⚠️ КРАХ РЫНКА"
            elif stress_scenario == "vol_spike":
                cov *= 3.0
                context["stress_label"] = "⚡️ ШОК ВОЛАТИЛЬНОСТИ"

            avg_sigma = np.sqrt(np.mean(np.diag(cov)))
            current_var = np.mean(mu) - (1.65 * avg_sigma)
            
            #
            new_run = QuantAnalysis.objects.create(
                user=request.user,
                n_stocks=len(tickers_list),
                mu=round(np.mean(mu), 4),
                sigma=round(avg_sigma, 4),
                var_value=round(abs(current_var), 4),
            )
            context["current"] = new_run
            context["show_results"] = True
            context["tickers"] = tickers_str
            
        except Exception as e:
            context["error"] = str(e)

    
    chart_history = list(reversed(history[:15]))
    context["history_json"] = json.dumps([
        {"date": h.timestamp.strftime("%d.%m"), "mu": float(h.mu), "var": float(h.var_value)}
        for h in chart_history
    ])

    return render(request, "analysis/unified_quant_bi_pro.html", context)



import yfinance as yf
import numpy as np



@login_required
def quant_lab(request):
    history = QuantAnalysis.objects.filter(user=request.user).order_by('-timestamp')
    context = {"history": history}

    if request.method == "POST":
        
        tickers_str = request.POST.get("tickers", "AAPL,MSFT,SPY")
        stress_scenario = request.POST.get("stress_test", "none") # none, crash, vol_spike
        tickers_list = [t.strip().upper() for t in tickers_str.split(",")]
        
        try:
            
            df = yf.download(tickers_list, period="2y")['Close']
            if len(tickers_list) == 1: df = df.to_frame()
            returns_df = df.dropna().pct_change().dropna()
            
            
            mu_base = returns_df.mean().values * 252
            cov_base = returns_df.cov().values * 252
            
            
            stress_label = "Без стресса"
            if stress_scenario == "crash":
               
                mu_base = mu_base - 0.30
                cov_base = cov_base * 2.0
                stress_label = "Рыночный обвал (-30% доходности)"
            elif stress_scenario == "vol_spike":
                
                cov_base = cov_base * 3.0
                stress_label = "Шок волатильности (Риск x3)"

            
            n_days = 252
            n_stocks = len(tickers_list)
            
            
            chol = np.linalg.cholesky(cov_base / 252)
            s_returns = np.dot(np.random.randn(n_days, n_stocks), chol.T) + (mu_base / 252)
            
            port_returns = s_returns.mean(axis=1) # 
            
            
            current_var, current_cvar = var_cvar(port_returns)
            current_hit_rate = hit_rate(port_returns)
            
            
            risk_pts, ret_pts = efficient_frontier(mu_base, cov_base)
            current_frontier_img = plot_frontier(risk_pts, ret_pts)

            
            QuantAnalysis.objects.create(
                user=request.user,
                n_stocks=n_stocks,
                mu=round(np.mean(mu_base), 4),
                sigma=round(np.sqrt(np.mean(np.diag(cov_base))), 4),
                var_value=round(abs(current_var), 4),
                cvar_value=round(abs(current_cvar), 4),
                hit_rate=round(current_hit_rate, 4),
                frontier_img=current_frontier_img
            )

            context.update({
                "var": round(abs(current_var), 4),
                "cvar": round(abs(current_cvar), 4),
                "hit_rate": round(current_hit_rate * 100, 2),
                "frontier_img": current_frontier_img,
                "stress_label": stress_label,
                "success": True
            })

        except Exception as e:
            context["error"] = f"Ошибка анализа: {e}"

    return render(request, "analysis/quant_lab.html", context)


def quant_labважно2(request):
    history = QuantAnalysis.objects.filter(user=request.user).order_by('-timestamp')
    context = {"history": history}

    if request.method == "POST":
        
        tickers_str = request.POST.get("tickers", "AAPL,MSFT,GOOGL,SPY")
        tickers_list = [t.strip().upper() for t in tickers_str.split(",")]
        
        try:
            
            df = yf.download(tickers_list, period="2y")['Close']
            
            
            if len(tickers_list) == 1:
                df = df.to_frame()
                
            
            df = df.dropna()
            
           
            returns_df = df.pct_change().dropna()
            
            
            mu_real = float(returns_df.mean().mean() * 252) 
            sigma_real = float(returns_df.std().mean() * np.sqrt(252))
            n_stocks = len(tickers_list)

           
            port_returns = returns_df.mean(axis=1) 
            
            current_var, current_cvar = var_cvar(port_returns)
            current_hit_rate = hit_rate(port_returns)

            
            mu_vec = returns_df.mean().values * 252
            cov = returns_df.cov().values * 252
            
            risk, ret = efficient_frontier(mu_vec, cov)
            current_frontier_img = plot_frontier(risk, ret)

            
            QuantAnalysis.objects.create(
                user=request.user,
                n_stocks=n_stocks,
                mu=round(mu_real, 4),
                sigma=round(sigma_real, 4),
                var_value=round(abs(current_var), 4),
                cvar_value=round(abs(current_cvar), 4),
                hit_rate=round(current_hit_rate, 4),
                frontier_img=current_frontier_img
            )

            context.update({
                "var": round(abs(current_var), 4),
                "cvar": round(abs(current_cvar), 4),
                "hit_rate": round(current_hit_rate * 100, 2),
                "frontier_img": current_frontier_img,
                "tickers": tickers_list,
                "real_mu": round(mu_real, 4),
            })

        except Exception as e:
            context["error"] = f"Ошибка загрузки данных: {e}"

    return render(request, "analysis/quant_lab.html", context)

def quant_labважно(request):
    
    history = QuantAnalysis.objects.filter(user=request.user).order_by('-timestamp')
    context = {"history": history}

    if request.method == "POST":
        
        n_stocks = int(request.POST.get("n_stocks", 10))
        mu = float(request.POST.get("mu", 0.1))
        sigma = float(request.POST.get("sigma", 0.2))

        
        prices = generate_price_series(n_stocks, 252, mu, sigma)
        returns = prices[1:] / prices[:-1] - 1
        port_returns = returns.mean(axis=1)

        current_var, current_cvar = var_cvar(port_returns)
        current_hit_rate = hit_rate(port_returns)

        mu_vec = returns.mean(axis=0)
        cov = np.cov(returns.T)
        risk, ret = efficient_frontier(mu_vec, cov)
        current_frontier_img = plot_frontier(risk, ret)

        
        QuantAnalysis.objects.create(
            user=request.user,
            n_stocks=n_stocks,
            mu=mu,
            sigma=sigma,
            var_value=round(current_var, 4),
            cvar_value=round(current_cvar, 4),
            hit_rate=round(current_hit_rate, 4),
            frontier_img=current_frontier_img
        )

        
        context.update({
            "var": round(current_var, 4),
            "cvar": round(current_cvar, 4),
            "hit_rate": round(current_hit_rate, 4),
            "frontier_img": current_frontier_img,
        })

    return render(request, "analysis/quant_lab.html", context)

def quant_labшьзщкефте(request):
    context = {}

    if request.method == "POST":
        n_stocks = int(request.POST.get("n_stocks", 10))
        mu = float(request.POST.get("mu", 0.1))
        sigma = float(request.POST.get("sigma", 0.2))

        prices = generate_price_series(n_stocks, 252, mu, sigma)
        returns = prices[1:] / prices[:-1] - 1
        port_returns = returns.mean(axis=1)

        var, cvar = var_cvar(port_returns)
        context["var"] = round(var, 4)
        context["cvar"] = round(cvar, 4)
        context["hit_rate"] = round(hit_rate(port_returns), 4)

        mu_vec = returns.mean(axis=0)
        cov = np.cov(returns.T)

        risk, ret = efficient_frontier(mu_vec, cov)
        context["frontier_img"] = plot_frontier(risk, ret)
        
        
        


    return render(request, "analysis/quant_lab.html", context)

    #return render(request, "analysis/quant_lab.html", context)


from .models import QuantLab3Result
import json

@login_required
@login_required
def quant_lab3(request):
    results = None
    live_data = live_yfinance;
    
    history = QuantLab3Result.objects.filter(user=request.user).order_by('-timestamp')[:10]

    if request.method == "POST":
        
        tickers_raw = request.POST.get("tickers", "AAPL,MSFT")
        tickers_list = [t.strip() for t in tickers_raw.split(",")]
        n_stocks = int(request.POST.get("n_stocks", len(tickers_list)))
        corr_threshold = float(request.POST.get("corr_threshold", 0.6))

        
        try:
            data = yf.download(tickers_list, period="1mo", interval="1d")['Close']
            live_data = data.to_dict()
            
            
            results = run_analysis_clean(n_stocks=n_stocks, corr_threshold=corr_threshold)
            
            
            QuantLab3Result.objects.create(
                user=request.user,  
                tickers=tickers_raw,
                n_stocks=n_stocks,
                corr_threshold=corr_threshold,
                expected_return=results.get("expected_return"),
                risk=results.get("risk"),
                sharpe_ratio=results.get("sharpe_ratio"),
                raw_results=results
            )
            
           
            history = QuantLab3Result.objects.filter(user=request.user).order_by('-timestamp')[:10]

        except Exception as e:
            print(f"Ошибка при расчете или сохранении: {e}")

    return render(request, "analysis/quant_lab.html", {
        "results": results,
        "live_data": live_data,
        "history": history,
    })
def quant_lab3imp(request):
    results = None
    live_data = None
    
    history = QuantLab3Result.objects.filter(user=request.user).order_by('-timestamp')[:10]

    if request.method == "POST":
        tickers_raw = request.POST.get("tickers", "AAPL,MSFT")
        tickers_list = [t.strip() for t in tickers_raw.split(",")]
        n_stocks = int(request.POST.get("n_stocks", len(tickers_list)))
        corr_threshold = float(request.POST.get("corr_threshold", 0.6))

        
        try:
            data = yf.download(tickers_list, period="1mo", interval="1d")['Close']
            live_data = data.to_dict()
        except Exception as e:
            print(f"YFinance Error: {e}")

        
        results = run_analysis_clean(n_stocks=n_stocks, corr_threshold=corr_threshold)
        
        
        QuantLab3Result.objects.create(
            user=request.user,
            tickers=tickers_raw,
            n_stocks=n_stocks,
            corr_threshold=corr_threshold,
            expected_return=results.get("expected_return"),
            risk=results.get("risk"),
            sharpe_ratio=results.get("sharpe_ratio"),
           
            raw_results=results 
        )
        
        
        history = QuantLab3Result.objects.filter(user=request.user).order_by('-timestamp')[:10]

    context = {
        "results": results,
        "live_data": live_data,
        "history": history,
    }

    return render(request, "analysis/quant_lab.html", context)
def quant_lab32(request):
    results = None
    live_data = None

    if request.method == "POST":
        tickers = request.POST.get("tickers", "AAPL,MSFT").split(",")
        n_stocks = int(request.POST.get("n_stocks", len(tickers)))
        corr_threshold = float(request.POST.get("corr_threshold", 0.6))

        
        data = yf.download(tickers, period="1mo", interval="1d")['Close']
        live_data = data.to_dict()

        
        results = run_analysis_clean(n_stocks=n_stocks, corr_threshold=corr_threshold)
        results['tickers'] = tickers

    context = {
        "results": results,
        "live_data": live_data,
    }
    
    
    
    results = { 
    "tickers": ["AAPL","MSFT","GOOGL"], 
    "expected_return": 0.12, 
    "risk": 0.18, 
    "sharpe_ratio": 0.67, 
    "jump_diffusion": { 
        "lambda": 0.3, 
        "mu": -0.2, 
        "delta": 0.1, 
        "prices": [100, 101, 99, 102, 103] 
    }, 
    "stress_scenarios": [ 
        {"name": "Market Crash", "expected_return": -0.25, "risk": 0.3}, 
        {"name": "Bull Market", "expected_return": 0.18, "risk": 0.15} 
    ] 
}

    return render(request, "analysis/quant_lab.html", context)






















from .simulations import (
    correlated_gbm,
    jump_diffusion,
    yahoo_returns,
)
from .stress import apply_stress
import numpy as np

def quant_lab4(request):
    context = {}

    if request.method == "POST":
        tickers = request.POST.get(
            "tickers", "AAPL,MSFT,GOOGL"
        ).split(",")

        model = request.POST.get("model", "gbm")
        stress = request.POST.get("stress", "none")

       
        data = yahoo_returns(tickers)
        mu, sigma, corr = data["mu"], data["sigma"], data["corr"]

        if stress != "none":
            mu, sigma = apply_stress(mu, sigma, stress)

        
        if model == "jump":
            prices = jump_diffusion(
                len(tickers), 252,
                mu, sigma, corr
            )
        else:
            prices = correlated_gbm(
                len(tickers), 252,
                mu, sigma, corr
            )

        returns = prices[1:] / prices[:-1] - 1
        port_returns = returns.mean(axis=1)

        context["mean_return"] = round(port_returns.mean(), 4)
        context["vol"] = round(port_returns.std(), 4)

    return render(request, "analysis/quant_lab.html", context)







def quant_lab5(request):
    context = {}

    if request.method == "POST":
        tickers = request.POST.get("tickers", "AAPL,MSFT,GOOGL").split(",")
        model = request.POST.get("model", "gbm")
        stress = request.POST.get("stress", "none")

        
        data = yahoo_returns(tickers)
        mu, sigma, corr = data["mu"], data["sigma"], data["corr"]

        if stress != "none":
            mu, sigma = apply_stress(mu, sigma, stress)

        
        if model == "jump":
            prices = jump_diffusion(len(tickers), 252, mu, sigma, corr)
        else:
            prices = correlated_gbm(len(tickers), 252, mu, sigma, corr)

        returns = prices[1:] / prices[:-1] - 1
        port_returns = returns.mean(axis=1)

        context.update({
            "tickers": tickers,
            "mean_return": round(port_returns.mean(), 4),
            "vol": round(port_returns.std(), 4),
            "prices": prices.tolist()
        })

    return render(request, "analysis/quant_lab.html", context)







































#попытка ноу-код и кода
# analysis/views.py
from django.shortcuts import render
from .simulations import correlated_gbm, jump_diffusion
import numpy as np

def quant_lab6(request):
    context = {}
    if request.method == "POST":
        tickers = request.POST.get("tickers", "AAPL,MSFT,GOOGL").split(",")
        model = request.POST.get("model", "gbm")
        n_days = int(request.POST.get("n_days", 252))

        
        mu = float(request.POST.get("mu", 0.1))
        sigma = float(request.POST.get("sigma", 0.2))
        corr = float(request.POST.get("corr", 0.5))

        if model == "jump":
            prices = jump_diffusion(len(tickers), n_days, mu, sigma, corr)
        else:
            prices = correlated_gbm(len(tickers), n_days, mu, sigma, corr)

        context["tickers"] = tickers
        context["prices"] = prices.tolist()
        context["mean_return"] = round(np.mean(prices[1:]/prices[:-1]-1), 4)
        context["vol"] = round(np.std(prices[1:]/prices[:-1]-1), 4)

    return render(request, "analysis/quant_lab.html", context)





















from django.shortcuts import render
from django.http import JsonResponse
import sys, io, traceback



from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import numpy as np


@csrf_exempt
def python_console(request):
    """
    Advanced Quant Python Console with:
    - NumPy
    - Quant finance functions
    - Matplotlib plotting
    - Base64 image rendering
    - Safe Cholesky handling
    """

    import sys
    import io
    import base64
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")  
    import matplotlib.pyplot as plt
    from io import BytesIO
    from django.shortcuts import render

    output = ""
    code = ""
    plot_image = None

   

    def returns(prices, log=False):
        prices = np.asarray(prices)
        if log:
            return np.diff(np.log(prices))
        return np.diff(prices) / prices[:-1]

    def volatility(r, annualization=252):
        return np.std(r) * np.sqrt(annualization)

    def sharpe_ratio(r, risk_free=0.0, annualization=252):
        excess = r - risk_free / annualization
        return np.mean(excess) / np.std(excess) * np.sqrt(annualization)

    def max_drawdown(prices):
        prices = np.asarray(prices)
        cummax = np.maximum.accumulate(prices)
        drawdown = (prices - cummax) / cummax
        return np.min(drawdown)

    def var_parametric(r, alpha=0.05):
        mean = np.mean(r)
        std = np.std(r)
        z = 1.65 if alpha == 0.05 else 2.33
        return mean - z * std

    def correlation_matrix(data):
        return np.corrcoef(np.asarray(data).T)

    def portfolio_return(weights, mean_returns):
        return np.dot(weights, mean_returns)

    def portfolio_volatility(weights, cov_matrix):
        return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

    def beta(asset_returns, market_returns):
        cov = np.cov(asset_returns, market_returns)
        return cov[0, 1] / cov[1, 1]

    def monte_carlo_gbm(S0, mu, sigma, T=1, steps=252, simulations=100):
        dt = T / steps
        paths = np.zeros((steps, simulations))
        paths[0] = S0
        for t in range(1, steps):
            z = np.random.standard_normal(simulations)
            paths[t] = paths[t-1] * np.exp(
                (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z
            )
        return paths

    

    if request.method == "POST":
        code = request.POST.get("code", "")

        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()

        safe_globals = {
            "np": np,
            "plt": plt,
            "returns": returns,
            "volatility": volatility,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "var_parametric": var_parametric,
            "correlation_matrix": correlation_matrix,
            "portfolio_return": portfolio_return,
            "portfolio_volatility": portfolio_volatility,
            "beta": beta,
            "monte_carlo_gbm": monte_carlo_gbm,
        }

        
        original_cholesky = np.linalg.cholesky

        def safe_cholesky(a):
            a = np.array(a)
            if a.ndim == 0:
                a = np.full((2, 2), a)
                np.fill_diagonal(a, 1.0)
            elif a.ndim == 1:
                a = np.diag(a)
            return original_cholesky(a)

        np.linalg.cholesky = safe_cholesky

        try:
            exec(code, safe_globals)

            printed = redirected_output.getvalue()
            result_val = safe_globals.get("result", None)

            
            if plt.get_fignums():
                buffer = BytesIO()
                plt.savefig(buffer, format="png")
                buffer.seek(0)
                plot_image = base64.b64encode(buffer.getvalue()).decode()
                buffer.close()
                plt.close("all")

            if result_val is not None:
                output = f"{printed}\nResult:\n{result_val}"
            else:
                output = printed or "Code executed successfully."

        except Exception as e:
            output = f"Error: {e}"

        finally:
            np.linalg.cholesky = original_cholesky
            sys.stdout = old_stdout

    return render(request, "analysis/python_console.html", {
        "code": code,
        "output": output,
        "plot_image": plot_image,
    })
def python_console4(request):
    """
    Python console for the app:
    - Executes Python code
    - Shows printed output
    - Shows 'result' variable if defined
    - Safe handling of scalar correlation in Cholesky
    - Includes quantitative finance functions
    """

    import sys
    import io
    import numpy as np
    from django.shortcuts import render

    output = ""
    code = ""

    

    def returns(prices, log=False):
        prices = np.asarray(prices)
        if log:
            return np.diff(np.log(prices))
        return np.diff(prices) / prices[:-1]

    def volatility(returns, annualization=252):
        returns = np.asarray(returns)
        return np.std(returns) * np.sqrt(annualization)

    def sharpe_ratio(returns, risk_free=0.0, annualization=252):
        returns = np.asarray(returns)
        excess = returns - risk_free / annualization
        return np.mean(excess) / np.std(excess) * np.sqrt(annualization)

    def max_drawdown(prices):
        prices = np.asarray(prices)
        cumulative_max = np.maximum.accumulate(prices)
        drawdowns = (prices - cumulative_max) / cumulative_max
        return np.min(drawdowns)

    def var_parametric(returns, alpha=0.05):
        mean = np.mean(returns)
        std = np.std(returns)
       
        z = 1.65 if alpha == 0.05 else 2.33
        return mean - z * std

    def correlation_matrix(data):
        return np.corrcoef(np.asarray(data).T)

    def portfolio_return(weights, mean_returns):
        return np.dot(weights, mean_returns)

    def portfolio_volatility(weights, cov_matrix):
        return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

    def beta(asset_returns, market_returns):
        cov = np.cov(asset_returns, market_returns)
        return cov[0, 1] / cov[1, 1]

    def monte_carlo_gbm(S0, mu, sigma, T=1, steps=252, simulations=1000):
        dt = T / steps
        paths = np.zeros((steps, simulations))
        paths[0] = S0
        for t in range(1, steps):
            z = np.random.standard_normal(simulations)
            paths[t] = paths[t-1] * np.exp(
                (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z
            )
        return paths

   

    if request.method == "POST":
        code = request.POST.get("code", "")

      
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()

        
        safe_globals = {
            "np": np,
            "returns": returns,
            "volatility": volatility,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "var_parametric": var_parametric,
            "correlation_matrix": correlation_matrix,
            "portfolio_return": portfolio_return,
            "portfolio_volatility": portfolio_volatility,
            "beta": beta,
            "monte_carlo_gbm": monte_carlo_gbm,
        }
        
       
        original_cholesky = np.linalg.cholesky

        def safe_cholesky(a):
            a = np.array(a)
            if a.ndim == 0:
                a = np.full((2, 2), a)
                np.fill_diagonal(a, 1.0)
            elif a.ndim == 1:
                a = np.diag(a)
            return original_cholesky(a)

        np.linalg.cholesky = safe_cholesky

        try:
            exec(code, safe_globals)

            printed = redirected_output.getvalue()
            result_val = safe_globals.get("result", None)

            if result_val is not None:
                output = f"{printed}\nResult:\n{result_val}"
            else:
                output = printed or "Code executed successfully."

        except Exception as e:
            output = f"Error: {e}"

        finally:
            np.linalg.cholesky = original_cholesky
            sys.stdout = old_stdout

    return render(request, "analysis/python_console.html", {
        "code": code,
        "output": output
    })
def python_console3(request):
    """
    Python console for the app:
    - Executes Python code
    - Shows printed output
    - Shows 'result' variable if defined
    - Safe handling of scalar correlation in Cholesky
    """
    output = ""
    code = ""

    if request.method == "POST":
        code = request.POST.get("code", "")

        
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()

        
        safe_globals = {"np": np}

        
        original_cholesky = np.linalg.cholesky

        def safe_cholesky(a):
            a = np.array(a)
            if a.ndim == 0:
                a = np.full((2, 2), a)
                np.fill_diagonal(a, 1.0)
            elif a.ndim == 1:
                a = np.diag(a)
            return original_cholesky(a)

        np.linalg.cholesky = safe_cholesky

        try:
            exec(code, safe_globals)
            printed = redirected_output.getvalue()
            result_val = safe_globals.get("result", None)
            if result_val is not None:
                output = f"{printed}\nResult:\n{result_val}"
            else:
                output = printed or "Code executed successfully."
        except Exception as e:
            output = f"Error: {e}"
        finally:
            np.linalg.cholesky = original_cholesky
            sys.stdout = old_stdout  # restore stdout

    return render(request, "analysis/python_console.html", {
        "code": code,
        "output": output
    })

@csrf_exempt
def python_console2(request):
    """
    A simple Python console in the web app.
    - Runs Python code safely
    - Auto-converts scalar correlation to full matrix for simulations
    """
    output = ""
    code = ""

    if request.method == "POST":
        code = request.POST.get("code", "")

        
        safe_globals = {"np": np}

        
        original_cholesky = np.linalg.cholesky

        def safe_cholesky(a):
            a = np.array(a)
            if a.ndim == 0: 
                a = np.full((2, 2), a)
                np.fill_diagonal(a, 1.0)
            elif a.ndim == 1:  
                a = np.diag(a)
            return original_cholesky(a)

        np.linalg.cholesky = safe_cholesky

        try:
            
            exec(code, safe_globals)
            output = safe_globals.get("result", "Code executed successfully.")
        except Exception as e:
            output = f"Error: {e}"
        finally:
            np.linalg.cholesky = original_cholesky  

    return render(request, "analysis/python_console.html", {
        "code": code,
        "output": output
    })




def python_console1(request):
    """
    Поле для ввода Python-кода пользователем.
    """
    result = ""
    error = ""
    code = ""

    if request.method == "POST":
        code = request.POST.get("code", "")

      
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        try:
            
            exec(code, {"np": __import__("numpy")})
            result = buffer.getvalue()
        except Exception as e:
            error = traceback.format_exc()
        finally:
            sys.stdout = old_stdout

    return render(request, "analysis/python_console.html", {
        "code": code,
        "result": result,
        "error": error
    })

def no_code_console(request):
    """
    Страница, где пользователь выбирает параметры визуально.
    """
    context = {}

    if request.method == "POST":
        
        tickers = request.POST.get("tickers", "AAPL,MSFT,GOOGL").split(",")
        n_days = int(request.POST.get("n_days", 252))
        mu = float(request.POST.get("mu", 0.1))
        sigma = float(request.POST.get("sigma", 0.2))
        corr = float(request.POST.get("corr", 0.5))
        model = request.POST.get("model", "gbm")

        from .simulations import correlated_gbm, jump_diffusion
        import numpy as np

        if model == "jump":
            prices = jump_diffusion(len(tickers), n_days, mu, sigma, corr)
        else:
            prices = correlated_gbm(len(tickers), n_days, mu, sigma, corr)

        context.update({
            "tickers": tickers,
            "prices": prices.tolist(),
            "mean_return": round(np.mean(prices[1:]/prices[:-1]-1), 4),
            "vol": round(np.std(prices[1:]/prices[:-1]-1), 4)
        })











from django.core.cache import cache
from django.http import JsonResponse

WATCHLIST = ["AAPL", "MSFT"]  


from django.shortcuts import render
import yfinance as yf

from django.shortcuts import render
import yfinance as yf

from django.shortcuts import render
import yfinance as yf


from django.shortcuts import render
import yfinance as yf




from django.shortcuts import render
import yfinance as yf

def watchlist(request):
    tickers = request.GET.get("tickers", "AAPL,MSFT,GOOGL").split(",")
    prices = {}
    alerts_list = []
    threshold = 150  

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="5d") 
            if not df.empty:
                last_price = round(df['Close'].iloc[-1], 2)
                prices[ticker] = last_price
                if last_price > threshold:
                    alerts_list.append(f"{ticker} @ {last_price} triggered")
            else:
                prices[ticker] = "N/A"
        except Exception as e:
            prices[ticker] = "Error"

    return render(request, "analysis/watchlist.html", {
        "prices": prices,
        "prices_data": prices,
        "alerts": alerts_list,
        "threshold": threshold,
    })

def watchlist6(request):
    tickers = request.GET.get("tickers", "AAPL,MSFT,GOOGL").split(",")
    prices = {}
    alerts_list = []

    for ticker in tickers:
        try:
            df = yf.download(ticker, period="1d", interval="1d", progress=False)
            if not df.empty:
                last_price = round(df['Close'].iloc[-1], 2)
                prices[ticker] = last_price

                
                if last_price > 150:
                    alerts_list.append(f"{ticker} @ {last_price} triggered")
            else:
                prices[ticker] = "N/A"
        except Exception:
            prices[ticker] = "Error"

   
    threshold = 150  

    return render(request, "analysis/watchlist.html", {
        "prices": prices,
        "prices_data": prices,  
        "alerts": alerts_list,
        "threshold": threshold,
    })


def watchlist1(request):
    tickers = request.GET.get("tickers", "AAPL,MSFT,GOOGL").split(",")
    data = {}

    for ticker in tickers:
        try:
            df = yf.download(ticker, period="1d", interval="1d", progress=False)
            if not df.empty:
                data[ticker] = round(df['Close'].iloc[-1], 2)  
            else:
                data[ticker] = "N/A"
        except Exception:
            data[ticker] = "Error"

    return render(request, "analysis/watchlist.html", {
        "prices": data
    })

def watchlist5(request):
    tickers = request.GET.get("tickers", "AAPL,MSFT,GOOGL").split(",")
    data = {}

    for ticker in tickers:
        try:
            df = yf.download(ticker, period="1d", interval="1d", progress=False)
            if not df.empty:
                data[ticker] = round(df['Close'][-1], 2)  
            else:
                data[ticker] = "N/A"
        except Exception:
            data[ticker] = "Error"

    return render(request, "analysis/watchlist.html", {
        "prices": data
    })


from django.shortcuts import render
from .analysis_code import run_analysis_clean
import yfinance as yf
from datetime import datetime
import pandas as pd


SIMULATION_HISTORY = []
from django.shortcuts import render
import yfinance as yf
from datetime import datetime
from .models import AnalysisOutcome
from .analysis_code import run_analysis_clean
import json
@login_required
def dashboard25(request):
    results = None
    live_data = live_yfinance;

    if request.method == "POST":
        tickers = request.POST.get("tickers", "AAPL,MSFT,GOOGL").split(",")
        n_stocks = int(request.POST.get("n_stocks", len(tickers)))
        corr_threshold = float(request.POST.get("corr_threshold", 0.6))

        
        data = yf.download(tickers, period="1mo", interval="1d")['Close']
        live_data = data.to_dict()

        
        results = run_analysis_clean(n_stocks=n_stocks, corr_threshold=corr_threshold)
        results['tickers'] = tickers
        results['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

       
        AnalysisOutcome.objects.create(
            tickers=json.dumps(tickers),
            weights=json.dumps(results.get("weights", [])),
            expected_return=results.get("expected_return", 0.0),
            risk=results.get("risk", 0.0),
            sharpe_ratio=results.get("sharpe_ratio", 0.0),
            bs_sample=json.dumps(results.get("jump_diffusion", {}).get("prices", []))
        )

    history = AnalysisOutcome.objects.order_by("-timestamp")[:20] 

    return render(request, "analysis/dashboard.html", {
        "results": results,
        "live_data": live_data,
        "history": history
    })
from .models import WatchlistItem

def watchlist3(request):
    if request.method == "POST":
        tickers = request.POST.get("tickers", "").split(",")
        for t in tickers:
            t = t.strip().upper()
            if t:
                WatchlistItem.objects.get_or_create(ticker=t)

    items = WatchlistItem.objects.all()
    tickers_list = [item.ticker for item in items]

    
    import yfinance as yf
    prices = {}
    if tickers_list:
        data = yf.download(tickers_list, period="1d", interval="1d")['Close'].iloc[-1]
        for t in tickers_list:
            prices[t] = round(data.get(t, 0), 2)

    return render(request, "analysis/watchlist.html", {
        "watchlist": items,
        "prices": prices
    })


from django.shortcuts import render
from .models import WatchlistAlert
import yfinance as yf


from django.shortcuts import render
from .models import WatchlistAlert
import yfinance as yf

def watchlist4(request):
    alerts_qs = WatchlistAlert.objects.filter(user=request.user)
    alerts = []

    for alert in alerts_qs:
        last_price = None
        triggered = False

        try:
           
            ticker_data = yf.download(
                tickers=alert.ticker,
                period="1d",
                interval="1m",
                progress=False
            )

            if not ticker_data.empty:
                
                if "Close" in ticker_data.columns:
                    last_price = ticker_data["Close"].iloc[-1]
                else:
                    
                    last_price = ticker_data["Close"].iloc[-1].values[0]

                last_price = float(last_price)  
                triggered = last_price >= alert.threshold_percent

        except Exception:
            last_price = None
            triggered = False

        alerts.append({
            "ticker": alert.ticker,
            "threshold_percent": float(alert.threshold_percent),
            "last_price": last_price,
            "triggered": triggered,
        })

    return render(request, "analysis/watchlist.html", {"alerts": alerts})




from .models import Alert, WatchlistItem
import yfinance as yf



from django.shortcuts import render
import yfinance as yf
from .models import Alert, WatchlistItem



from django.shortcuts import render, redirect
import yfinance as yf
from .models import Alert, WatchlistItem

def alerts(request):
    
    if request.method == "POST":
        ticker = request.POST.get("ticker", "").upper()
        threshold = request.POST.get("threshold", "")
        if ticker and threshold:
            try:
                threshold = float(threshold)
                Alert.objects.create(ticker=ticker, threshold=threshold)
            except ValueError:
                pass  

        return redirect("alerts") 

    
    all_alerts = Alert.objects.all()

    
    watchlist_tickers = [item.ticker for item in WatchlistItem.objects.all()]

    
    prices = {}
    triggered = []
    for ticker in watchlist_tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")
            if not hist.empty:
                last_price = hist['Close'].iloc[-1]
                prices[ticker] = last_price
        except Exception:
            prices[ticker] = None

    
    for alert in all_alerts:
        price = prices.get(alert.ticker)
        if price is not None and price >= alert.threshold:
            triggered.append({
                "ticker": alert.ticker,
                "price": round(price, 2),
                "threshold": alert.threshold
            })
            alert.triggered = True
        else:
            alert.triggered = False
        alert.save()

    return render(request, "analysis/alerts.html", {
        "alerts": all_alerts,
        "triggered": triggered,
        "prices": prices,
    })

def alerts3(request):
    if request.method == "POST":
        ticker = request.POST.get("ticker", "").upper()
        threshold = float(request.POST.get("threshold", 0))
        if ticker:
            Alert.objects.create(ticker=ticker, threshold=threshold)

    all_alerts = Alert.objects.all()
    watchlist_tickers = [item.ticker for item in WatchlistItem.objects.all()]

    triggered = []

    if watchlist_tickers:
        try:
            
            prices = {}
            for ticker in watchlist_tickers:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="5d") 
                if not hist.empty:
                    prices[ticker] = hist['Close'].iloc[-1]

            for alert in all_alerts:
                price = prices.get(alert.ticker)
                if price is not None:
                    if price >= alert.threshold:
                        triggered.append({
                            "ticker": alert.ticker,
                            "price": round(price, 2)
                        })
                        alert.triggered = True
                    else:
                        alert.triggered = False
                    alert.save()
        except Exception as e:
            print("Error fetching prices:", e)

    return render(request, "analysis/alerts.html", {
        "alerts": all_alerts,
        "triggered": triggered
    })


def alerts2(request):
    if request.method == "POST":
        ticker = request.POST.get("ticker", "").upper()
        threshold = float(request.POST.get("threshold", 0))
        if ticker:
            Alert.objects.create(ticker=ticker, threshold=threshold)

    all_alerts = Alert.objects.all()
    watchlist_tickers = [item.ticker for item in WatchlistItem.objects.all()]

    triggered = []
    if watchlist_tickers:
        data = yf.download(watchlist_tickers, period="1d", interval="1d")['Close'].iloc[-1]
        for alert in all_alerts:
            price = data.get(alert.ticker)
            if price and price >= alert.threshold:
                triggered.append({
                    "ticker": alert.ticker,
                    "price": round(price, 2)
                })
                alert.triggered = True
                alert.save()

    return render(request, "analysis/alerts.html", {
        "alerts": all_alerts,
        "triggered": triggered
    })
from django.shortcuts import render
import numpy as np
from .models import AnalysisOutcome




import numpy as np
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import AnalysisOutcome

@login_required
def monte_carlo(request):
    context = {}

    if request.method == "POST":
        S0 = float(request.POST.get("S0", 100))
        mu = float(request.POST.get("mu", 0.1))
        sigma = float(request.POST.get("sigma", 0.2))
        T = int(request.POST.get("T", 252))
        I = int(request.POST.get("I", 1000))

        dt = 1 / 252
        prices = np.zeros((T, I))
        prices[0] = S0

        for t in range(1, T):
            Z = np.random.standard_normal(I)
            prices[t] = prices[t - 1] * np.exp(
                (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z
            )

        mean_end = round(prices[-1].mean(), 2)
        std_end = round(prices[-1].std(), 2)

        prices_list = prices.tolist()

        context["mean_end"] = mean_end
        context["std_end"] = std_end
        context["prices"] = prices_list

        
        AnalysisOutcome.objects.create(
            user=request.user,
            tickers=["MonteCarlo_Simulation"],
            weights={},
            expected_return=mu * 100,
            risk=sigma * 100,
            sharpe_ratio=0,

            simulation_data={
                "bs_sample": prices_list,
                "bs_mean": mean_end,
                "bs_std": std_end,
            },

            backtest_data={}
        )

    return render(request, "analysis/monte_carlo.html", context)

def monte_carlo3(request):
    context = {}
    if request.method == "POST":
        
        S0 = float(request.POST.get("S0", 100))
        mu = float(request.POST.get("mu", 0.1))
        sigma = float(request.POST.get("sigma", 0.2))
        T = int(request.POST.get("T", 252))
        I = int(request.POST.get("I", 1000))

        
        dt = 1/252
        prices = np.zeros((T, I))
        prices[0] = S0

        for t in range(1, T):
            Z = np.random.standard_normal(I)
            prices[t] = prices[t-1]*np.exp((mu-0.5*sigma**2)*dt + sigma*np.sqrt(dt)*Z)

        
        context["mean_end"] = round(prices[-1].mean(), 2)
        context["std_end"] = round(prices[-1].std(), 2)
       
        prices_list = prices.tolist()
        context["prices"] = prices_list

       
        AnalysisOutcome.objects.create(
            user=request.user,  
            tickers=json.dumps(["MonteCarlo_Simulation"]),
            bs_sample=json.dumps(prices_list), 
            bs_mean=context["mean_end"],
            bs_std=context["std_end"],
            expected_return=mu * 100, 
            risk=sigma * 100
        )

    return render(request, "analysis/monte_carlo.html", context)
def monte_carlo2(request):
    context = {}
    if request.method == "POST":
        S0 = float(request.POST.get("S0", 100))
        mu = float(request.POST.get("mu", 0.1))
        sigma = float(request.POST.get("sigma", 0.2))
        T = int(request.POST.get("T", 252))
        I = int(request.POST.get("I", 1000))

        dt = 1/252
        prices = np.zeros((T, I))
        prices[0] = S0

        for t in range(1, T):
            Z = np.random.standard_normal(I)
            prices[t] = prices[t-1]*np.exp((mu-0.5*sigma**2)*dt + sigma*np.sqrt(dt)*Z)

        context["prices"] = prices.tolist()
        context["mean_end"] = round(prices[-1].mean(), 2)
        context["std_end"] = round(prices[-1].std(), 2)

        # Save Monte Carlo to database
       # AnalysisOutcome.objects.create(
           # tickers=json.dumps(["MonteCarlo"]),
          #  bs_sample=json.dumps(prices.tolist()),
            #bs_mean=context["mean_end"],
            #bs_std=context["std_end"]
        #)
        
        #results = run_monte_carlo_logic(...) 

        # 2. ИСПРАВЛЕНИЕ: Добавляем user=request.user при сохранении
        AnalysisOutcome.objects.create(
            user=request.user,  # 🔑 Ключевая строка!
            tickers=json.dumps(results.get("tickers", ["MonteCarlo"])), # Чтобы не было пустых строк
            expected_return=results.get("expected_return", 0.0),
            risk=results.get("risk", 0.0),
            sharpe_ratio=results.get("sharpe_ratio", 0.0),
            # Добавьте остальные поля, которые возвращает ваш расчет
        )

    return render(request, "analysis/monte_carlo.html", context)

from django.shortcuts import render


SIMULATION_HISTORY = []

def portfolio(request):
   
    context = {"history": SIMULATION_HISTORY}
    return render(request, "analysis/portfolio.html", context)
@login_required
def dashboard252(request):
    results = None
    live_data = None

    if request.method == "POST":
        tickers = request.POST.get("tickers", "AAPL,MSFT,GOOGL").split(",")
        n_stocks = int(request.POST.get("n_stocks", len(tickers)))
        corr_threshold = float(request.POST.get("corr_threshold", 0.6))

       
        data = yf.download(tickers, period="1mo", interval="1d")['Close']
        live_data = data.to_dict()

        
        results = run_analysis_clean(n_stocks=n_stocks, corr_threshold=corr_threshold)
        results['tickers'] = tickers
        results['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        SIMULATION_HISTORY.append(results)

    return render(request, "analysis/dashboard.html", {
        "results": results,
        "live_data": live_data,
        "history": SIMULATION_HISTORY
    })

from django.shortcuts import render
import numpy as np

def monte_carlo2(request):
    context = {}
    if request.method == "POST":
        S0 = float(request.POST.get("S0", 100))
        mu = float(request.POST.get("mu", 0.1))
        sigma = float(request.POST.get("sigma", 0.2))
        T = int(request.POST.get("T", 252))
        I = int(request.POST.get("I", 1000))

        dt = 1/252
        prices = np.zeros((T, I))
        prices[0] = S0

        for t in range(1, T):
            Z = np.random.standard_normal(I)
            prices[t] = prices[t-1]*np.exp((mu-0.5*sigma**2)*dt + sigma*np.sqrt(dt)*Z)

        context["prices"] = prices.tolist()
        context["mean_end"] = round(prices[-1].mean(), 2)
        context["std_end"] = round(prices[-1].std(), 2)

    return render(request, "analysis/monte_carlo.html", context)

def portfolio2(request):
    
    context = {"history": SIMULATION_HISTORY}
    return render(request, "analysis/portfolio.html", context)


ALERTS = []

def alerts2(request):
    context = {"alerts": ALERTS, "watchlist": WATCHLIST}

    if request.method == "POST":
        ticker = request.POST.get("ticker").upper()
        threshold = float(request.POST.get("threshold", 0))
        ALERTS.append({"ticker": ticker, "threshold": threshold})

    
    import yfinance as yf
    if WATCHLIST:
        data = yf.download(WATCHLIST, period="1d", interval="1d")['Close'].iloc[-1]
        triggered = []
        for alert in ALERTS:
            price = data.get(alert["ticker"], None)
            if price and price >= alert["threshold"]:
                triggered.append({"ticker": alert["ticker"], "price": price})
        context["triggered"] = triggered

    return render(request, "analysis/alerts.html", context)


    return render(request, "analysis/no_code_console.html", context)













from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, "analysis/home.html")



def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = UserCreationForm()

    return render(request, "analysis/register.html", {"form": form})



def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")
    else:
        form = AuthenticationForm()

    return render(request, "analysis/login.html", {"form": form})



def logout_view(request):
    logout(request)
    return redirect("home")


































from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import WatchlistAlert
import yfinance as yf

@login_required
def watchlist5(request):
   
    if request.method == "POST":
        tickers = request.POST.get("tickers")
        threshold = float(request.POST.get("threshold_percent", 0))
        if tickers:
            ticker_list = [t.strip().upper() for t in tickers.split(",") if t.strip()]
            for ticker in ticker_list:
                WatchlistAlert.objects.get_or_create(
                    user=request.user,
                    ticker=ticker,
                    defaults={"threshold_percent": threshold}
                )
        return redirect("watchlist")

    
    alerts = WatchlistAlert.objects.filter(user=request.user)

    
    triggered_alerts = []
    for alert in alerts:
        try:
            data = yf.download(alert.ticker, period="1d", interval="1m", progress=False)
            if not data.empty:
                last_price = data["Close"].iloc[-1]
                alert.last_price = last_price
                change_pct = ((last_price - data["Close"].iloc[0]) / data["Close"].iloc[0]) * 100

               
                if abs(change_pct) >= alert.threshold_percent:
                    alert.triggered = True
                    triggered_alerts.append(f"{alert.ticker}: {last_price:.2f} ({change_pct:.2f}%)")
                else:
                    alert.triggered = False

                alert.save()
        except Exception:
            continue

    return render(request, "analysis/watchlist.html", {
        "alerts": alerts,
        "triggered_alerts": triggered_alerts,
    })

















from django.shortcuts import render
from .ml_model import run_ml_trading

@login_required
def ml_trading_view(request):
    results = run_ml_trading()
    return render(request, "analysis/mltrading.html", results)















from django.shortcuts import render
from .ml_model import run_ml_trading

@login_required
def ml_trading_view(request):

    ticker = request.GET.get("ticker", "AAPL")

    results = run_ml_trading(ticker)

    return render(
        request,
        "analysis/mltrading.html",
        {"results": results}
    )








from .models import SimulationRecord 


def run_analysis_with_save(**kwargs):
   
    results = run_analysis_clean(**kwargs)
    
    
    SimulationRecord.objects.create(
        final_value=results['backtest_final_value'],
        sharpe_ratio=results['backtest_sharpe']
    )
    
    return results


def simulation_view(request):
    
    current_results = run_analysis_with_save(n_stocks=10)
    
    
    history_chart_url = plot_simulation_history()
    
    context = {
        'results': current_results,
        'history_chart': history_chart_url,
    }
    return render(request, 'analysis/simulation_template.html', context)
def simulation_view3(request):
    current_results = run_analysis_with_save(n_stocks=10)
    history_chart_url = plot_simulation_history()
    
  
    forward_returns = current_results.get('alpha_analysis', {}).get('quantile_returns', [])

    context = {
        'results': current_results,
        'history_chart': history_chart_url,
        'forward_returns': forward_returns,
    }
    return render(request, 'simulation_template.html', context)

def simulation_view2(request):
   
    current_results = run_analysis_with_save(n_stocks=10)
    
    
    history_chart_url = plot_simulation_history()
    
    context = {
        'results': current_results,
        'history_chart': history_chart_url,
    }
    return render(request, 'dashboard.html', context)









import io
import base64
import matplotlib.pyplot as plt
from .models import SimulationRecord

def plot_simulation_history():
    
    records = SimulationRecord.objects.all().order_by('timestamp')
    
    if not records.exists():
        return None

    
    values = [r.final_value for r in records]
    simulation_counts = list(range(1, len(values) + 1))

   
    plt.figure(figsize=(10, 5))
    plt.plot(simulation_counts, values, marker='o', linestyle='-', color='#2c3e50', linewidth=2)
    plt.fill_between(simulation_counts, values, alpha=0.2, color='#3498db')
    
    plt.title("Historical Performance Trend (All Simulations)")
    plt.xlabel("Simulation Number")
    plt.ylabel("Final Portfolio Value")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()

  
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()





import yfinance as yf
import pandas as pd
import numpy as np

def run_analysis_real_data(symbols):
    try:
        
        data = yf.download(symbols, period="1y", interval="1d")
        
        if data.empty:
            return {'error': 'Не вдалося отримати дані з Yahoo Finance'}

        
        close_prices = data['Close']

      
        sma_20 = close_prices.rolling(window=20).mean()
        sma_50 = close_prices.rolling(window=50).mean()

        
        first_stock = symbols[0]
        std = close_prices[first_stock].rolling(window=20).std()
        upper_band = sma_20[first_stock] + (std * 2)
        lower_band = sma_20[first_stock] - (std * 2)

        
        ma_chart_base64 = generate_ma_plot(close_prices, sma_20, sma_50)
        bollinger_chart_base64 = generate_bb_plot(close_prices[first_stock], upper_band, lower_band)

        return {
            'ma_chart': ma_chart_base64,
            'bollinger_chart': bollinger_chart_base64,
        }
    except Exception as e:
        return {'error': str(e)}




import io
import base64
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import yfinance as yf
from django.shortcuts import render

import io
import base64
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd

def run_analysis_cleantech(n_stocks=10):
    try:
        
        symbol = "AAPL" 
       
        df = yf.download(symbol, period="6mo", interval="1d", auto_adjust=True)
        
        if df.empty:
            return {'error': "No data found for the ticker."}

        
        if isinstance(df.columns, pd.MultiIndex):
            close_prices = df['Close'][symbol]
        else:
            close_prices = df['Close']

      
        ma20 = close_prices.rolling(window=20).mean()
        std = close_prices.rolling(window=20).std()
        
        upper_band = ma20 + (std * 2)
        lower_band = ma20 - (std * 2)

       
        plt.figure(figsize=(10, 5))
        plt.plot(close_prices.index, close_prices, label='Price', color='black', lw=1)
        plt.plot(ma20.index, ma20, label='MA 20', color='blue', lw=1.5)
        plt.fill_between(close_prices.index, lower_band, upper_band, color='gray', alpha=0.2, label='Bollinger Bands')
        
        plt.title(f"Technical Analysis: {symbol}")
        plt.legend()
        plt.grid(True, alpha=0.2)

      
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        graphic = base64.b64encode(buf.getvalue()).decode('utf-8')

        return {
            'ma_chart': graphic,
            'bollinger_chart': graphic,
        }
    except Exception as e:
      
        return {'error': str(e)}

def technical_analysis_view(request):
   
    results = run_analysis_cleantech(n_stocks=10)
   
    if 'error' in results:
        return render(request, 'analysis/technical_analysis.html', {'error_message': results['error']})

    context = {
        'ma_chart': results.get('ma_chart'),
        'bollinger_chart': results.get('bollinger_chart'),
    }
    
    return render(request, 'analysis/technical_analysis.html', context)


from django.shortcuts import render

def technical_analysis_viewimp(request):
   
    results = run_analysis_clean(n_stocks=10) 
    
   
    context = {
        'ma_chart': results.get('ma_chart'),
        'bollinger_chart': results.get('bollinger_chart'),
    }
    
    return render(request, 'analysis/technical_analysis.html', context)
def technical_analysis_view3(request):
   
    
    
   
    if results is None:
        return render(request, 'error.html', {'message': 'Analysis failed to return data.'})

    context = {
        'ma_chart': results.get('ma_chart'),
        'bollinger_chart': results.get('bollinger_chart'),
    }
    return render(request, 'technical_analysis.html', context)
    #results = run_analysis_clean(n_stocks=10) 

   # context = {
       # 'ma_chart': results.get('ma_chart'),
       # 'bollinger_chart': results.get('bollinger_chart'),
       # 'final_value': results.get('backtest_final_value'),
   # }
    
    #return render(request, 'technical_analysis.html', context)
def technical_analysis_view2(request):
    # Run the logic
    results = run_analysis_clean(n_stocks=10)
    
    return render(request, "analysis/tech_analysis.html", {
        "ma_chart": results["ma_chart"],
        "bollinger_chart": results["bollinger_chart"]
    })





@login_required
def history_view(request):
    
    analyses = AnalysisOutcome.objects.filter(user=request.user).order_by('-timestamp')
    
    return render(request, "analysis/history.html", {
        "analyses": analyses
    })





from django.shortcuts import render
from .analysis_code import run_analysis   

def analysis_results2(request):
    results = run_analysis(
        n_stocks=10,
        corr_threshold=0.6
    )

    return render(request, "analysis/results.html", {
        "results": results
    })



from django.shortcuts import render
from .analysis_code import run_analysis
from .models import AnalysisResult


def analysis_results(request):

    results = run_analysis()

    
    AnalysisResult.objects.create(

        expected_return=results["expected_return"],

        risk=results["risk"],

        bs_mean=results["bs_mean"],

        bs_std=results["bs_std"],

        jd_mean=results["jd_mean"],

        jd_std=results["jd_std"],

        backtest_final_value=results["backtest_final_value"],

        backtest_sharpe=results["backtest_sharpe"],

        backtest_drawdown=results["backtest_drawdown"],

        weights=results["weights"],

        gnn_prediction=results["gnn_prediction"],

        #alpha_analysis=results["alpha_analysis"],

       # ml_alpha_analysis=results["ml_alpha_analysis"],
    )

    return render(request, "analysis/results.html", {
        "results": results
    })


from django.shortcuts import render
from .models import AnalysisResult

def analysis_list_view(request):
    
    records = AnalysisResult.objects.all()
    
    
    count = records.count()
    
    return render(request, 'analysis/results.html', {
        'results': records,
        'total_count': count
    })
@login_required
def analysis_list_view5(request):
    
    results = AnalysisResult2.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'analysis/analysis_list.html', {'results': results})


import json
from django.shortcuts import render
from .models import AnalysisResult

def get_analytics_dashboard(request):
   
    records = AnalysisResult.objects.all().order_by('-created_at')[:20][::-1]

    
    dates = [r.created_at.strftime("%d.%m %H:%M") for r in records]
    returns = [round(r.expected_return, 4) for r in records]
    risks = [round(r.risk, 4) for r in records]
    sharpe = [round(r.backtest_sharpe, 2) for r in records]

    context = {
        'chart_labels': json.dumps(dates),
        'chart_returns': json.dumps(returns),
        'chart_risks': json.dumps(risks),
        'chart_sharpe': json.dumps(sharpe),
        'raw_records': records,
    }
    
    return render(request, 'analysis/templates/analysis/dashboardfre.html', context)



from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import AnalysisResult2

@login_required
def analysis_list_view4(request):
    
    results = AnalysisResult2.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'analysis/analysis_list.html', {'results': results})





def analysis_archive(request):

    results = run_analysis()

    
    AnalysisResult.objects.create(

        expected_return=results["expected_return"],

        risk=results["risk"],

        bs_mean=results["bs_mean"],

        bs_std=results["bs_std"],

        jd_mean=results["jd_mean"],

        jd_std=results["jd_std"],

        backtest_final_value=results["backtest_final_value"],

        backtest_sharpe=results["backtest_sharpe"],

        backtest_drawdown=results["backtest_drawdown"],

        weights=results["weights"],

        gnn_prediction=results["gnn_prediction"],

        #alpha_analysis=results["alpha_analysis"],

        #ml_alpha_analysis=results["ml_alpha_analysis"],
    )

    return render(request, "analysis/archive.html", {
        "results": results
    })



def main_index(request):
    return render(request, 'analysis/main_index.html')














import yfinance as yf

from django.db.models import Avg, Max, Count


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Max, Count
import yfinance as yf
from .models import QuantAnalysis, QuantLab3Result

@login_required
@login_required
def bi_dashboardgttf(request):
  
    user_sims = QuantLab3Result.objects.filter(user=request.user).order_by('-timestamp')
    
 
    stats = user_sims.aggregate(
        avg_mu=Avg('expected_return'),  
        max_mu=Max('expected_return'), 
        avg_var=Avg('risk'),         
        total=Count('id')
    )

    
    spy_yearly_return = 0.15 
    try:
        spy = yf.Ticker("SPY")
        spy_hist = spy.history(period="1y")
        if not spy_hist.empty:
            spy_yearly_return = (spy_hist['Close'].iloc[-1] / spy_hist['Close'].iloc[0]) - 1
    except:
        pass
    
    recent_sims = user_sims[:12][::-1]
    chart_labels = [s.timestamp.strftime("%d.%m") for s in recent_sims]
    
    
    my_returns = [float(s.expected_return or 0) for s in recent_sims] 
    
    market_returns = [round(spy_yearly_return, 4)] * len(my_returns)

    
    max_ret_val = stats['max_mu'] or 0
    diff = max_ret_val - spy_yearly_return

    context = {
        "avg_mu": round((stats['avg_mu'] or 0) * 100, 2),
        "avg_var": round((stats['avg_var'] or 0) * 100, 2),
        "total_sims": stats['total'],
        "max_return": round(max_ret_val * 100, 2),
        "market_return": round(spy_yearly_return * 100, 2),
        "return_diff": round(diff * 100, 2),
        "chart_labels": chart_labels,
        "my_returns": my_returns,
        "market_returns": market_returns,
        "history": user_sims[:5],
    }
    
    return render(request, "analysis/bi_dashboard.html", context)


import json 
from django.shortcuts import render
from django.db.models import Avg, Max, Count
import yfinance as yf
from .models import QuantAnalysis
from django.contrib.auth.decorators import login_required

@login_required
def bi_dashboard5(request):
   
    user_sims = QuantAnalysis.objects.filter(user=request.user).order_by('-timestamp')
    
    
    stress_scenario = request.GET.get('stress_scenario', 'standard')
    
   
    stats = user_sims.aggregate(
        avg_mu=Avg('mu'),
        avg_var=Avg('var_value'),
        avg_sigma=Avg('sigma'),
        max_mu=Max('mu'),
        total=Count('id')
    )

 
    if stats['total'] == 0:
        return render(request, "analysis/bi_dashboard.html", {"no_data": True})


    mu_multiplier = 1.0
    risk_multiplier = 1.0
    scenario_label = "Standard Market"

    if stress_scenario == 'crash':
        mu_multiplier = 0.7
        risk_multiplier = 1.5
        scenario_label = "Market Crash (-30%)"
    elif stress_scenario == 'volatility':
        mu_multiplier = 0.9
        risk_multiplier = 3.0
        scenario_label = "Volatility Spike (x3)"

    
    base_mu = float(stats['avg_mu'] or 0)
    base_sigma = float(stats['avg_sigma'] or 0)
    base_var = float(stats['avg_var'] or 0)
    
    display_avg_mu = base_mu * mu_multiplier
    display_avg_var = base_var * risk_multiplier
    
    
    denominator = (base_sigma * risk_multiplier)
    calculated_sharpe = display_avg_mu / denominator if denominator != 0 else 0

   
    spy_yearly_return = 0.236
    try:
        spy = yf.Ticker("SPY")
        spy_hist = spy.history(period="1y")
        if not spy_hist.empty:
            spy_yearly_return = (spy_hist['Close'].iloc[-1] / spy_hist['Close'].iloc[0]) - 1
    except Exception as e:
        print(f"YFinance error: {e}")

    alpha = display_avg_mu - spy_yearly_return

   
    recent_sims = user_sims[:15]
    chart_data_raw = []
    for s in recent_sims:
        chart_data_raw.append({
            
            'x': round(float(s.sigma or 0) * 100 * risk_multiplier, 2),
            'y': round(float(s.mu or 0) * 100 * mu_multiplier, 2),
            'label': s.timestamp.strftime("%d.%m %H:%M")
        })
    
    
    chart_data_json = json.dumps(chart_data_raw)

    
    context = {
        "total_sims": stats['total'],
        "avg_sharpe": round(calculated_sharpe, 2),
        "max_return": round(float(stats['max_mu'] or 0) * 100 * mu_multiplier, 2),
        "avg_mu_pct": round(display_avg_mu * 100, 2),
        "avg_var_pct": round(display_avg_var * 100, 2),
        "alpha_pct": round(alpha * 100, 2),
        "market_return_pct": round(spy_yearly_return * 100, 2),
        
        "chart_data_js": chart_data_json, # Отдаем как строку!
        "history": user_sims[:10],
        "current_scenario": scenario_label,
        "stress_scenario_slug": stress_scenario,
    }
    
    return render(request, "analysis/bi_dashboard.html", context)
def bi_dashboard(request):
    # Получаем данные пользователя
    user_sims = QuantAnalysis.objects.filter(user=request.user).order_by('-timestamp')
    #user_sims = QuantLab3Result.objects.filter(user=request.user).order_by('-timestamp')
  
    stats = user_sims.aggregate(
        avg_mu=Avg('mu'),
        max_mu=Max('mu'),
        avg_var=Avg('var_value'),
        total=Count('id')
    )

    
    spy_yearly_return = 0.15 
    try:
        spy = yf.Ticker("SPY")
        spy_hist = spy.history(period="1y")
        if not spy_hist.empty:
            spy_yearly_return = (spy_hist['Close'].iloc[-1] / spy_hist['Close'].iloc[0]) - 1
    except:
        pass

    
    recent_sims = user_sims[:12][::-1]
    chart_labels = [s.timestamp.strftime("%d.%m") for s in recent_sims]
    my_returns = [float(s.mu) for s in recent_sims]
    market_returns = [round(spy_yearly_return, 4)] * len(my_returns)

    
    max_ret_val = stats['max_mu'] or 0
    diff = max_ret_val - spy_yearly_return

    context = {
        "avg_mu": round((stats['avg_mu'] or 0) * 100, 2), # в процентах
        "avg_var": round((stats['avg_var'] or 0) * 100, 2),
        "total_sims": stats['total'],
        "max_return": round(max_ret_val * 100, 2),
        "market_return": round(spy_yearly_return * 100, 2),
        "return_diff": round(diff * 100, 2),
        "chart_labels": chart_labels,
        "my_returns": my_returns,
        "market_returns": market_returns,
        "history": user_sims[:5],
    }
    
    return render(request, "analysis/bi_dashboard.html", context)

def bi_dashboard3(request):
    user_sims = QuantAnalysis.objects.filter(user=request.user).order_by('-timestamp')
    
    
    stats = user_sims.aggregate(
        avg_mu=Avg('mu'),
        max_mu=Max('mu'),
        avg_var=Avg('var_value'),
        total=Count('id')
    )

    
    spy = yf.Ticker("SPY")
    spy_hist = spy.history(period="1y")
    spy_yearly_return = 0.15 
    if not spy_hist.empty:
        spy_yearly_return = (spy_hist['Close'].iloc[-1] / spy_hist['Close'].iloc[0]) - 1

    
    recent_sims = user_sims[:12][::-1]
    chart_labels = [s.timestamp.strftime("%d.%m") for s in recent_sims]
    my_returns = [float(s.mu) for s in recent_sims] 
    market_returns = [round(spy_yearly_return, 4)] * len(my_returns)

    context = {
        "avg_mu": round(stats['avg_mu'] or 0, 4),
        "avg_var": round(stats['avg_var'] or 0, 4),
        "total_sims": stats['total'],
        "max_return": round(stats['max_mu'] or 0, 4),
        "market_return": round(spy_yearly_return, 4),
        "chart_labels": chart_labels,
        "my_returns": my_returns,
        "market_returns": market_returns,
        "history": user_sims[:5],
        "return_diff": round((stats['max_mu'] or 0) - spy_yearly_return, 4)
    }
    
    return render(request, "analysis/bi_dashboard.html", context)













def detect_fvgs(df):
    fvgs = []
    
    for i in range(2, len(df)):
        
        if df['Low'].iloc[i] > df['High'].iloc[i-2]:
            zone_top = df['Low'].iloc[i]
            zone_bottom = df['High'].iloc[i-2]
            
           
            tapped = any(df['Low'].iloc[i+1:] <= zone_top)
            
            fvgs.append({
                'time': df.index[i-1],
                'type': 'Bullish',
                'top': round(float(zone_top), 2),
                'bottom': round(float(zone_bottom), 2),
                'is_tapped': tapped
            })
            
       
        elif df['High'].iloc[i] < df['Low'].iloc[i-2]:
            zone_top = df['Low'].iloc[i-2]
            zone_bottom = df['High'].iloc[i]
            
            tapped = any(df['High'].iloc[i+1:] >= zone_bottom)
            
            fvgs.append({
                'time': df.index[i-1],
                'type': 'Bearish',
                'top': round(float(zone_top), 2),
                'bottom': round(float(zone_bottom), 2),
                'is_tapped': tapped
            })
    return fvgs[::-1] 







def fvg_monitor(request):
    ticker_symbol = request.GET.get('ticker', 'BTC-USD')
    interval = request.GET.get('interval', '1h') # 1h, 4h, 1d
    
    try:
       
        data = yf.download(ticker_symbol, period="5d", interval=interval)
        
       
        if hasattr(data.columns, "levels"):
            data.columns = data.columns.get_level_values(0)
            
        all_fvgs = detect_fvgs(data)
        
        
        active_fvgs = [f for f in all_fvgs if not f['is_tapped']]
        tapped_fvgs = [f for f in all_fvgs if f['is_tapped']]
        
    except Exception as e:
        return render(request, 'analysis/fvg_page.html', {'error': str(e)})

    return render(request, 'analysis/fvg_page.html', {
        'ticker': ticker_symbol,
        'active_fvgs': active_fvgs,
        'tapped_fvgs': tapped_fvgs,
        'last_price': round(float(data['Close'].iloc[-1]), 2)
    })







import json
from .models import BIDashboardReport

def save_dashboard_snapshot(request, stats_data):
    
    report = BIDashboardReport.objects.create(
        user=request.user,
        total_simulations=stats_data['total_sims'],
        avg_return=stats_data['avg_mu'],
        avg_risk_var=stats_data['avg_var'],
        market_comparison=stats_data['return_diff'],
       
        chart_data_json=json.dumps({
            'labels': stats_data['chart_labels'],
            'returns': stats_data['my_returns']
        }),
        active_fvg_count=stats_data['active_fvg_count']
    )
    return report.id

















from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import yfinance as yf
import numpy as np
import pandas as pd
from .models import TradeAnalysisRecord
@login_required
def trade_analytics_page(request):
    context = {}
    
    if request.method == "POST":
        try:
            
            tickers_str = request.POST.get("tickers", "AAPL,MSFT,SPY")
            tickers = [t.strip().upper() for t in tickers_str.split(",")]
            capital = float(request.POST.get("capital", 10000))
            raw_risk_pct = request.POST.get("risk_pct", 1) # Сохраняем для БД
            risk_pct = float(raw_risk_pct) / 100 
            
            
            data = yf.download(tickers, period="2y")
            prices = data['Close'].dropna()
            
            if isinstance(prices, pd.Series):
                prices = prices.to_frame()
                
            returns = prices.pct_change().dropna()
            port_returns = returns.mean(axis=1) 
            
            
            wins = port_returns[port_returns > 0]
            losses = port_returns[port_returns < 0]
            
            win_rate = (len(wins) / len(port_returns)) * 100 if len(port_returns) > 0 else 0
            profit_factor = wins.sum() / abs(losses.sum()) if not losses.empty else 0
            
            excess_returns = port_returns - (0.02 / 252)
            sharpe = (excess_returns.mean() / port_returns.std()) * np.sqrt(252) if port_returns.std() != 0 else 0
            
            cum_rets = (1 + port_returns).cumprod()
            peak = cum_rets.cummax()
            dd = (cum_rets - peak) / peak
            max_dd = dd.min() * 100
            
           
            stop_distance = port_returns.std() * 2 
            risk_amount = capital * risk_pct
            risk_size = risk_amount / stop_distance if stop_distance != 0 else 0
            
            tr = pd.concat([
                data['High'] - data['Low'],
                abs(data['High'] - data['Close'].shift()),
                abs(data['Low'] - data['Close'].shift())
            ], axis=1).max(axis=1)
            atr = tr.rolling(14).mean().iloc[-1]
            atr_size = risk_amount / (atr / prices.iloc[-1].mean()) if atr != 0 else 0

           
            record = TradeAnalysisRecord.objects.create(
                user=request.user,
                tickers=tickers_str,
                capital=capital,
                risk_pct=float(raw_risk_pct),
                win_rate=round(win_rate, 2),
                profit_factor=round(profit_factor, 2),
                sharpe_ratio=round(sharpe, 2),
                max_drawdown=round(max_dd, 2),
                risk_based_size=round(risk_size, 2),
                atr_based_size=round(atr_size, 2)
            )

           
            context = {
                "tickers": tickers,
                "win_rate": round(win_rate, 2),
                "profit_factor": round(profit_factor, 2),
                "sharpe": round(sharpe, 2),
                "max_dd": round(max_dd, 2),
                "risk_size": round(risk_size, 2),
                "atr_size": round(atr_size, 2),
                "capital": capital,
                "record_id": record.id,
                "success": True
            }
            return render(request, "analysis/trade_results.html", context)

        except Exception as e:
            return render(request, "analysis/trade_results.html", {"error": str(e)})

  
    history = TradeAnalysisRecord.objects.filter(user=request.user).order_by('-timestamp')[:10]
    return render(request, "analysis/trade_input.html", {"history": history})


@login_required
def trade_trends_page(request):
    ticker = request.GET.get("ticker", "AAPL").upper()
    try:
        
        df = yf.download(ticker, period="1y")
        if df.empty:
            return render(request, "analysis/trade_trends.html", {"error": "No data found"})

        
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()
        
        
        last_close = float(df['Close'].iloc[-1])
        sma_50 = float(df['SMA_50'].iloc[-1])
        sma_200 = float(df['SMA_200'].iloc[-1])
        
        if last_close > sma_50 > sma_200:
            trend_status = "Strong Bullish"
            trend_class = "text-success"
        elif last_close < sma_50 < sma_200:
            trend_status = "Strong Bearish"
            trend_class = "text-danger"
        else:
            trend_status = "Neutral / Transition"
            trend_class = "text-warning"

        
        recent = df.tail(100)
        chart_data = {
            "dates": recent.index.strftime('%Y-%m-%d').tolist(),
            "prices": recent['Close'].round(2).tolist(),
            "sma50": recent['SMA_50'].round(2).tolist(),
            "sma200": recent['SMA_200'].round(2).tolist(),
        }

        return render(request, "analysis/trade_trends.html", {
            "ticker": ticker,
            "status": trend_status,
            "class": trend_class,
            "chart_data": chart_data,
            "last_price": round(last_close, 2)
        })
    except Exception as e:
        return render(request, "analysis/trade_trends.html", {"error": str(e)})






from django.db.models import Avg, Count
from .models import QuantLab3Result, QuantAnalysis, BIDashboardReport
import json

def update_bi_report(user):
    
    lab_data = QuantLab3Result.objects.filter(user=user)
    lab_stats = lab_data.aggregate(
        avg_ret=Avg('expected_return'),
        avg_sh=Avg('sharpe_ratio'),
        total=Count('id')
    )

   
    quant_stats = QuantAnalysis.objects.filter(user=user).aggregate(
        avg_var=Avg('var_value')
    )

   
    history_points = list(lab_data.order_by('timestamp').values_list('expected_return', flat=True)[:10])

   
    report, created = BIDashboardReport.objects.update_or_create(
        user=user,
        defaults={
            'total_simulations': lab_stats['total'] or 0,
            'avg_return': lab_stats['avg_ret'] or 0.0,
            'avg_risk_var': quant_stats['avg_var'] or 0.0,
            'market_comparison': (lab_stats['avg_ret'] or 0.0) - 0.07, 
            'chart_data_json': {
                'labels': [f"Sim {i+1}" for i in range(len(history_points))],
                'datasets': history_points
            },
            'active_fvg_count': 0 
        }
    )
    return report










@login_required
def dashboard_bi_view(request):
    
    report = update_bi_report(request.user)
    
   
    history = QuantLab3Result.objects.filter(user=request.user).order_by('-timestamp')[:10]

    return render(request, "analysis/dashboard_new.html", {
        "report": report,
        "history": history,
        
        "chart_data_js": json.dumps(report.chart_data_json)
    })














import json

@login_required
def quant_lab_bi(request):
    history = QuantAnalysis.objects.filter(user=request.user).order_by('-timestamp')
    
   
    last_res = history.first()
    chart_data = {
        "labels": [],
        "values": []
    }
    
    if last_res:
        
        chart_data["labels"] = ["Risk", "Return", "VaR", "CVaR"]
        chart_data["values"] = [float(last_res.sigma), float(last_res.mu), float(last_res.var_value), float(last_res.cvar_value)]

    context = {
        "history": history,
        "chart_data_json": json.dumps(chart_data), 
    }
    return render(request, "analysis/bi_dashboard.html", context)
















from django.http import JsonResponse
from .models import StockTicker

def stock_analysis_view(request):
    stocks = StockTicker.objects.all().values('symbol', 'last_price', 'prediction')
    return JsonResponse(list(stocks), safe=False)






    
    
from django.http import JsonResponse
from .gnn_engine import get_gnn_predictions 

def stock_analysis_view(request):
    try:
      
        predictions = get_gnn_predictions()
        return JsonResponse({'status': 'success', 'data': predictions}, safe=False)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    
    
    
    
    









from django.shortcuts import render
from .gnn_engine import get_gnn_predictions
import yfinance as yf
import numpy as np  

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import yfinance as yf
import numpy as np
import pandas as pd

from .gnn_engine import get_gnn_predictions 


import json
from .models import GNNAnalysis  

@login_required

def gnn_analytics_page(request):
    default_tickers = "AAPL, MSFT, GOOG, TSLA, NVDA"
    default_formula = "abs(corr) > 0.5"
    
  
    if request.method == 'POST':
        user_input = request.POST.get('tickers', default_tickers)
        graph_formula = request.POST.get('graph_formula', default_formula)
    else:
        user_input = default_tickers
        graph_formula = default_formula

    results = []
    error = None
    tickers = [t.strip().upper() for t in user_input.split(',') if t.strip()]

   
    if request.method == 'POST':
        try:
            
            data = yf.download(tickers, period="1y")['Close']
            if data.empty or len(tickers) < 2:
                error = "Нужно минимум 2 валидных тикера."
            else:
               
                returns = data.pct_change().dropna()
                actual_tickers = returns.columns.tolist()
                mu = returns.mean().values.reshape(-1, 1)
                sigma = returns.std().values.reshape(-1, 1)
                features = np.hstack([mu, sigma])
                corr_matrix = returns.corr().values
                
               
                predictions = get_gnn_predictions(corr_matrix, features, formula=graph_formula)
                
                
                for i, ticker in enumerate(actual_tickers):
                    results.append({
                        'ticker': ticker,
                        'prediction': round(float(predictions[i]), 6),
                        'current_mu': round(float(mu[i][0]), 6)
                    })
                
                
                GNNAnalysis.objects.create(
                    user=request.user,
                    tickers_input=user_input,
                    formula=graph_formula,
                    results_json=results  
                )
        except Exception as e:
            error = f"Ошибка анализа: {str(e)}"

    
    history = GNNAnalysis.objects.filter(user=request.user).order_by('-date')[:5]

    return render(request, "analysis/gnn_page.html", {
        "results": results, 
        "user_input": user_input,
        "graph_formula": graph_formula,
        "history": history,
        "error": error
    })
def gnn_analytics_pageмыпавап(request):
    default_tickers = "AAPL, MSFT, GOOG, TSLA, NVDA"
    default_formula = "abs(corr) > 0.5"
    
    if request.method == 'POST':
        user_input = request.POST.get('tickers', default_tickers)
        graph_formula = request.POST.get('graph_formula', default_formula)
    else:
        user_input = default_tickers
        graph_formula = default_formula
    
    tickers = [t.strip().upper() for t in user_input.split(',') if t.strip()]

    try:
        
        data = yf.download(tickers, period="1y")['Close']
        if data.empty or len(tickers) < 2:
            return render(request, "analysis/gnn_page.html", {
                "error": "Нужно минимум 2 тикера.",
                "user_input": user_input,
                "graph_formula": graph_formula
            })
            
      
        returns = data.pct_change().dropna()
        actual_tickers = returns.columns.tolist()
        mu = returns.mean().values.reshape(-1, 1)
        sigma = returns.std().values.reshape(-1, 1)
        features = np.hstack([mu, sigma])
        corr_matrix = returns.corr().values
        
        
        predictions = get_gnn_predictions(corr_matrix, features, formula=graph_formula)
        
        
        results = []
        for i, ticker in enumerate(actual_tickers):
            results.append({
                'ticker': ticker,
                'prediction': round(float(predictions[i]), 6),
                'current_mu': round(float(mu[i][0]), 6)
            })
        
        
        if request.method == 'POST':
            GNNAnalysis.objects.create(
                user=request.user,
                tickers_input=user_input,
                formula=graph_formula,
                results_json=results  
            )
       
        history = GNNAnalysis.objects.filter(user=request.user).order_by('-date')[:5]
            
        return render(request, "analysis/gnn_page.html", {
            "results": results, 
            "user_input": user_input,
            "graph_formula": graph_formula,
            "history": history  
        })
        
    except Exception as e:
        return render(request, "analysis/gnn_page.html", {
            "error": f"Ошибка: {str(e)}",
            "user_input": user_input,
            "graph_formula": graph_formula
        })

def gnn_analytics_pageоченьважно(request):
    default_tickers = "AAPL, MSFT, GOOG, TSLA, NVDA"
    default_formula = "abs(corr) > 0.5"
    
    if request.method == 'POST':
        user_input = request.POST.get('tickers', default_tickers)
        graph_formula = request.POST.get('graph_formula', default_formula)
    else:
        user_input = default_tickers
        graph_formula = default_formula
    
    tickers = [t.strip().upper() for t in user_input.split(',') if t.strip()]

    try:
        
        data = yf.download(tickers, period="1y")['Close']
        if data.empty or len(tickers) < 2:
            return render(request, "analysis/gnn_page.html", {
                "error": "Нужно минимум 2 тикера.",
                "user_input": user_input,
                "graph_formula": graph_formula
            })
            
        
        returns = data.pct_change().dropna()
        actual_tickers = returns.columns.tolist()
        mu = returns.mean().values.reshape(-1, 1)
        sigma = returns.std().values.reshape(-1, 1)
        features = np.hstack([mu, sigma])
        corr_matrix = returns.corr().values
        
       
        predictions = get_gnn_predictions(corr_matrix, features, formula=graph_formula)
        
       
        results = []
        for i, ticker in enumerate(actual_tickers):
            results.append({
                'ticker': ticker,
                'prediction': round(float(predictions[i]), 6),
                'current_mu': round(float(mu[i][0]), 6)
            })
            
        return render(request, "analysis/gnn_page.html", {
            "results": results, 
            "user_input": user_input,
            "graph_formula": graph_formula
        })
        
    except Exception as e:
        return render(request, "analysis/gnn_page.html", {
            "error": f"Ошибка: {str(e)}",
            "user_input": user_input,
            "graph_formula": graph_formula
        })
@login_required
def gnn_analytics_page3(request):
    default_tickers = "AAPL, MSFT, GOOG, TSLA, NVDA"
    
    default_formula = "abs(corr) > 0.5"
    
    if request.method == 'POST':
        user_input = request.POST.get('tickers', default_tickers)
        graph_formula = request.POST.get('graph_formula', default_formula)
    else:
        user_input = default_tickers
        graph_formula = default_formula
    
    tickers = [t.strip().upper() for t in user_input.split(',') if t.strip()]

    try:
       
        data = yf.download(tickers, period="1y")['Close']
        if data.empty or len(tickers) < 2:
            return render(request, "analysis/gnn_page.html", {
                "error": "Нужно минимум 2 валидных тикера для построения графа.",
                "user_input": user_input,
                "graph_formula": graph_formula
            })
            
        
        returns = data.pct_change().dropna()
        actual_tickers = returns.columns.tolist()
        
        mu = returns.mean().values.reshape(-1, 1)
        sigma = returns.std().values.reshape(-1, 1)
        features = np.hstack([mu, sigma])
        corr_matrix = returns.corr().values
        
        
        predictions = get_gnn_predictions(corr_matrix, features, formula=graph_formula)
        
        
        results = []
        for i, ticker in enumerate(actual_tickers):
            results.append({
                'ticker': ticker,
                'prediction': round(float(predictions[i]), 6),
                'current_mu': round(float(mu[i][0]), 6)
            })
            
        return render(request, "analysis/gnn_page.html", {
            "results": results, 
            "user_input": user_input,
            "graph_formula": graph_formula 
        })
        
    except Exception as e:
        return render(request, "analysis/gnn_page.html", {
            "error": f"Ошибка при расчете: {str(e)}",
            "user_input": user_input,
            "graph_formula": graph_formula
        })
def gnn_analytics_page2(request):
    default_tickers = "AAPL, MSFT, GOOG, TSLA, NVDA"
    
    user_input = request.POST.get('tickers', default_tickers) if request.method == 'POST' else default_tickers
    
    tickers = [t.strip().upper() for t in user_input.split(',') if t.strip()]

    try:
        
        data = yf.download(tickers, period="1y")['Close']
        if data.empty or len(tickers) < 2:
            return render(request, "analysis/gnn_page.html", {
                "error": "Нужно минимум 2 валидных тикера для построения графа.",
                "user_input": user_input
            })
            
        
        returns = data.pct_change().dropna()
        
        
        actual_tickers = returns.columns.tolist()
        
        mu = returns.mean().values.reshape(-1, 1)
        sigma = returns.std().values.reshape(-1, 1)
        features = np.hstack([mu, sigma])
        corr_matrix = returns.corr().values
        
       
        predictions = get_gnn_predictions(corr_matrix, features)
        
        
        results = []
        for i, ticker in enumerate(actual_tickers):
            results.append({
                'ticker': ticker,
                'prediction': round(float(predictions[i]), 6),
                'current_mu': round(float(mu[i][0]), 6)
            })
            
        return render(request, "analysis/gnn_page.html", {
            "results": results, 
            "user_input": user_input
        })
        
    except Exception as e:
        return render(request, "analysis/gnn_page.html", {
            "error": f"Ошибка при расчете: {str(e)}",
            "user_input": user_input
        })
 
from .models import Company, GNNPrediction

def save_predictions_to_db(results):
    for item in results:
       
        company, created = Company.objects.get_or_create(ticker=item['ticker'])
        
        
        GNNPrediction.objects.create(
            company=company,
            current_mu=item['current_mu'],
            current_sigma=item.get('sigma', 0),
            predicted_return=item['prediction']
        )
 
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .gnn_engine import get_gnn_predictions

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
def access_denied_view(request):
    """Страница для неавторизованных пользователей"""
    return render(request, 'analysis/access_denied.html')   
    

