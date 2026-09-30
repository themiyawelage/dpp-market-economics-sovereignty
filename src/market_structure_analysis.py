import numpy as np
from scipy import stats

from src.config import PROCESSED, TABLES
from src.io_utils import as_float, read_csv, write_csv


def _gini(values):
    x = np.sort(np.asarray(values, dtype=float))
    if len(x) == 0 or np.sum(x) == 0:
        return 0.0
    n = len(x)
    return float((2 * np.sum((np.arange(1, n + 1)) * x) / (n * np.sum(x))) - (n + 1) / n)


def main():
    trade = read_csv(PROCESSED / "trade_long.csv")
    circular = read_csv(PROCESSED / "circularity_long.csv")
    digital = read_csv(PROCESSED / "digital_intensity_long.csv")
    concentration = []
    years = sorted({int(r["year"]) for r in trade})
    for year in years:
        values = [as_float(r["value"]) for r in trade if int(r["year"]) == year and not r["country"].startswith("European Union") and as_float(r["value"]) is not None]
        total = sum(values)
        shares = np.array(values) / total
        concentration.append({
            "year": year,
            "hhi": float(np.sum(shares ** 2)),
            "hhi_10000": float(np.sum(shares ** 2) * 10000),
            "top4_share": float(np.sum(np.sort(shares)[-4:])),
            "gini": _gini(values),
        })
    write_csv(TABLES / "trade_market_concentration.csv", concentration, ["year", "hhi", "hhi_10000", "top4_share", "gini"])
    dispersion = []
    for year in sorted({int(r["year"]) for r in circular}):
        values = [as_float(r["value"]) for r in circular if int(r["year"]) == year and not r["country"].startswith("European Union") and as_float(r["value"]) is not None]
        dispersion.append({
            "year": year,
            "mean": float(np.mean(values)),
            "sd": float(np.std(values, ddof=1)),
            "cv": float(np.std(values, ddof=1) / np.mean(values)),
            "iqr": float(np.quantile(values, 0.75) - np.quantile(values, 0.25)),
        })
    write_csv(TABLES / "circularity_dispersion.csv", dispersion, ["year", "mean", "sd", "cv", "iqr"])
    circ24 = {r["country"]: as_float(r["value"]) for r in circular if int(r["year"]) == 2024 and not r["country"].startswith("European Union") and as_float(r["value"]) is not None}
    small24 = {r["country"]: as_float(r["value"]) for r in digital if int(r["year"]) == 2024 and r["size_class"] == "small_10_49" and r["intensity"] == "basic_or_above" and r["version"] == "v4" and not r["country"].startswith("European Union") and as_float(r["value"]) is not None}
    large24 = {r["country"]: as_float(r["value"]) for r in digital if int(r["year"]) == 2024 and r["size_class"] == "large_250_plus" and r["intensity"] == "basic_or_above" and r["version"] == "v4" and not r["country"].startswith("European Union") and as_float(r["value"]) is not None}
    common = sorted(set(circ24) & set(small24) & set(large24))
    gaps = np.array([large24[c] - small24[c] for c in common])
    circ = np.array([circ24[c] for c in common])
    pearson = stats.pearsonr(gaps, circ)
    spearman = stats.spearmanr(gaps, circ)
    assoc = [{
        "relationship": "digital_size_gap_vs_circularity_2024",
        "n": len(common),
        "pearson_r": pearson.statistic,
        "pearson_p": pearson.pvalue,
        "spearman_rho": spearman.statistic,
        "spearman_p": spearman.pvalue,
    }]
    write_csv(TABLES / "market_structure_associations.csv", assoc, list(assoc[0]))
    return concentration, dispersion, assoc


if __name__ == "__main__":
    main()
