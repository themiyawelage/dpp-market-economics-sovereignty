import json

import numpy as np
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.outliers_influence import variance_inflation_factor

from src.config import MODELS, PROCESSED, TABLES
from src.io_utils import as_float, read_csv, write_csv


def _dict(rows, year, size=None, version=None):
    out = {}
    for row in rows:
        if int(row["year"]) != year or row["country"].startswith("European Union"):
            continue
        if size and row.get("size_class") != size:
            continue
        if version and row.get("version") != version:
            continue
        if size and row.get("intensity") != "basic_or_above":
            continue
        value = as_float(row["value"])
        if value is not None:
            out[row["country"]] = value
    return out


def _fit(name, y, X, terms):
    Xc = sm.add_constant(np.asarray(X, dtype=float), has_constant="add")
    model = sm.OLS(np.asarray(y, dtype=float), Xc).fit(cov_type="HC3")
    rows = []
    labels = ["const"] + terms
    for idx, label in enumerate(labels):
        rows.append({
            "model": name,
            "term": label,
            "coef": model.params[idx],
            "std_err_hc3": model.bse[idx],
            "t": model.tvalues[idx],
            "p": model.pvalues[idx],
            "ci_low": model.conf_int()[idx, 0],
            "ci_high": model.conf_int()[idx, 1],
            "n": int(model.nobs),
            "r2": model.rsquared,
            "adj_r2": model.rsquared_adj,
        })
    diagnostics = {
        "model": name,
        "n": int(model.nobs),
        "r2": float(model.rsquared),
        "adj_r2": float(model.rsquared_adj),
        "aic": float(model.aic),
        "bic": float(model.bic),
        "jarque_bera_p": float(stats.jarque_bera(model.resid).pvalue),
        "condition_number": float(model.condition_number),
    }
    if Xc.shape[1] > 2:
        diagnostics["vif"] = {
            labels[i]: float(variance_inflation_factor(Xc, i))
            for i in range(1, Xc.shape[1])
        }
    return model, rows, diagnostics


def main():
    circular = read_csv(PROCESSED / "circularity_long.csv")
    trade = read_csv(PROCESSED / "trade_long.csv")
    digital = read_csv(PROCESSED / "digital_intensity_long.csv")
    circ24 = _dict(circular, 2024)
    trade24 = _dict(trade, 2024)
    small24 = _dict(digital, 2024, "small_10_49", "v4")
    large24 = _dict(digital, 2024, "large_250_plus", "v4")
    common = sorted(set(circ24) & set(trade24) & set(small24) & set(large24))
    y_circ = [circ24[c] for c in common]
    log_trade = [np.log1p(trade24[c]) for c in common]
    gap = [large24[c] - small24[c] for c in common]
    models = []
    rows = []
    diagnostics = []
    m, r, d = _fit("circularity_small_dii", y_circ, [[small24[c]] for c in common], ["small_basic_dii"])
    models.append(m); rows += r; diagnostics.append(d)
    m, r, d = _fit("circularity_large_dii", y_circ, [[large24[c]] for c in common], ["large_basic_dii"])
    models.append(m); rows += r; diagnostics.append(d)
    m, r, d = _fit("circularity_gap_trade", y_circ, [[gap[i], log_trade[i]] for i in range(len(common))], ["large_minus_small_gap", "log_recyclable_imports"])
    models.append(m); rows += r; diagnostics.append(d)
    y_trade = log_trade
    m, r, d = _fit("trade_small_dii_circularity", y_trade, [[small24[c], circ24[c]] for c in common], ["small_basic_dii", "circularity_rate"])
    models.append(m); rows += r; diagnostics.append(d)
    write_csv(TABLES / "regression_results.csv", rows, ["model", "term", "coef", "std_err_hc3", "t", "p", "ci_low", "ci_high", "n", "r2", "adj_r2"])
    MODELS.mkdir(parents=True, exist_ok=True)
    with (MODELS / "diagnostics.json").open("w", encoding="utf-8") as handle:
        json.dump(diagnostics, handle, indent=2)
    with (MODELS / "model_summaries.txt").open("w", encoding="utf-8") as handle:
        for model in models:
            handle.write(model.summary().as_text())
            handle.write("\n\n")
    return rows, diagnostics


if __name__ == "__main__":
    main()
