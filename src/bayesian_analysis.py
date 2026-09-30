"""Bayesian extensions for the DPP market-economics analysis.

The module uses conjugate Bayesian linear regression so the full analysis remains
lightweight and reproducible without requiring an MCMC runtime. Predictors and
outcomes are standardized before estimation. Posterior simulation is then used
to report credible intervals, direction probabilities, posterior R2, and
posterior predictive uncertainty.
"""
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

from src.config import FIGURES, MODELS, PROCESSED, TABLES
from src.io_utils import as_float, read_csv, write_csv

SEED = 20260930
N_DRAWS = 50000


def _series(rows, year):
    return {
        r["country"]: as_float(r["value"])
        for r in rows
        if int(r["year"]) == year
        and not r["country"].startswith("European Union")
        and as_float(r["value"]) is not None
    }


def _digital(rows, year, size):
    return {
        r["country"]: as_float(r["value"])
        for r in rows
        if int(r["year"]) == year
        and r["size_class"] == size
        and r["intensity"] == "basic_or_above"
        and r["version"] == "v4"
        and not r["country"].startswith("European Union")
        and as_float(r["value"]) is not None
    }


def _standardize(a):
    a = np.asarray(a, dtype=float)
    mean = a.mean(axis=0)
    sd = a.std(axis=0, ddof=1)
    sd = np.where(sd == 0, 1.0, sd)
    return (a - mean) / sd, mean, sd


def _bayesian_linear(y, X, labels, model_name, seed=SEED, n_draws=N_DRAWS):
    """Normal-inverse-gamma conjugate Bayesian linear regression.

    y and non-intercept X columns are standardized. Priors are weakly regularizing:
    alpha ~ N(0, 10^2 sigma^2), beta_k ~ N(0, 2^2 sigma^2),
    sigma^2 ~ InvGamma(2, 1).
    """
    y = np.asarray(y, dtype=float)
    X = np.asarray(X, dtype=float)
    yz, y_mean, y_sd = _standardize(y)
    Xz, x_mean, x_sd = _standardize(X)
    design = np.column_stack([np.ones(len(yz)), Xz])

    p = design.shape[1]
    m0 = np.zeros(p)
    prior_var = np.diag([100.0] + [4.0] * (p - 1))
    V0_inv = np.linalg.inv(prior_var)
    a0, b0 = 2.0, 1.0

    Vn = np.linalg.inv(V0_inv + design.T @ design)
    mn = Vn @ (V0_inv @ m0 + design.T @ yz)
    an = a0 + len(yz) / 2.0
    bn = b0 + 0.5 * (yz @ yz + m0 @ V0_inv @ m0 - mn @ np.linalg.inv(Vn) @ mn)

    rng = np.random.default_rng(seed)
    sigma2 = stats.invgamma(a=an, scale=bn).rvs(size=n_draws, random_state=rng)
    L = np.linalg.cholesky(Vn)
    z = rng.normal(size=(n_draws, p))
    beta_draws = mn + (z @ L.T) * np.sqrt(sigma2)[:, None]

    summaries = []
    all_labels = ["intercept"] + labels
    for j, label in enumerate(all_labels):
        d = beta_draws[:, j]
        summaries.append({
            "model": model_name,
            "term": label,
            "posterior_mean_std": float(d.mean()),
            "posterior_sd_std": float(d.std(ddof=1)),
            "ci_low_95": float(np.quantile(d, 0.025)),
            "ci_high_95": float(np.quantile(d, 0.975)),
            "prob_gt_zero": float(np.mean(d > 0)),
            "prob_lt_zero": float(np.mean(d < 0)),
            "n": len(y),
        })

    mu = beta_draws[:, 0, None] + beta_draws[:, 1:] @ Xz.T
    var_mu = np.var(mu, axis=1, ddof=1)
    bayes_r2 = var_mu / (var_mu + sigma2)
    fit = {
        "model": model_name,
        "n": len(y),
        "posterior_r2_mean": float(bayes_r2.mean()),
        "posterior_r2_ci_low": float(np.quantile(bayes_r2, 0.025)),
        "posterior_r2_ci_high": float(np.quantile(bayes_r2, 0.975)),
        "y_mean_original": float(y_mean),
        "y_sd_original": float(y_sd),
    }
    metadata = {
        "x_mean": np.asarray(x_mean).tolist(),
        "x_sd": np.asarray(x_sd).tolist(),
        "y_mean": float(y_mean),
        "y_sd": float(y_sd),
    }
    return summaries, fit, beta_draws, sigma2, metadata


def _plot_coefficients(rows, path_base, title):
    terms = [r for r in rows if r["term"] != "intercept"]
    y = np.arange(len(terms))
    means = np.array([r["posterior_mean_std"] for r in terms], dtype=float)
    lo = np.array([r["ci_low_95"] for r in terms], dtype=float)
    hi = np.array([r["ci_high_95"] for r in terms], dtype=float)
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    ax.axvline(0, linewidth=1)
    ax.errorbar(means, y, xerr=[means - lo, hi - means], fmt="o", capsize=4)
    ax.set_yticks(y, [r["term"].replace("_", " ") for r in terms])
    ax.set_xlabel("Standardized posterior coefficient (95% credible interval)")
    ax.set_title(title)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(path_base.with_suffix(f".{ext}"), dpi=300, bbox_inches="tight")
    plt.close(fig)


