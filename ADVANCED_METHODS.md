# Advanced Methods Extension

This repository extends the original descriptive and frequentist analysis with Bayesian inference, explicit causal-structure analysis, and a scenario-based sovereignty optimization model.

## 1. Bayesian inference

The Bayesian module (`src/bayesian_analysis.py`) estimates standardized linear models using a conjugate normal-inverse-gamma specification. It generates 50,000 posterior draws per model with fixed random seeds.

Models include:

1. 2024 small-firm DII -> circular material use.
2. 2024 large-firm DII -> circular material use.
3. Multivariable 2024 model with small-firm DII, the large-minus-small DII gap, and log recyclable-material imports.
4. 2022--2024 change model with change in small-firm DII, baseline circularity, and baseline log imports.

Reported quantities include posterior means, 95% credible intervals, posterior direction probabilities, and posterior R2.

The Bayesian results quantify uncertainty in the observed associations. They do not convert observational associations into identified causal effects.

## 2. Causal structure and sensitivity

The causal module (`src/causal_analysis.py`) encodes a directed acyclic graph linking digital capability, DPP implementation capacity, information frictions, circular activity, provider dependence, and operational digital sovereignty. Potential confounders include economic development, industrial structure, and environmental policy.

The repository does not observe actual DPP adoption or all required confounders. Therefore, it does not report an identified causal effect of DPP implementation. Instead, it provides:

- a DAG edge list;
- a causal-identification audit;
- a partial-R2 sensitivity diagnostic for the 2024 small-DII/circularity association; and
- an equal-strength omitted-confounder robustness value showing the confounding strength required to reduce the classical coefficient to zero under the sensitivity parameterization.

## 3. Sovereignty optimization

The optimization module (`src/sovereignty_optimization.py`) is a theoretical scenario analysis. It does not use fabricated provider observations.

It minimizes a weighted combination of normalized implementation effort and operational-sovereignty risk over five normalized design variables:

- interoperability (INT),
- provider substitutability (SUB),
- switching cost (SC),
- operational resilience (RES), and
- data portability (PORT).

The model evaluates 41 sovereignty-weight settings and traces a Pareto-style frontier between implementation effort and sovereignty risk. Minimum safeguards constrain interoperability, resilience, and portability to be at least 0.5.

The frontier is intended to formalize the governance trade-off developed in the paper. It is a decision-theoretic extension, not an empirical estimate of existing DPP providers.

## 4. Interpretation rule

The repository distinguishes four evidence classes:

- descriptive evidence,
- frequentist associations,
- Bayesian posterior evidence,
- theoretical causal/optimization mechanisms.

Only the first three are empirical. No output should be described as a demonstrated causal effect of DPP adoption with the currently available Eurostat data.
