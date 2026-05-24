import numpy as np

STRESS_SCENARIOS = {
    "2008": {"mu_shift": -0.4, "sigma_mult": 2.5},
    "covid": {"mu_shift": -0.3, "sigma_mult": 3.0},
    "rate_shock": {"mu_shift": -0.2, "sigma_mult": 1.8},
}

def apply_stress(mu, sigma, scenario):
    stress = STRESS_SCENARIOS[scenario]
    mu_stressed = mu + stress["mu_shift"] * abs(mu)
    sigma_stressed = sigma * stress["sigma_mult"]
    return mu_stressed, sigma_stressed
