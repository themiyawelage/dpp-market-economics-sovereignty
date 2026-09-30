from collections import defaultdict

import numpy as np
from scipy import stats

from src.config import PROCESSED, TABLES
from src.io_utils import as_float, read_csv, write_csv
from src.analysis_utils import summary


def _digital(rows, year, size, version="v4"):
    return {
        row["country"]: as_float(row["value"])
        for row in rows
        if int(row["year"]) == year
        and row["size_class"] == size
        and row["intensity"] == "basic_or_above"
        and row["version"] == version
        and row["country"] != "European Union - 27 countries (from 2020)"
    }


def _series(rows, year):
    return {
        row["country"]: as_float(row["value"])
        for row in rows
        if int(row["year"]) == year and row["country"] != "European Union - 27 countries (from 2020)"
    }


def main():
    circular = read_csv(PROCESSED / "circularity_long.csv")
    trade = read_csv(PROCESSED / "trade_long.csv")
    digital = read_csv(PROCESSED / "digital_intensity_long.csv")
    circ24 = _series(circular, 2024)
    trade24 = _series(trade, 2024)
    small24 = _digital(digital, 2024, "small_10_49")
    medium24 = _digital(digital, 2024, "medium_50_249")
    large24 = _digital(digital, 2024, "large_250_plus")
    variables = {
        "Circular material use rate 2024 (%)": list(circ24.values()),
        "Recyclable imports 2024 (tonnes)": list(trade24.values()),
        "Small firms basic DII 2024 (%)": list(small24.values()),
        "Medium firms basic DII 2024 (%)": list(medium24.values()),
        "Large firms basic DII 2024 (%)": list(large24.values()),
    }
    stats_rows = []
    for name, values in variables.items():
        item = {"variable": name}
        item.update(summary(values))
        stats_rows.append(item)
    write_csv(TABLES / "descriptive_statistics.csv", stats_rows, ["variable", "n", "mean", "sd", "median", "min", "max"])
    countries = sorted(set(circ24) & set(trade24) & set(small24) & set(large24))
    gap_rows = []
    for country in countries:
        gap_rows.append({
            "country": country,
            "small_basic_dii": small24[country],
            "medium_basic_dii": medium24.get(country),
            "large_basic_dii": large24[country],
            "large_minus_small_gap": large24[country] - small24[country],
            "circularity_rate": circ24[country],
            "recyclable_imports_tonnes": trade24[country],
        })
    gap_rows.sort(key=lambda x: x["large_minus_small_gap"], reverse=True)
    write_csv(
        TABLES / "sme_digital_gap.csv",
        gap_rows,
        ["country", "small_basic_dii", "medium_basic_dii", "large_basic_dii", "large_minus_small_gap", "circularity_rate", "recyclable_imports_tonnes"],
    )
    corr_vars = {
        "circularity": circ24,
        "small_dii": small24,
        "medium_dii": medium24,
        "large_dii": large24,
        "log_trade": {k: np.log1p(v) for k, v in trade24.items() if v is not None},
    }
    corr_rows = []
    names = list(corr_vars)
    for a in names:
        for b in names:
            common = sorted(set(corr_vars[a]) & set(corr_vars[b]))
            x = np.array([corr_vars[a][c] for c in common], dtype=float)
            y = np.array([corr_vars[b][c] for c in common], dtype=float)
            pearson = stats.pearsonr(x, y) if len(common) >= 3 else None
            spearman = stats.spearmanr(x, y) if len(common) >= 3 else None
            corr_rows.append({
                "variable_x": a,
                "variable_y": b,
                "n": len(common),
                "pearson_r": pearson.statistic if pearson else None,
                "pearson_p": pearson.pvalue if pearson else None,
                "spearman_rho": spearman.statistic if spearman else None,
                "spearman_p": spearman.pvalue if spearman else None,
            })
    write_csv(TABLES / "correlations_2024.csv", corr_rows, ["variable_x", "variable_y", "n", "pearson_r", "pearson_p", "spearman_rho", "spearman_p"])
    return {
        "circ24": circ24, "trade24": trade24, "small24": small24,
        "medium24": medium24, "large24": large24, "gaps": gap_rows,
    }


if __name__ == "__main__":
    main()