def _plot_target_posterior(draws, label, path_base, title):
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    ax.hist(draws, bins=60, density=True, alpha=0.75)
    ax.axvline(0, linewidth=1)
    ax.axvline(np.mean(draws), linestyle="--", linewidth=1.2)
    ax.set_xlabel(f"Standardized coefficient: {label.replace('_', ' ')}")
    ax.set_ylabel("Posterior density")
    ax.set_title(title)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(path_base.with_suffix(f".{ext}"), dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    circular = read_csv(PROCESSED / "circularity_long.csv")
    trade = read_csv(PROCESSED / "trade_long.csv")
    digital = read_csv(PROCESSED / "digital_intensity_long.csv")

    circ22, circ24 = _series(circular, 2022), _series(circular, 2024)
    trade22, trade24 = _series(trade, 2022), _series(trade, 2024)
    small22 = _digital(digital, 2022, "small_10_49")
    small24 = _digital(digital, 2024, "small_10_49")
    large24 = _digital(digital, 2024, "large_250_plus")

    common24 = sorted(set(circ24) & set(trade24) & set(small24) & set(large24))
    y24 = [circ24[c] for c in common24]

    # Direct Bayesian analogues of the paper's original one-predictor models.
    rows_small, fit_small, draws_small, sigma_small, meta_small = _bayesian_linear(
        y24, [[small24[c]] for c in common24], ["small_basic_dii"], "bayes_small_dii_2024", seed=SEED - 2
    )
    rows_large, fit_large, draws_large, sigma_large, meta_large = _bayesian_linear(
        y24, [[large24[c]] for c in common24], ["large_basic_dii"], "bayes_large_dii_2024", seed=SEED - 1
    )

    X24 = [[small24[c], large24[c] - small24[c], np.log1p(trade24[c])] for c in common24]
    labels24 = ["small_basic_dii", "large_minus_small_gap", "log_recyclable_imports"]
    rows24, fit24, draws24, sigma24, meta24 = _bayesian_linear(y24, X24, labels24, "bayes_cross_section_2024")

    common_change = sorted(set(circ22) & set(circ24) & set(trade22) & set(small22) & set(small24))
    ychg = [circ24[c] - circ22[c] for c in common_change]
    Xchg = [[small24[c] - small22[c], circ22[c], np.log1p(trade22[c])] for c in common_change]
    labelschg = ["small_dii_change_2022_2024", "baseline_circularity_2022", "log_imports_2022"]
    rowschg, fitchg, drawschg, sigmachg, metachg = _bayesian_linear(ychg, Xchg, labelschg, "bayes_change_2022_2024", seed=SEED + 1)

    all_rows = rows_small + rows_large + rows24 + rowschg
    write_csv(TABLES / "bayesian_posterior_summary.csv", all_rows,
              ["model", "term", "posterior_mean_std", "posterior_sd_std", "ci_low_95", "ci_high_95", "prob_gt_zero", "prob_lt_zero", "n"])
    write_csv(TABLES / "bayesian_model_fit.csv", [fit_small, fit_large, fit24, fitchg],
              ["model", "n", "posterior_r2_mean", "posterior_r2_ci_low", "posterior_r2_ci_high", "y_mean_original", "y_sd_original"])

    MODELS.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        MODELS / "bayesian_posterior_draws.npz",
        small_dii_beta=draws_small,
        small_dii_sigma2=sigma_small,
        large_dii_beta=draws_large,
        large_dii_sigma2=sigma_large,
        cross_section_beta=draws24,
        cross_section_sigma2=sigma24,
        change_beta=drawschg,
        change_sigma2=sigmachg,
    )
    (MODELS / "bayesian_model_metadata.txt").write_text(
        "Bayesian linear models use standardized outcomes/predictors and weakly regularizing "
        "normal-inverse-gamma priors.\n"
        f"Small-DII metadata: {meta_small}\nLarge-DII metadata: {meta_large}\n"
        f"Cross-section metadata: {meta24}\nChange-model metadata: {metachg}\n"
        f"Posterior draws per model: {N_DRAWS}\nSeed: {SEED}\n",
        encoding="utf-8",
    )

    FIGURES.mkdir(parents=True, exist_ok=True)
    _plot_coefficients(rows_small + rows_large, FIGURES / "fig19_bayesian_single_predictor_coefficients", "Bayesian DII models, 2024")
    _plot_coefficients(rows24, FIGURES / "fig20_bayesian_cross_section_coefficients", "Bayesian cross-section model, 2024")
    _plot_coefficients(rowschg, FIGURES / "fig21_bayesian_change_coefficients", "Bayesian change model, 2022–2024")
    target_idx = 1 + labelschg.index("small_dii_change_2022_2024")
    _plot_target_posterior(drawschg[:, target_idx], "small_dii_change_2022_2024", FIGURES / "fig24_bayesian_change_posterior", "Posterior for digital-capability change")

    return all_rows, [fit_small, fit_large, fit24, fitchg]


if __name__ == "__main__":
    main()
