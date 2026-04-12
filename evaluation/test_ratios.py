import numpy as np
import pandas as pd

from features.ratios import compute_ratio_panel


def _panel_one_year():
    return pd.DataFrame(
        [
            {
                "ticker": "AAA",
                "fiscal_year": 2023,
                "total_current_assets": 100.0,
                "total_current_liabilities": 50.0,
                "inventory": 20.0,
                "cash_and_equivalents": 10.0,
                "total_assets": 200.0,
                "total_debt": 60.0,
                "total_liabilities": 120.0,
                "shareholders_equity": 80.0,
                "retained_earnings": 40.0,
                "revenue": 300.0,
                "net_income": 15.0,
                "operating_income": 25.0,
                "cogs": 200.0,
                "interest_expense": 5.0,
                "operating_cash_flow": 20.0,
                "capex": -8.0,
                "diluted_avg_shares": 1e9,
                "market_cap": 400.0,
            }
        ]
    ).set_index(["ticker", "fiscal_year"])


def test_current_ratio_and_roe():
    p = _panel_one_year()
    r = compute_ratio_panel(p)
    row = r.loc[("AAA", 2023)]
    assert abs(row["current_ratio"] - 2.0) < 1e-9
    assert abs(row["roe"] - (15.0 / 80.0)) < 1e-9
    assert abs(row["roa"] - (15.0 / 200.0)) < 1e-9


def test_free_cash_flow():
    p = _panel_one_year()
    r = compute_ratio_panel(p)
    row = r.loc[("AAA", 2023)]
    assert abs(row["free_cash_flow"] - 12.0) < 1e-9
