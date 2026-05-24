# yourapp/ml_model.py


import matplotlib
matplotlib.use("Agg")  

import matplotlib.pyplot as plt






import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler


def run_ml_trading():

   
    np.random.seed(42)
    n_days = 500
    dt = 1/252
    prices = [100]

    for _ in range(n_days-1):
        prices.append(
            prices[-1] * np.exp((0.08 - 0.5*0.2**2)*dt + 0.2*np.sqrt(dt)*np.random.randn())
        )

    df = pd.DataFrame({"price": prices})

    
    df["return_1"] = df["price"].pct_change(1)
    df["return_5"] = df["price"].pct_change(5)
    df["ma_5"] = df["price"].rolling(5).mean()
    df["ma_20"] = df["price"].rolling(20).mean()
    df["ma_ratio"] = df["ma_5"] / df["ma_20"]
    df["target"] = df["price"].pct_change().shift(-1)

    df = df.dropna()

    split = int(len(df)*0.7)
    train = df.iloc[:split]
    test = df.iloc[split:]

    X_train = train[["return_1","return_5","ma_ratio"]]
    y_train = train["target"]

    X_test = test[["return_1","return_5","ma_ratio"]]
    y_test = test["target"]

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    
    model = RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)

    
    signals = np.where(preds > 0, 1, -1)
    strategy_returns = signals * y_test.values
    equity = (1 + strategy_returns).cumprod()

    sharpe = np.mean(strategy_returns)/np.std(strategy_returns)*np.sqrt(252)
    final_value = equity[-1]

    
    plt.figure(figsize=(8,4))
    plt.plot(equity)
    plt.title("ML Trading Equity Curve")

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    plt.close()
    buffer.seek(0)

    image_base64 = base64.b64encode(buffer.read()).decode()

    return {
        "sharpe": round(sharpe,2),
        "final_value": round(float(final_value),2),
        "equity_img": image_base64
    }



































import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import yfinance as yf

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler


def run_ml_trading(ticker="AAPL"):

    try:
        df = yf.download(ticker, start="2018-01-01", progress=False)

        if df.empty:
            return {"error": "No data found for ticker"}

        df = df[["Close"]].rename(columns={"Close": "price"})
        df.dropna(inplace=True)

        
        df["return_1"] = df["price"].pct_change(1)
        df["return_5"] = df["price"].pct_change(5)
        df["return_10"] = df["price"].pct_change(10)

        df["ma_5"] = df["price"].rolling(5).mean()
        df["ma_20"] = df["price"].rolling(20).mean()
        df["ma_ratio"] = df["ma_5"] / df["ma_20"]

        df["volatility_10"] = df["return_1"].rolling(10).std()

        df["target"] = df["price"].pct_change().shift(-1)

        df.dropna(inplace=True)

        split = int(len(df) * 0.7)

        train = df.iloc[:split]
        test = df.iloc[split:]

        features = [
            "return_1", "return_5", "return_10",
            "ma_ratio", "volatility_10"
        ]

        X_train = train[features]
        y_train = train["target"]

        X_test = test[features]
        y_test = test["target"]

        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

        
        model = RandomForestRegressor(
            n_estimators=200,
            max_depth=6,
            random_state=42
        )

        model.fit(X_train, y_train)
        preds = model.predict(X_test)

        
        signals = np.where(preds > 0, 1, -1)

        strategy_returns = signals * y_test.values

        cost = 0.0005
        turnover = np.abs(np.diff(signals, prepend=signals[0]))
        strategy_returns -= cost * turnover

        equity = (1 + strategy_returns).cumprod()

        sharpe = (
            np.mean(strategy_returns)
            / np.std(strategy_returns)
            * np.sqrt(252)
        )

        final_value = equity[-1]

 
        
        plt.figure(figsize=(8, 4))
        plt.plot(test.index, equity)
        plt.title(f"ML Strategy – {ticker}")
        plt.xlabel("Date")
        plt.ylabel("Equity")

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        plt.close()
        buffer.seek(0)

        image_base64 = base64.b64encode(buffer.read()).decode()

        return {
            "ticker": ticker,
            "sharpe": round(float(sharpe), 2),
            "final_value": round(float(final_value), 2),
            "equity_img": image_base64
        }

    except Exception as e:
        return {"error": str(e)}