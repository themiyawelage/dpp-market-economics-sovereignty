# Digital Product Passports and Market Economics

Reproducible empirical analysis for the paper **Digital Product Passports and Market Economics: An Economic Theory of Information, Competition, and Strategic Dependency**.

## Data

The repository contains three Eurostat extracts:

- `env_ac_cur`: circular material use rate
- `isoc_e_dii`: digital intensity by enterprise size class
- `cei_srm020`: trade in recyclable raw materials

The raw workbooks are preserved in `data/raw/`. The pipeline parses the Excel files directly and writes standardized long-form and merged datasets to `data/processed/`.

## Analysis

The empirical work covers:

- circular material use trends and country dispersion
- recyclable raw-material import trends and market concentration
- digital intensity by enterprise size
- large-firm versus small-firm digital-readiness gaps
- Pearson and Spearman association tests
- bootstrap confidence intervals
- heteroskedasticity-robust OLS models
- multicollinearity and residual diagnostics
- country change analysis
- PCA and K-means country typology
- publication-ready figures and result tables

The analysis is descriptive and associational. It does not identify a causal effect of DPP implementation.

## Run

```bash
python -m pip install -r requirements.txt
python run_analysis.py
```

Generated outputs are written to `output/` and `reports/analysis_summary.md`.

## Structure

```text
data/raw/          Original Eurostat workbooks
data/processed/    Cleaned and merged data
src/               Data and analysis modules
output/tables/     Statistical result tables
output/figures/    PNG and PDF figures
output/models/     Model summaries and diagnostics
reports/           Analysis narrative
run_analysis.py    Full pipeline
```

## Bayesian, causal, and sovereignty extensions

The reproducibility package also includes:

- conjugate Bayesian linear regression for the 2024 cross-section
- a Bayesian 2022--2024 change model using DII Version 4 observations
- posterior direction probabilities and 95% credible intervals
- posterior R2 and posterior draws saved for reproducibility
- an explicit directed acyclic graph (DAG) for causal assumptions
- an identification audit distinguishing observed variables, mediators, and unobserved confounders
- omitted-confounding sensitivity diagnostics for the DII--circularity association
- a scenario-based multi-objective optimization model for interoperability, provider substitutability, switching cost, resilience, and portability

The causal module does **not** claim an identified causal effect of DPP adoption because the available Eurostat extracts do not contain a DPP-adoption treatment or the full confounder set required for causal identification. The optimization results are theoretical normalized scenarios, not observed provider measurements.
