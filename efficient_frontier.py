import numpy as np
import matplotlib.pyplot as plt
import io, base64
from scipy.optimize import minimize

def efficient_frontier(mu, cov, n=40):
    risks, rets = [], []

    for target in np.linspace(mu.min(), mu.max(), n):
        cons = (
            {"type": "eq", "fun": lambda w: w.sum() - 1},
            {"type": "eq", "fun": lambda w: w @ mu - target},
        )
        bounds = [(0,1)] * len(mu)

        res = minimize(lambda w: w @ cov @ w,
                       np.ones(len(mu))/len(mu),
                       bounds=bounds,
                       constraints=cons)

        if res.success:
            risks.append(np.sqrt(res.fun))
            rets.append(target)

    return risks, rets


def plot_frontier(risk, ret):
    plt.figure(figsize=(6,4))
    plt.plot(risk, ret)
    plt.xlabel("Risk")
    plt.ylabel("Return")
    plt.title("Efficient Frontier")

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    return base64.b64encode(buf.getvalue()).decode()
