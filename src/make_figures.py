import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from src.config import FIGURES, PROCESSED, TABLES
from src.io_utils import as_float, read_csv


def _save(name):
    FIGURES.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(FIGURES / f"{name}.png", dpi=300, bbox_inches="tight")
    plt.savefig(FIGURES / f"{name}.pdf", bbox_inches="tight")
    plt.close()


def _series(rows, year):
    return {r["country"]: as_float(r["value"]) for r in rows if int(r["year"]) == year and as_float(r["value"]) is not None}


def _digital(rows, year, size):
    return {r["country"]: as_float(r["value"]) for r in rows if int(r["year"]) == year and r["size_class"] == size and r["intensity"] == "basic_or_above" and r["version"] == "v4" and as_float(r["value"]) is not None}


def _scatter(x, y, labels, xlabel, ylabel, name):
    plt.figure(figsize=(7.2, 5.2))
    plt.scatter(x, y, s=45)
    slope, intercept, r, p, _ = stats.linregress(x, y)
    grid = np.linspace(min(x), max(x), 100)
    plt.plot(grid, intercept + slope * grid, linewidth=1.6)
    for xi, yi, label in zip(x, y, labels):
        plt.annotate(label, (xi, yi), fontsize=6.5, xytext=(3, 3), textcoords="offset points")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(f"r = {r:.2f}, p = {p:.3f}")
    plt.grid(alpha=0.2)
    _save(name)


