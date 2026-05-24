

import numpy as np
import yfinance as yf
import pandas as pd



#попытка ноу-код и кода

# analysis/simulations.py
import numpy as np

def correlated_gbm(n_assets, n_days, mu, sigma, corr):
    cov = np.outer(sigma, sigma) * corr
    L = np.linalg.cholesky(cov)
    dt = 1/252
    prices = np.zeros((n_days, n_assets))
    prices[0] = 100  # initial prices
    for t in range(1, n_days):
        z = np.random.normal(size=n_assets)
        prices[t] = prices[t-1] * np.exp(mu*dt + np.dot(L, z)*np.sqrt(dt))
    return prices

def jump_diffusion(n_assets, n_days, mu, sigma, corr, lam=0.3, mu_j=-0.2, delta_j=0.1):
    prices = correlated_gbm(n_assets, n_days, mu, sigma, corr)
    jumps = np.random.poisson(lam=lam, size=prices.shape)
    jump_sizes = np.random.normal(mu_j, delta_j, size=prices.shape)
    prices *= (1 + jumps * jump_sizes)
    return prices
















def yahoo_returns(tickers, period="3y"):
    """
    Download historical data from Yahoo Finance
    and compute returns, mean, vol, correlation
    """
    data = yf.download(
        tickers,
        period=period,
        auto_adjust=True,
        progress=False
    )["Close"]

    returns = data.pct_change().dropna()

    return {
        "returns": returns,
        "mu": returns.mean().values,
        "sigma": returns.std().values,
        "corr": returns.corr().values,
    }


def correlated_gbm(
    n_assets,
    n_days,
    mu,
    sigma,
    corr,
    s0=100
):
    dt = 1 / 252
    prices = np.zeros((n_days, n_assets))
    prices[0] = s0

    L = np.linalg.cholesky(corr)

    for t in range(1, n_days):
        z = L @ np.random.normal(size=n_assets)
        prices[t] = prices[t-1] * np.exp(
            (mu - 0.5 * sigma**2) * dt +
            sigma * np.sqrt(dt) * z
        )

    return prices


def jump_diffusion(
    n_assets,
    n_days,
    mu,
    sigma,
    corr,
    lambda_jump=0.3,
    mu_jump=-0.2,
    sigma_jump=0.1,
    s0=100
):
    dt = 1 / 252
    prices = np.zeros((n_days, n_assets))
    prices[0] = s0

    L = np.linalg.cholesky(corr)

    for t in range(1, n_days):
        z = L @ np.random.normal(size=n_assets)

        jumps = np.random.poisson(lambda_jump * dt, n_assets)
        jump_sizes = jumps * np.random.normal(
            mu_jump, sigma_jump, n_assets
        )

        prices[t] = prices[t-1] * np.exp(
            (mu - 0.5 * sigma**2) * dt +
            sigma * np.sqrt(dt) * z +
            jump_sizes
        )

    return prices





















import numpy as np

def generate_price_series(
    n_assets,
    n_days,
    mu=0.1,
    sigma=0.2,
    s0=100
):
    dt = 1 / 252
    prices = np.zeros((n_days, n_assets))
    prices[0] = s0

    for t in range(1, n_days):
        z = np.random.normal(size=n_assets)
        prices[t] = prices[t-1] * np.exp(
            (mu - 0.5 * sigma**2) * dt +
            sigma * np.sqrt(dt) * z
        )

    return prices























import numpy as np


def jump_diffusion(
    n_assets,
    n_days,
    mu,
    sigma,
    corr,
    lambda_jump=0.3,
    mu_jump=-0.2,
    sigma_jump=0.1,
    s0=100
):
    dt = 1 / 252

    mu = np.array(mu)
    sigma = np.array(sigma)
    L = np.linalg.cholesky(corr)

    prices = np.zeros((n_days, n_assets))
    prices[0] = s0

    for t in range(1, n_days):
        z = L @ np.random.normal(size=n_assets)

        jumps = np.random.poisson(lambda_jump * dt, n_assets)
        jump_sizes = jumps * np.random.normal(mu_jump, sigma_jump, n_assets)

        prices[t] = prices[t-1] * np.exp(
            (mu - 0.5 * sigma**2) * dt +
            sigma * np.sqrt(dt) * z +
            jump_sizes
        )

    return prices




def correlated_gbm(
    n_assets,
    n_days,
    mu,
    sigma,
    corr,
    s0=100
):
    dt = 1 / 252

    mu = np.array(mu)
    sigma = np.array(sigma)

    # Cholesky
    L = np.linalg.cholesky(corr)

    prices = np.zeros((n_days, n_assets))
    prices[0] = s0

    for t in range(1, n_days):
        z = np.random.normal(size=n_assets)
        correlated_z = L @ z

        prices[t] = prices[t-1] * np.exp(
            (mu - 0.5 * sigma**2) * dt +
            sigma * np.sqrt(dt) * correlated_z
        )

    return prices
