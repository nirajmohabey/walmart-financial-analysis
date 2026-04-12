"""
Financial ratios — consistent snake_case names across pipeline, CSV, JSON, and UI.

Formulas follow standard textbook definitions. Where inputs are missing, ratio is NaN
(not imputed with placeholders).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _safe_div(num: float, den: float) -> float:
    if den is None or num is None:
        return np.nan
    try:
        d = float(den)
        n = float(num)
        if np.isnan(d) or np.isnan(n) or d == 0:
            return np.nan
        return n / d
    except (TypeError, ValueError):
        return np.nan


def _avg(a: float, b: float) -> float:
    if np.isnan(a) and np.isnan(b):
        return np.nan
    if np.isnan(a):
        return float(b)
    if np.isnan(b):
        return float(a)
    return (float(a) + float(b)) / 2.0


def compute_ratio_panel(panel: pd.DataFrame) -> pd.DataFrame:
    """
    panel: MultiIndex (ticker, fiscal_year), columns produced by ``src.loader``.

    Returns a new frame with the same index and columns for liquidity, leverage, profitability,
    efficiency, cash-flow metrics, and Altman Z (public formula) where inputs exist.
    """
    if not isinstance(panel.index, pd.MultiIndex):
        raise TypeError("panel must use MultiIndex [ticker, fiscal_year]")
    if not panel.index.names == ["ticker", "fiscal_year"]:
        panel = panel.copy()
        panel.index.names = ["ticker", "fiscal_year"]

    rows: list[dict] = []

    for ticker in panel.index.get_level_values(0).unique():
        sub = panel.xs(ticker, level=0).sort_index()
        years = list(sub.index)

        for i, year in enumerate(years):
            r = sub.loc[year]
            prev = sub.loc[years[i - 1]] if i > 0 else None

            tca = r.get("total_current_assets", np.nan)
            tcl = r.get("total_current_liabilities", np.nan)
            inv = r.get("inventory", np.nan)
            cash = r.get("cash_and_equivalents", np.nan)
            ta = r.get("total_assets", np.nan)
            td = r.get("total_debt", np.nan)
            tl = r.get("total_liabilities", np.nan)
            eq = r.get("shareholders_equity", np.nan)
            re = r.get("retained_earnings", np.nan)
            rev = r.get("revenue", np.nan)
            ni = r.get("net_income", np.nan)
            oi = r.get("operating_income", np.nan)
            cogs = r.get("cogs", np.nan)
            ie = r.get("interest_expense", np.nan)
            ocf = r.get("operating_cash_flow", np.nan)
            capex = r.get("capex", np.nan)
            mcap = r.get("market_cap", np.nan)

            wc = tca - tcl if not (np.isnan(tca) or np.isnan(tcl)) else np.nan

            rec: dict = {
                "ticker": ticker,
                "fiscal_year": int(year),
                "working_capital": wc,
                "current_ratio": _safe_div(tca, tcl),
                "quick_ratio": _safe_div(tca - inv if not np.isnan(inv) else np.nan, tcl),
                "cash_ratio": _safe_div(cash, tcl),
                "debt_to_equity": _safe_div(td, eq),
                "debt_to_assets": _safe_div(td, ta),
                "equity_multiplier": _safe_div(ta, eq),
                "gross_margin": _safe_div(rev - cogs, rev) if not np.isnan(cogs) else np.nan,
                "net_profit_margin": _safe_div(ni, rev),
                "roa": _safe_div(ni, ta),
                "roe": _safe_div(ni, eq),
                "asset_turnover": _safe_div(rev, ta),
                "operating_cf_margin": _safe_div(ocf, rev),
            }

            # Inventory turnover = COGS / average inventory
            inv_prev = prev.get("inventory", np.nan) if prev is not None else np.nan
            inv_avg = _avg(inv, inv_prev)
            rec["inventory_turnover"] = _safe_div(cogs, inv_avg)

            # Interest coverage = EBIT / |interest expense|
            if ie is not None and not np.isnan(ie) and float(ie) != 0:
                rec["interest_coverage"] = _safe_div(oi, abs(float(ie)))
            else:
                rec["interest_coverage"] = np.nan

            # FCF: capex often reported negative in yfinance
            if not np.isnan(ocf):
                cap = 0.0 if np.isnan(capex) else float(capex)
                rec["free_cash_flow"] = float(ocf) + cap
                rec["free_cash_flow_margin"] = _safe_div(rec["free_cash_flow"], rev)
            else:
                rec["free_cash_flow"] = np.nan
                rec["free_cash_flow_margin"] = np.nan

            # Altman Z (public manufacturing variant; used widely for large caps)
            # Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5
            # X4 = Market Value of Equity / Total Liabilities
            x1 = _safe_div(wc, ta)
            x2 = _safe_div(re, ta)
            x3 = _safe_div(oi, ta)
            x4 = _safe_div(mcap, tl)
            x5 = _safe_div(rev, ta)
            if any(np.isnan(v) for v in (x1, x2, x3, x4, x5)):
                rec["altman_z_score"] = np.nan
            else:
                rec["altman_z_score"] = (
                    1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 1.0 * x5
                )

            if not np.isnan(rec["altman_z_score"]):
                z = rec["altman_z_score"]
                if z > 2.99:
                    rec["altman_risk_zone"] = "safe"
                elif z > 1.81:
                    rec["altman_risk_zone"] = "grey"
                else:
                    rec["altman_risk_zone"] = "distress"
            else:
                rec["altman_risk_zone"] = np.nan

            rows.append(rec)

    out = pd.DataFrame(rows).set_index(["ticker", "fiscal_year"]).sort_index()
    return out


def latest_fiscal_slice(ratios: pd.DataFrame) -> pd.DataFrame:
    """One row per ticker: most recent fiscal_year."""
    return ratios.reset_index().sort_values("fiscal_year").groupby("ticker", as_index=False).tail(1).set_index("ticker")
