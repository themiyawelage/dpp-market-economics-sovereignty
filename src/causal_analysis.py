"""Causal-structure audit and omitted-confounding sensitivity analysis.

The DAG makes assumptions explicit. Because the repository does not contain a
DPP-adoption treatment or the full adjustment set, the module deliberately does
not label observational associations as identified DPP causal effects.
"""
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import statsmodels.api as sm

from src.config import FIGURES, PROCESSED, TABLES
from src.io_utils import as_float, read_csv, write_csv


def _series(rows, year):
    return {r["country"]: as_float(r["value"]) for r in rows if int(r["year"]) == year and not r["country"].startswith("European Union") and as_float(r["value"]) is not None}


def _digital(rows, year):
    return {r["country"]: as_float(r["value"]) for r in rows if int(r["year"]) == year and r["size_class"] == "small_10_49" and r["intensity"] == "basic_or_above" and r["version"] == "v4" and not r["country"].startswith("European Union") and as_float(r["value"]) is not None}


def _robustness_value(t_stat, df, q=1.0):
    # Equal-strength omitted-confounder robustness value following the standard
    # partial-R2 sensitivity parameterization. It is descriptive, not proof of identification.
    f_q = q * abs(float(t_stat)) / np.sqrt(float(df))
    f2 = f_q ** 2
    return 0.5 * (np.sqrt(f2 ** 2 + 4 * f2) - f2)


def main():
    nodes = [
        "Economic development", "Industrial structure", "Environmental policy",
        "Digital capability", "DPP implementation capacity", "Information quality / lower frictions",
        "Repair / reuse / recycling activity", "Circular material use",
        "Provider dependence", "Operational digital sovereignty"
    ]
    edges = [
        ("Economic development", "Digital capability"),
        ("Economic development", "Circular material use"),
        ("Industrial structure", "Digital capability"),
        ("Industrial structure", "Circular material use"),
        ("Environmental policy", "DPP implementation capacity"),
        ("Environmental policy", "Circular material use"),
        ("Digital capability", "DPP implementation capacity"),
        ("DPP implementation capacity", "Information quality / lower frictions"),
        ("Information quality / lower frictions", "Repair / reuse / recycling activity"),
        ("Repair / reuse / recycling activity", "Circular material use"),
        ("Digital capability", "Provider dependence"),
        ("DPP implementation capacity", "Provider dependence"),
        ("Provider dependence", "Operational digital sovereignty"),
        ("DPP implementation capacity", "Operational digital sovereignty"),
    ]
    write_csv(TABLES / "causal_dag_edges.csv", [{"source": a, "target": b} for a, b in edges], ["source", "target"])

    audit = [
        {"construct": "Digital capability", "role": "Observed exposure/proxy", "observed_in_repository": "yes", "measure": "DII Version 4"},
        {"construct": "DPP implementation capacity", "role": "Mediator", "observed_in_repository": "no", "measure": "conceptual"},
        {"construct": "Circular material use", "role": "Observed outcome/context", "observed_in_repository": "yes", "measure": "Eurostat circular material use rate"},
        {"construct": "Economic development", "role": "Potential confounder", "observed_in_repository": "no", "measure": "not included"},
        {"construct": "Industrial structure", "role": "Potential confounder", "observed_in_repository": "no", "measure": "not included"},
        {"construct": "Environmental policy", "role": "Potential confounder", "observed_in_repository": "no", "measure": "not included"},
        {"construct": "Provider dependence", "role": "Sovereignty mechanism", "observed_in_repository": "no", "measure": "theoretical mechanism"},
    ]
    write_csv(TABLES / "causal_identification_audit.csv", audit, ["construct", "role", "observed_in_repository", "measure"])

    circular = read_csv(PROCESSED / "circularity_long.csv")
    digital = read_csv(PROCESSED / "digital_intensity_long.csv")
    circ24, dii24 = _series(circular, 2024), _digital(digital, 2024)
    common = sorted(set(circ24) & set(dii24))
    y = np.asarray([circ24[c] for c in common])
    x = np.asarray([dii24[c] for c in common])
    model = sm.OLS(y, sm.add_constant(x)).fit()
    t = model.tvalues[1]
    df = model.df_resid
    partial_r2 = float(t**2 / (t**2 + df))
    rv = float(_robustness_value(t, df))
    sens = [{
        "relationship": "small_basic_dii_2024_to_circularity_2024",
        "n": len(common),
        "ols_beta": float(model.params[1]),
        "classical_t": float(t),
        "df_resid": float(df),
        "partial_r2_exposure_outcome": partial_r2,
        "equal_strength_robustness_value_to_zero": rv,
        "interpretation": "Sensitivity diagnostic only; causal identification is not established because key confounders and DPP adoption are unobserved.",
    }]
    write_csv(TABLES / "causal_sensitivity.csv", sens, list(sens[0]))

    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    pos = {
        "Economic development": (-3.2, 2.0),
        "Industrial structure": (-3.2, 0.6),
        "Environmental policy": (-3.2, -0.8),
        "Digital capability": (-1.2, 1.6),
        "DPP implementation capacity": (0.6, 1.2),
        "Information quality / lower frictions": (2.5, 1.2),
        "Repair / reuse / recycling activity": (4.4, 1.2),
        "Circular material use": (6.2, 1.2),
        "Provider dependence": (0.7, -1.2),
        "Operational digital sovereignty": (3.0, -1.2),
    }
    labels = {
        "Economic development": "Economic\ndevelopment",
        "Industrial structure": "Industrial\nstructure",
        "Environmental policy": "Environmental\npolicy",
        "Digital capability": "Digital\ncapability",
        "DPP implementation capacity": "DPP implementation\ncapacity",
        "Information quality / lower frictions": "Information quality /\nlower frictions",
        "Repair / reuse / recycling activity": "Repair / reuse /\nrecycling activity",
        "Circular material use": "Circular\nmaterial use",
        "Provider dependence": "Provider\ndependence",
        "Operational digital sovereignty": "Operational digital\nsovereignty",
    }
    fig, ax = plt.subplots(figsize=(12, 5.5))
    nx.draw_networkx_nodes(G, pos, node_size=1800, ax=ax)
    nx.draw_networkx_edges(
        G, pos, arrows=True, arrowstyle="-|>", arrowsize=18, width=1.0,
        min_source_margin=22, min_target_margin=22, ax=ax
    )
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=7.2, ax=ax)
    ax.set_title("Causal structure for DPP capability, circularity, and operational sovereignty")
    ax.set_xlim(-4.2, 7.0)
    ax.set_ylim(-2.1, 2.8)
    ax.axis("off")
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(FIGURES / f"fig22_causal_dag.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    return audit, sens


if __name__ == "__main__":
    main()
