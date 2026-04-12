import pandas as pd

from scoring.composite import compute_composite_scores


def test_composite_ranking_order():
    """Three synthetic peers: highest ROE should not always win every pillar but composite orders."""
    latest = pd.DataFrame(
        {
            "fiscal_year": [2023, 2023, 2023],
            "roe": [0.20, 0.10, 0.15],
            "roa": [0.10, 0.05, 0.08],
            "net_profit_margin": [0.10, 0.05, 0.08],
            "current_ratio": [1.5, 1.2, 1.0],
            "quick_ratio": [1.0, 0.8, 0.6],
            "debt_to_equity": [0.5, 1.0, 2.0],
            "interest_coverage": [10.0, 5.0, 2.0],
            "asset_turnover": [2.0, 1.5, 1.0],
            "inventory_turnover": [8.0, 6.0, 4.0],
            "piotroski_f_score": [5.0, 5.0, 5.0],
        },
        index=["A", "B", "C"],
    )
    cfg = {
        "composite_weights": {
            "profitability": 1.0,
            "liquidity": 0.0,
            "leverage": 0.0,
            "efficiency": 0.0,
        },
        "pillar_metrics": {
            "profitability": {"roe": 1.0, "roa": 0.0, "net_profit_margin": 0.0},
            "liquidity": {"current_ratio": 0.5, "quick_ratio": 0.5},
            "leverage": {"debt_to_equity": 0.5, "interest_coverage": 0.5},
            "efficiency": {"asset_turnover": 0.5, "inventory_turnover": 0.5},
        },
        "piotroski_blend": 0.0,
    }
    out = compute_composite_scores(latest, cfg)
    # Profitability pillar uses ROE only → ordering follows ROE: A (20%) > C (15%) > B (10%)
    assert out.loc["A", "composite_score"] > out.loc["C", "composite_score"]
    assert out.loc["C", "composite_score"] > out.loc["B", "composite_score"]