def main():
    circular = read_csv(PROCESSED / "circularity_long.csv")
    trade = read_csv(PROCESSED / "trade_long.csv")
    digital = read_csv(PROCESSED / "digital_intensity_long.csv")
    eu_circ = [(int(r["year"]), as_float(r["value"])) for r in circular if r["country"].startswith("European Union")]
    eu_circ.sort()
    plt.figure(figsize=(7.2, 4.8))
    plt.plot([x[0] for x in eu_circ], [x[1] for x in eu_circ], marker="o")
    plt.xlabel("Year"); plt.ylabel("Circular material use rate (%)"); plt.grid(alpha=0.2)
    _save("fig01_eu_circularity_trend")
    circ24 = _series(circular, 2024)
    circ24.pop("European Union - 27 countries (from 2020)", None)
    ordered = sorted(circ24.items(), key=lambda x: x[1])
    plt.figure(figsize=(7.2, 8.4))
    plt.barh([x[0] for x in ordered], [x[1] for x in ordered])
    plt.xlabel("Circular material use rate (%)")
    _save("fig02_country_circularity_2024")
    eu_trade = [(int(r["year"]), as_float(r["value"])) for r in trade if r["country"].startswith("European Union")]
    eu_trade.sort()
    plt.figure(figsize=(7.2, 4.8))
    plt.plot([x[0] for x in eu_trade], [x[1] / 1e6 for x in eu_trade], marker="o")
    plt.xlabel("Year"); plt.ylabel("Extra-EU recyclable imports (million tonnes)"); plt.grid(alpha=0.2)
    _save("fig03_eu_recyclable_imports_trend")
    trade24 = _series(trade, 2024)
    trade24.pop("European Union - 27 countries (from 2020)", None)
    ordered_trade = sorted(trade24.items(), key=lambda x: x[1])
    plt.figure(figsize=(7.2, 8.4))
    plt.barh([x[0] for x in ordered_trade], [x[1] / 1e6 for x in ordered_trade])
    plt.xlabel("Extra-EU recyclable imports (million tonnes)")
    _save("fig04_country_recyclable_imports_2024")
    small24 = _digital(digital, 2024, "small_10_49")
    medium24 = _digital(digital, 2024, "medium_50_249")
    large24 = _digital(digital, 2024, "large_250_plus")
    for d in (small24, medium24, large24):
        d.pop("European Union - 27 countries (from 2020)", None)
    countries = sorted(set(small24) & set(medium24) & set(large24))
    idx = np.arange(len(countries))
    plt.figure(figsize=(10.5, 5.5))
    width = 0.27
    plt.bar(idx - width, [small24[c] for c in countries], width=width, label="10–49")
    plt.bar(idx, [medium24[c] for c in countries], width=width, label="50–249")
    plt.bar(idx + width, [large24[c] for c in countries], width=width, label="250+")
    plt.xticks(idx, countries, rotation=75, ha="right", fontsize=7)
    plt.ylabel("Enterprises with at least basic digital intensity (%)")
    plt.legend(frameon=False)
    _save("fig05_digital_intensity_by_firm_size_2024")
    gaps = [(c, large24[c] - small24[c]) for c in countries]
    gaps.sort(key=lambda x: x[1])
    plt.figure(figsize=(7.2, 8.4))
    plt.barh([x[0] for x in gaps], [x[1] for x in gaps])
    plt.xlabel("Large-firm minus small-firm basic DII (percentage points)")
    _save("fig06_sme_digital_gap_2024")
    common = sorted(set(circ24) & set(small24))
    _scatter([small24[c] for c in common], [circ24[c] for c in common], common, "Small firms with basic DII (%)", "Circular material use rate (%)", "fig07_small_dii_vs_circularity")
    common = sorted(set(circ24) & set(large24))
    _scatter([large24[c] for c in common], [circ24[c] for c in common], common, "Large firms with basic DII (%)", "Circular material use rate (%)", "fig08_large_dii_vs_circularity")
    common = sorted(set(trade24) & set(small24))
    _scatter([small24[c] for c in common], [np.log1p(trade24[c]) for c in common], common, "Small firms with basic DII (%)", "log(1 + recyclable imports tonnes)", "fig09_small_dii_vs_trade")
    common = sorted(set(trade24) & set(circ24))
    _scatter([circ24[c] for c in common], [np.log1p(trade24[c]) for c in common], common, "Circular material use rate (%)", "log(1 + recyclable imports tonnes)", "fig10_circularity_vs_trade")
    corr_rows = read_csv(TABLES / "correlations_2024.csv")
    names = ["circularity", "small_dii", "medium_dii", "large_dii", "log_trade"]
    matrix = np.empty((len(names), len(names)))
    for i, a in enumerate(names):
        for j, b in enumerate(names):
            match = next(r for r in corr_rows if r["variable_x"] == a and r["variable_y"] == b)
            matrix[i, j] = float(match["pearson_r"])
    plt.figure(figsize=(6.2, 5.2))
    im = plt.imshow(matrix, vmin=-1, vmax=1, cmap="coolwarm")
    plt.xticks(range(len(names)), names, rotation=40, ha="right")
    plt.yticks(range(len(names)), names)
    for i in range(len(names)):
        for j in range(len(names)):
            plt.text(j, i, f"{matrix[i,j]:.2f}", ha="center", va="center", fontsize=8)
    plt.colorbar(im, label="Pearson correlation")
    _save("fig11_correlation_matrix_2024")
    clusters = read_csv(TABLES / "country_clusters_2024.csv")
    plt.figure(figsize=(7.2, 5.4))
    for cluster in sorted(set(r["cluster"] for r in clusters)):
        subset = [r for r in clusters if r["cluster"] == cluster]
        plt.scatter([float(r["pca1"]) for r in subset], [float(r["pca2"]) for r in subset], label=f"Cluster {cluster}", s=55)
    for r in clusters:
        plt.annotate(r["country"], (float(r["pca1"]), float(r["pca2"])), fontsize=6.5, xytext=(3,3), textcoords="offset points")
    plt.xlabel("Principal component 1"); plt.ylabel("Principal component 2"); plt.legend(frameon=False)
    _save("fig12_country_clusters_pca_2024")
    reg = read_csv(TABLES / "regression_results.csv")
    coeffs = [r for r in reg if r["term"] != "const"]
    labels = [f"{r['model']}\n{r['term']}" for r in coeffs]
    y = np.arange(len(coeffs))
    vals = np.array([float(r["coef"]) for r in coeffs])
    low = vals - np.array([float(r["ci_low"]) for r in coeffs])
    high = np.array([float(r["ci_high"]) for r in coeffs]) - vals
    plt.figure(figsize=(8.2, 5.8))
    plt.errorbar(vals, y, xerr=[low, high], fmt="o", capsize=3)
    plt.axvline(0, linewidth=1)
    plt.yticks(y, labels, fontsize=7)
    plt.xlabel("Coefficient with 95% robust confidence interval")
    _save("fig13_regression_coefficients")
    changes = read_csv(TABLES / "country_changes.csv")
    valid = [r for r in changes if r["small_dii_change_2022_2024"] not in ("", None)]
    if valid:
        _scatter([float(r["small_dii_change_2022_2024"]) for r in valid], [float(r["circularity_change_2015_2024"]) for r in valid], [r["country"] for r in valid], "Small-firm basic DII change, 2022–2024 (pp)", "Circularity change, 2015–2024 (pp)", "fig14_digital_change_vs_circularity_change")
    x = np.array([small24[c] for c in countries])
    y = np.array([circ24[c] for c in countries])
    plt.figure(figsize=(7.2, 5.4))
    plt.scatter(x, y, s=50)
    plt.axvline(np.median(x), linewidth=1)
    plt.axhline(np.median(y), linewidth=1)
    for c, xi, yi in zip(countries, x, y):
        plt.annotate(c, (xi, yi), fontsize=6.5, xytext=(3,3), textcoords="offset points")
    plt.xlabel("Small firms with basic DII (%)"); plt.ylabel("Circular material use rate (%)")
    _save("fig15_readiness_circularity_quadrants")
    concentration = read_csv(TABLES / "trade_market_concentration.csv")
    plt.figure(figsize=(7.2, 4.8))
    plt.plot([int(r["year"]) for r in concentration], [float(r["top4_share"]) * 100 for r in concentration], marker="o")
    plt.xlabel("Year"); plt.ylabel("Top-four country share of imports (%)"); plt.grid(alpha=0.2)
    _save("fig16_trade_top4_concentration")
    plt.figure(figsize=(7.2, 4.8))
    plt.plot([int(r["year"]) for r in concentration], [float(r["gini"]) for r in concentration], marker="o")
    plt.xlabel("Year"); plt.ylabel("Gini coefficient of country import volumes"); plt.grid(alpha=0.2)
    _save("fig17_trade_import_inequality")
    dispersion = read_csv(TABLES / "circularity_dispersion.csv")
    plt.figure(figsize=(7.2, 4.8))
    plt.plot([int(r["year"]) for r in dispersion], [float(r["sd"]) for r in dispersion], marker="o", label="Standard deviation")
    plt.plot([int(r["year"]) for r in dispersion], [float(r["iqr"]) for r in dispersion], marker="s", label="IQR")
    plt.xlabel("Year"); plt.ylabel("Cross-country dispersion (percentage points)"); plt.legend(frameon=False); plt.grid(alpha=0.2)
    _save("fig18_circularity_cross_country_dispersion")


if __name__ == "__main__":
    main()
