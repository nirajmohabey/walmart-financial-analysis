"""
Piotroski F-Score (original 9 binary signals), computed year-over-year.

Reference: Piotroski, J. (2000). Value investing: The use of historical financial
statement information to separate winners from losers.

Signals (1 point each if condition met for fiscal year t vs t-1):
1. Positive ROA: NetIncome_t / TotalAssets_t > 0
2. Positive operating cash flow: OCF_t > 0
3. ROA improving: ROA_t > ROA_{t-1}
4. Accruals quality: OCF_t > NetIncome_t
5. Leverage improving: Long-term leverage lower — we use TotalDebt/TotalAssets_t < same ratio_{t-1}
6. Liquidity improving: CurrentRatio_t > CurrentRatio_{t-1}
7. No dilution: DilutedAvgShares_t <= DilutedAvgShares_{t-1} (missing share data → signal not counted, see below)
8. Gross margin improving: GM_t > GM_{t-1}
9. Asset turnover improving: AT_t > AT_{t-1}

If ``diluted_avg_shares`` is missing for either year t or t-1, signal 7 is scored as 0;
``piotroski_note`` records whether share data was available for that check.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _roa(ni: float, ta: float) -> float:
    if ta is None or ta == 0 or (isinstance(ta, float) and np.isnan(ta)):
        return np.nan
    if ni is None or (isinstance(ni, float) and np.isnan(ni)):
        return np.nan
    return float(ni) / float(ta)


def compute_piotroski_panel(
    fundamentals: pd.DataFrame,
    ratios: pd.DataFrame,
) -> pd.DataFrame:
    """
    Join fundamentals to selected ratio columns, then walk each ticker's fiscal years in order.

    The first fiscal year per ticker has no prior period: ``piotroski_f_score`` is NaN and
    ``piotroski_note`` is ``no_prior_year``. Later years receive an integer 0–9 sum of binary signals.
    """
    df = fundamentals.join(ratios[["current_ratio", "gross_margin", "asset_turnover"]], how="inner")
    df = df.sort_index()

    records = []
    for ticker in df.index.get_level_values(0).unique():
        sub = df.xs(ticker, level=0).sort_index()
        years = list(sub.index)
        for i, y in enumerate(years):
            row = sub.loc[y]
            if i == 0:
                records.append(
                    {
                        "ticker": ticker,
                        "fiscal_year": int(y),
                        "piotroski_f_score": np.nan,
                        "piotroski_shares_used": False,
                        "piotroski_note": "no_prior_year",
                    }
                )
                continue

            p = sub.loc[years[i - 1]]

            ni, ta, ocf = row.get("net_income"), row.get("total_assets"), row.get("operating_cash_flow")
            ni_p, ta_p = p.get("net_income"), p.get("total_assets")

            roa = _roa(ni, ta)
            roa_p = _roa(ni_p, ta_p)

            def _td_a(z) -> float:
                tdd, ta_ = z.get("total_debt", np.nan), z.get("total_assets", np.nan)
                if np.isnan(tdd) or np.isnan(ta_) or float(ta_) == 0:
                    return np.nan
                return float(tdd) / float(ta_)

            td_a, td_a_p = _td_a(row), _td_a(p)

            s1 = 1 if (not np.isnan(roa) and roa > 0) else 0
            s2 = 1 if (not np.isnan(ocf) and float(ocf) > 0) else 0
            s3 = 1 if (not np.isnan(roa) and not np.isnan(roa_p) and roa > roa_p) else 0
            s4 = 1 if (not np.isnan(ocf) and not np.isnan(ni) and float(ocf) > float(ni)) else 0
            s5 = 1 if (not np.isnan(td_a) and not np.isnan(td_a_p) and float(td_a) < float(td_a_p)) else 0
            cr, cr_p = row.get("current_ratio"), p.get("current_ratio")
            s6 = 1 if (not np.isnan(cr) and not np.isnan(cr_p) and float(cr) > float(cr_p)) else 0

            sh, sh_p = row.get("diluted_avg_shares"), p.get("diluted_avg_shares")
            shares_ok = not (np.isnan(sh) or np.isnan(sh_p))
            s7 = 1 if shares_ok and float(sh) <= float(sh_p) else 0

            gm, gm_p = row.get("gross_margin"), p.get("gross_margin")
            s8 = 1 if (not np.isnan(gm) and not np.isnan(gm_p) and float(gm) > float(gm_p)) else 0

            at, at_p = row.get("asset_turnover"), p.get("asset_turnover")
            s9 = 1 if (not np.isnan(at) and not np.isnan(at_p) and float(at) > float(at_p)) else 0

            total = s1 + s2 + s3 + s4 + s5 + s6 + s7 + s8 + s9

            records.append(
                {
                    "ticker": ticker,
                    "fiscal_year": int(y),
                    "piotroski_f_score": int(total),
                    "piotroski_shares_used": bool(shares_ok and s7 == 1),
                    "piotroski_note": "ok" if shares_ok else "shares_missing_signal7_unverified",
                    "piotroski_s1_roa_positive": s1,
                    "piotroski_s2_cfo_positive": s2,
                    "piotroski_s3_roa_improving": s3,
                    "piotroski_s4_accrual_quality": s4,
                    "piotroski_s5_leverage_improving": s5,
                    "piotroski_s6_liquidity_improving": s6,
                    "piotroski_s7_no_dilution": s7,
                    "piotroski_s8_margin_improving": s8,
                    "piotroski_s9_turnover_improving": s9,
                }
            )

    out = pd.DataFrame(records).set_index(["ticker", "fiscal_year"])
    return out
