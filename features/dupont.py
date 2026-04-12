"""
DuPont decomposition: ROE = net_profit_margin * asset_turnover * equity_multiplier
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def dupont_decomposition(latest_ratios: pd.DataFrame) -> pd.DataFrame:
    """
    latest_ratios: index=ticker, columns include net_profit_margin, asset_turnover, equity_multiplier, roe

    Adds roe_dupont (product) and roe_dupont_residual (roe - roe_dupont).
    """
    out = latest_ratios.copy()
    npm = out["net_profit_margin"]
    ato = out["asset_turnover"]
    em = out["equity_multiplier"]
    out["roe_dupont"] = npm * ato * em
    out["roe_dupont_residual"] = out["roe"] - out["roe_dupont"]
    return out
