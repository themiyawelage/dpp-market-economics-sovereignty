import numpy as np
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from src.config import PROCESSED, TABLES
from src.io_utils import as_float, read_csv, write_csv


def _series(rows, year):
    return {r["country"]: as_float(r["value"]) for r in rows if int(r["year"]) == year and not r["country"].startswith("European Union") and as_float(r["value"]) is not None}


def _digital(rows, year, size):
    return {r["country"]: as_float(r["value"]) for r in rows if int(r["year"]) == year and r["size_class"] == size and r["intensity"] == "basic_or_above" and r["version"] == "v4" and not r["country"].startswith("European Union") and as_float(r["value"]) is not None}


def _bootstrap_corr(x, y, reps=10000, seed=42):
    rng = np.random.default_rng(seed)
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    values = []
    for _ in range(reps):
        idx = rng.integers(0, len(x), len(x))
        if np.std(x[idx]) > 0 and np.std(y[idx]) > 0:
            values.append(np.corrcoef(x[idx], y[idx])[0, 1])
    return np.quantile(values, [0.025, 0.5, 0.975])


def main():
    circular = read_csv(PROCESSED / "circularity_long.csv")
    trade = read_csv(PROCESSED / "trade_long.csv")
    digital = read_csv(PROCESSED / "digital_intensity_long.csv")
    circ15 = _series(circular, 2015)
    circ24 = _series(circular, 2024)
    trade16 = _series(trade, 2016)
    trade24 = _series(trade, 2024)
    small22 = _digital(digital, 2022, "small_10_49")
    small24 = _digital(digital, 2024, "small_10_49")
    large24 = _digital(digital, 2024, "large_250_plus")
    common = sorted(set(circ24) & set(trade24) & set(small24) & set(large24))
    features = np.array([[circ24[c], small24[c], large24[c], np.log1p(trade24[c])] for c in common])
    scaled = StandardScaler().fit_transform(features)
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=50).fit(scaled)
    pca = PCA(n_components=2).fit(scaled)
    scores = pca.transform(scaled)
    cluster_rows = []
    for i, country in enumerate(common):
        cluster_rows.append({
            "country": country,
            "cluster": int(kmeans.labels_[i]) + 1,
            "pca1": scores[i, 0],
            "pca2": scores[i, 1],
            "circularity_rate": circ24[country],
            "small_basic_dii": small24[country],
            "large_basic_dii": large24[country],
            "digital_gap": large24[country] - small24[country],
            "recyclable_imports_tonnes": trade24[country],
        })
    write_csv(TABLES / "country_clusters_2024.csv", cluster_rows, ["country", "cluster", "pca1", "pca2", "circularity_rate", "small_basic_dii", "large_basic_dii", "digital_gap", "recyclable_imports_tonnes"])
    change_rows = []
    for country in sorted(set(circ15) & set(circ24)):
        change_rows.append({"country": country, "circularity_change_2015_2024": circ24[country] - circ15[country]})
    trade_changes = {c: (trade24[c] / trade16[c]) ** (1 / 8) - 1 for c in set(trade16) & set(trade24) if trade16[c] > 0}
    digital_changes = {c: small24[c] - small22[c] for c in set(small22) & set(small24)}
    for row in change_rows:
        c = row["country"]
        row["small_dii_change_2022_2024"] = digital_changes.get(c)
        row["trade_cagr_2016_2024"] = trade_changes.get(c)
    write_csv(TABLES / "country_changes.csv", change_rows, ["country", "circularity_change_2015_2024", "small_dii_change_2022_2024", "trade_cagr_2016_2024"])
    pairs = [c for c in common if c in small24]
    x = [small24[c] for c in pairs]
    y = [circ24[c] for c in pairs]
    ci = _bootstrap_corr(x, y)
    robustness = [{
        "relationship": "small_basic_dii_2024_vs_circularity_2024",
        "pearson_r": stats.pearsonr(x, y).statistic,
        "pearson_p": stats.pearsonr(x, y).pvalue,
        "spearman_rho": stats.spearmanr(x, y).statistic,
        "spearman_p": stats.spearmanr(x, y).pvalue,
        "bootstrap_ci_low": ci[0],
        "bootstrap_median": ci[1],
        "bootstrap_ci_high": ci[2],
        "n": len(pairs),
    }]
    write_csv(TABLES / "robustness_checks.csv", robustness, list(robustness[0]))
    pca_rows = [{"component": "PC1", "explained_variance_ratio": pca.explained_variance_ratio_[0]}, {"component": "PC2", "explained_variance_ratio": pca.explained_variance_ratio_[1]}]
    write_csv(TABLES / "pca_variance.csv", pca_rows, ["component", "explained_variance_ratio"])
    return cluster_rows, change_rows, robustness


if __name__ == "__main__":
    main()
