# Empirical Results

## Data coverage

The analysis combines Eurostat circular material use, enterprise digital intensity, and extra-EU recyclable raw-material imports. Circularity covers 2015–2024, trade covers 2016–2025, and DII Version 4 provides comparable basic-intensity observations for 2022 and 2024 across firm-size groups.

## Descriptive evidence

- Circular material use rate 2024 (%): n=27, mean=10.92, median=9.40, min=1.30, max=32.70.
- Recyclable imports 2024 (tonnes): n=27, mean=1744975.67, median=1137970.00, min=3500.00, max=7131527.00.
- Small firms basic DII 2024 (%): n=27, mean=68.62, median=67.59, min=46.45, max=91.34.
- Medium firms basic DII 2024 (%): n=27, mean=88.07, median=89.20, min=69.77, max=98.77.
- Large firms basic DII 2024 (%): n=27, mean=97.43, median=98.41, min=86.43, max=100.00.

## Digital readiness and circularity

Across EU countries in 2024, the Pearson correlation between the share of small enterprises with at least basic digital intensity and the circular material use rate is 0.261 (p=0.189). The Spearman rank correlation is 0.252 (p=0.205).
A 10,000-draw nonparametric bootstrap gives a 95% interval of [-0.085, 0.578] for the Pearson correlation.

## Firm-size digital divide

Largest large-minus-small digital intensity gaps in 2024:
- Bulgaria: 44.69 percentage points.
- Latvia: 42.62 percentage points.
- Hungary: 42.41 percentage points.
- Croatia: 36.81 percentage points.
- Slovakia: 36.72 percentage points.

Smallest gaps:
- Finland: 8.66 percentage points.
- Denmark: 10.94 percentage points.
- Sweden: 15.11 percentage points.
- Malta: 15.89 percentage points.
- Belgium: 17.97 percentage points.

## Regression evidence

- circularity_small_dii / small_basic_dii: beta=0.181, robust SE=0.153, p=0.238, 95% CI [-0.120, 0.481], R2=0.068.
- circularity_large_dii / large_basic_dii: beta=0.552, robust SE=0.288, p=0.055, 95% CI [-0.013, 1.117], R2=0.055.
- circularity_gap_trade / large_minus_small_gap: beta=-0.179, robust SE=0.194, p=0.356, 95% CI [-0.559, 0.201], R2=0.052.
- circularity_gap_trade / log_recyclable_imports: beta=0.228, robust SE=1.110, p=0.837, 95% CI [-1.947, 2.404], R2=0.052.
- trade_small_dii_circularity / small_basic_dii: beta=-0.007, robust SE=0.041, p=0.864, 95% CI [-0.087, 0.073], R2=0.004.
- trade_small_dii_circularity / circularity_rate: beta=0.015, robust SE=0.074, p=0.839, 95% CI [-0.131, 0.161], R2=0.004.

## Market structure

The top-four country share of extra-EU recyclable raw-material imports changed from 52.69% in 2016 to 50.57% in 2025. The corresponding Gini coefficient changed from 0.633 to 0.606.
The 2024 large-minus-small digital-intensity gap has a Pearson correlation of -0.221 with circularity (p=0.267).

## Country typology

The four-cluster solution uses standardized 2024 circularity, small-firm digital intensity, large-firm digital intensity, and log recyclable imports. Cluster sizes are 1: 11, 2: 7, 3: 3, 4: 6.

## Interpretation

The results describe structural readiness and market conditions rather than causal effects of DPP implementation. DPP mandates are too recent for a credible ex-post causal evaluation using these datasets. The empirical evidence is therefore used to evaluate the economic mechanisms developed in the paper: information capacity, unequal digital readiness, circular-market depth, and potential compliance asymmetry.

## Bayesian extension

- bayes_small_dii_2024 / small_basic_dii: posterior mean=0.259, 95% credible interval [-0.103, 0.626], P(beta>0|data)=0.922.
- bayes_large_dii_2024 / large_basic_dii: posterior mean=0.232, 95% credible interval [-0.135, 0.602], P(beta>0|data)=0.896.
- bayes_cross_section_2024 / small_basic_dii: posterior mean=0.512, 95% credible interval [-0.682, 1.702], P(beta>0|data)=0.808.
- bayes_cross_section_2024 / large_minus_small_gap: posterior mean=0.267, 95% credible interval [-0.919, 1.452], P(beta>0|data)=0.678.
- bayes_cross_section_2024 / log_recyclable_imports: posterior mean=0.052, 95% credible interval [-0.312, 0.420], P(beta>0|data)=0.614.
- bayes_change_2022_2024 / small_dii_change_2022_2024: posterior mean=-0.009, 95% credible interval [-0.375, 0.357], P(beta>0|data)=0.481.
- bayes_change_2022_2024 / baseline_circularity_2022: posterior mean=0.269, 95% credible interval [-0.102, 0.637], P(beta>0|data)=0.927.
- bayes_change_2022_2024 / log_imports_2022: posterior mean=0.315, 95% credible interval [-0.037, 0.667], P(beta>0|data)=0.961.
- bayes_small_dii_2024: posterior R2 mean=0.095, 95% interval [0.000, 0.311].
- bayes_large_dii_2024: posterior R2 mean=0.083, 95% interval [0.000, 0.288].
- bayes_cross_section_2024: posterior R2 mean=0.152, 95% interval [0.016, 0.362].
- bayes_change_2022_2024: posterior R2 mean=0.225, 95% interval [0.036, 0.451].

## Causal-structure and sensitivity audit

A directed acyclic graph separates the hypothesized DPP mechanism from the observed Eurostat associations. DPP adoption, economic development, industrial structure, and environmental-policy confounders are not fully observed in this repository, so a DPP causal effect is not identified.
For the 2024 small-DII/circularity association, the classical partial R2 is 0.068 and the equal-strength robustness value to reduce the coefficient to zero is 0.236. This is a sensitivity diagnostic, not a causal estimate.

## Sovereignty optimization scenario

The optimization module traces a normalized Pareto frontier between implementation effort and operational-sovereignty risk. It is a theoretical scenario analysis rather than provider-level empirical evidence.
Across 41 sovereignty-weight settings, the model records optimal interoperability, substitutability, switching-cost, resilience, and portability configurations under minimum technical safeguards.