import numpy as np
import pandas as pd

from features.ratios import compute_ratio_panel
from scoring.piotroski import compute_piotroski_panel


def test_piotroski_improves_when_all_signals_positive():
    """Two-year panel: year2 strictly better on all Piotroski dimensions."""
    rows = [
        # Year 1 — weaker
        {
            "ticker": "TST",
            "fiscal_year": 2021,
            "total_current_assets": 100,
            "total_current_liabilities": 100,
            "inventory": 10,
            "cash_and_equivalents": 5,
            "total_assets": 500,
            "total_debt": 200,
            "total_liabilities": 350,
            "shareholders_equity": 150,
            "retained_earnings": 50,
            "revenue": 1000,
            "net_income": -10,
            "operating_income": 5,
            "cogs": 800,
            "interest_expense": 2,
            "operating_cash_flow": -5,
            "capex": -10,
            "diluted_avg_shares": 1000,
            "market_cap": 400,
        },
        # Year 2 — stronger
        {
            "ticker": "TST",
            "fiscal_year": 2022,
            "total_current_assets": 150,
            "total_current_liabilities": 100,
            "inventory": 10,
            "cash_and_equivalents": 40,
            "total_assets": 500,
            "total_debt": 150,
            "total_liabilities": 300,
            "shareholders_equity": 200,
            "retained_earnings": 80,
            "revenue": 1200,
            "net_income": 40,
            "operating_income": 80,
            "cogs": 900,
            "interest_expense": 2,
            "operating_cash_flow": 60,
            "capex": -20,
            "diluted_avg_shares": 950,
            "market_cap": 500,
        },
    ]
    panel = pd.DataFrame(rows).set_index(["ticker", "fiscal_year"])
    ratios = compute_ratio_panel(panel)
    piot = compute_piotroski_panel(panel, ratios)
    score_2022 = piot.loc[("TST", 2022), "piotroski_f_score"]
    assert score_2022 == 9
