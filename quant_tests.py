import numpy as np

def var_cvar(returns, alpha=0.95):
    r = np.sort(returns)
    idx = int((1 - alpha) * len(r))
    return float(r[idx]), float(r[:idx].mean())

def hit_rate(returns):
    return float((returns > 0).mean())

def max_dd(equity):
    peak = np.maximum.accumulate(equity)
    dd = (equity - peak) / peak
    return float(dd.min())
