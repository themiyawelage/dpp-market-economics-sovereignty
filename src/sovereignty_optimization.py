"""Scenario-based multi-objective optimization for DPP infrastructure design.

This is a theoretical decision model, not an empirical estimate of observed DPP
providers. All quantities are normalized to [0, 1]. The model traces the Pareto
trade-off between implementation effort and operational-sovereignty risk.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

from src.config import FIGURES, TABLES
from src.io_utils import write_csv


def implementation_effort(x):
    # Increasing convex effort for interoperability, substitutability, resilience,
    # and portability, plus effort to engineer lower switching frictions.
    INT, SUB, SC, RES, PORT = x
    return 0.22 * INT**2 + 0.18 * SUB**2 + 0.14 * (1 - SC)**2 + 0.24 * RES**2 + 0.22 * PORT**2


def sovereignty_risk(x):
    INT, SUB, SC, RES, PORT = x
    return 0.24 * (1 - INT) + 0.24 * (1 - SUB) + 0.20 * SC + 0.18 * (1 - RES) + 0.14 * (1 - PORT)


def optimize_for_lambda(lam):
    def obj(x):
        return implementation_effort(x) + lam * sovereignty_risk(x)
    x0 = np.array([0.7, 0.7, 0.3, 0.7, 0.7])
    bounds = [(0, 1)] * 5
    # Minimum technical safeguards: DPP infrastructure must remain at least moderately interoperable/portable/resilient.
    constraints = [
        {"type": "ineq", "fun": lambda x: x[0] - 0.50},
        {"type": "ineq", "fun": lambda x: x[3] - 0.50},
        {"type": "ineq", "fun": lambda x: x[4] - 0.50},
    ]
    res = minimize(obj, x0, method="SLSQP", bounds=bounds, constraints=constraints, options={"ftol": 1e-12, "maxiter": 1000})
    if not res.success:
        raise RuntimeError(res.message)
    return res.x, implementation_effort(res.x), sovereignty_risk(res.x)


def main():
    lambdas = np.geomspace(0.05, 20.0, 41)
    rows = []
    for lam in lambdas:
        x, effort, risk = optimize_for_lambda(float(lam))
        rows.append({
            "sovereignty_weight_lambda": float(lam),
            "interoperability_INT": float(x[0]),
            "provider_substitutability_SUB": float(x[1]),
            "switching_cost_SC": float(x[2]),
            "operational_resilience_RES": float(x[3]),
            "data_portability_PORT": float(x[4]),
            "normalized_implementation_effort": float(effort),
            "normalized_sovereignty_risk": float(risk),
        })
    write_csv(TABLES / "sovereignty_optimization_frontier.csv", rows, list(rows[0]))

    effort = [r["normalized_implementation_effort"] for r in rows]
    risk = [r["normalized_sovereignty_risk"] for r in rows]
    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    ax.plot(effort, risk, marker="o", markersize=3)
    ax.set_xlabel("Normalized implementation effort")
    ax.set_ylabel("Normalized operational-sovereignty risk")
    ax.set_title("Scenario-based DPP sovereignty frontier")
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(FIGURES / f"fig23_sovereignty_optimization_frontier.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    return rows


if __name__ == "__main__":
    main()
