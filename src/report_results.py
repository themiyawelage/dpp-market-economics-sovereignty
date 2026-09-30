import json

from src.config import MODELS, REPORTS, TABLES
from src.io_utils import read_csv


def _fmt(value, digits=3):
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


def main():
    desc = read_csv(TABLES / "descriptive_statistics.csv")
    corr = read_csv(TABLES / "correlations_2024.csv")
    gaps = read_csv(TABLES / "sme_digital_gap.csv")
    reg = read_csv(TABLES / "regression_results.csv")
    robust = read_csv(TABLES / "robustness_checks.csv")
    clusters = read_csv(TABLES / "country_clusters_2024.csv")
    concentration = read_csv(TABLES / "trade_market_concentration.csv")
    dispersion = read_csv(TABLES / "circularity_dispersion.csv")
    structure_assoc = read_csv(TABLES / "market_structure_associations.csv")

    bayes = read_csv(TABLES / "bayesian_posterior_summary.csv")
    bayes_fit = read_csv(TABLES / "bayesian_model_fit.csv")
    causal_sens = read_csv(TABLES / "causal_sensitivity.csv")
    frontier = read_csv(TABLES / "sovereignty_optimization_frontier.csv")
    target = next(r for r in corr if r["variable_x"] == "small_dii" and r["variable_y"] == "circularity")
    largest_gaps = gaps[:5]
    smallest_gaps = sorted(gaps, key=lambda r: float(r["large_minus_small_gap"]))[:5]
    lines = [
        "# Empirical Results",
        "",
        "## Data coverage",
        "",
        "The analysis combines Eurostat circular material use, enterprise digital intensity, and extra-EU recyclable raw-material imports. Circularity covers 2015–2024, trade covers 2016–2025, and DII Version 4 provides comparable basic-intensity observations for 2022 and 2024 across firm-size groups.",
        "",
        "## Descriptive evidence",
        "",
    ]
    for row in desc:
        lines.append(f"- {row['variable']}: n={row['n']}, mean={_fmt(row['mean'],2)}, median={_fmt(row['median'],2)}, min={_fmt(row['min'],2)}, max={_fmt(row['max'],2)}.")
    lines += [
        "",
        "## Digital readiness and circularity",
        "",
        f"Across EU countries in 2024, the Pearson correlation between the share of small enterprises with at least basic digital intensity and the circular material use rate is {_fmt(target['pearson_r'])} (p={_fmt(target['pearson_p'])}). The Spearman rank correlation is {_fmt(target['spearman_rho'])} (p={_fmt(target['spearman_p'])}).",
        f"A 10,000-draw nonparametric bootstrap gives a 95% interval of [{_fmt(robust[0]['bootstrap_ci_low'])}, {_fmt(robust[0]['bootstrap_ci_high'])}] for the Pearson correlation.",
        "",
        "## Firm-size digital divide",
        "",
        "Largest large-minus-small digital intensity gaps in 2024:",
    ]
    lines += [f"- {r['country']}: {_fmt(r['large_minus_small_gap'],2)} percentage points." for r in largest_gaps]
    lines += ["", "Smallest gaps:"]
    lines += [f"- {r['country']}: {_fmt(r['large_minus_small_gap'],2)} percentage points." for r in smallest_gaps]
    lines += ["", "## Regression evidence", ""]
    for row in reg:
        if row["term"] != "const":
            lines.append(f"- {row['model']} / {row['term']}: beta={_fmt(row['coef'])}, robust SE={_fmt(row['std_err_hc3'])}, p={_fmt(row['p'])}, 95% CI [{_fmt(row['ci_low'])}, {_fmt(row['ci_high'])}], R2={_fmt(row['r2'])}.")
    counts = {}
    for row in clusters:
        counts[row["cluster"]] = counts.get(row["cluster"], 0) + 1
    latest_conc = concentration[-1]
    first_conc = concentration[0]
    assoc = structure_assoc[0]
    lines += [
        "", "## Market structure", "",
        f"The top-four country share of extra-EU recyclable raw-material imports changed from {_fmt(float(first_conc['top4_share']) * 100,2)}% in {first_conc['year']} to {_fmt(float(latest_conc['top4_share']) * 100,2)}% in {latest_conc['year']}. The corresponding Gini coefficient changed from {_fmt(first_conc['gini'])} to {_fmt(latest_conc['gini'])}.",
        f"The 2024 large-minus-small digital-intensity gap has a Pearson correlation of {_fmt(assoc['pearson_r'])} with circularity (p={_fmt(assoc['pearson_p'])}).",
        "", "## Country typology", "",
        "The four-cluster solution uses standardized 2024 circularity, small-firm digital intensity, large-firm digital intensity, and log recyclable imports. Cluster sizes are " + ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())) + ".",
        "", "## Interpretation", "",
        "The results describe structural readiness and market conditions rather than causal effects of DPP implementation. DPP mandates are too recent for a credible ex-post causal evaluation using these datasets. The empirical evidence is therefore used to evaluate the economic mechanisms developed in the paper: information capacity, unequal digital readiness, circular-market depth, and potential compliance asymmetry.",
        "", "## Bayesian extension", ""
    ]
    for row in bayes:
        if row["term"] != "intercept":
            lines.append(f"- {row['model']} / {row['term']}: posterior mean={_fmt(row['posterior_mean_std'])}, 95% credible interval [{_fmt(row['ci_low_95'])}, {_fmt(row['ci_high_95'])}], P(beta>0|data)={_fmt(row['prob_gt_zero'])}.")
    for row in bayes_fit:
        lines.append(f"- {row['model']}: posterior R2 mean={_fmt(row['posterior_r2_mean'])}, 95% interval [{_fmt(row['posterior_r2_ci_low'])}, {_fmt(row['posterior_r2_ci_high'])}].")
    cs = causal_sens[0]
    lines += [
        "", "## Causal-structure and sensitivity audit", "",
        "A directed acyclic graph separates the hypothesized DPP mechanism from the observed Eurostat associations. DPP adoption, economic development, industrial structure, and environmental-policy confounders are not fully observed in this repository, so a DPP causal effect is not identified.",
        f"For the 2024 small-DII/circularity association, the classical partial R2 is {_fmt(cs['partial_r2_exposure_outcome'])} and the equal-strength robustness value to reduce the coefficient to zero is {_fmt(cs['equal_strength_robustness_value_to_zero'])}. This is a sensitivity diagnostic, not a causal estimate.",
        "", "## Sovereignty optimization scenario", "",
        "The optimization module traces a normalized Pareto frontier between implementation effort and operational-sovereignty risk. It is a theoretical scenario analysis rather than provider-level empirical evidence.",
        f"Across {len(frontier)} sovereignty-weight settings, the model records optimal interoperability, substitutability, switching-cost, resilience, and portability configurations under minimum technical safeguards."
    ]
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "analysis_summary.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
