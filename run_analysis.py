from src.advanced_analysis import main as advanced
from src.descriptive_analysis import main as descriptive
from src.make_figures import main as figures
from src.market_structure_analysis import main as market_structure
from src.merge_data import main as merge
from src.regression_analysis import main as regressions
from src.report_results import main as report
from src.bayesian_analysis import main as bayesian
from src.causal_analysis import main as causal
from src.sovereignty_optimization import main as optimize_sovereignty


def main():
    merge()
    descriptive()
    regressions()
    advanced()
    market_structure()
    bayesian()
    causal()
    optimize_sovereignty()
    figures()
    report()
    print("Analysis complete")


if __name__ == "__main__":
    main()
