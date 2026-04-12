import pandas as pd

from features.dupont import dupont_decomposition


def test_dupont_identity():
    latest = pd.DataFrame(
        {
            "net_profit_margin": [0.05],
            "asset_turnover": [2.0],
            "equity_multiplier": [3.0],
            "roe": [0.30],
        },
        index=["X"],
    )
    out = dupont_decomposition(latest)
    assert abs(out.loc["X", "roe_dupont"] - 0.30) < 1e-12
    assert abs(out.loc["X", "roe_dupont_residual"]) < 1e-12
