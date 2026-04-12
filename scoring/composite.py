"""
Cross-sectional composite financial health score (latest fiscal year).

Each metric is converted to a 0–100 percentile score across the peer set for that run
(higher = stronger). Metrics where lower raw values are better use inverted percentiles.

Combined with optional blend of Piotroski F-Score scaled to 0–100 (F/9*100).
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def _normalize_weights(d: dict[str, float]) -> dict[str, float]:
    s = sum(max(0.0, float(v)) for v in d.values())
    if s <= 0:
        raise ValueError("Composite pillar weights sum to zero")
    return {k: max(0.0, float(v)) / s for k, v in d.items()}


def _pct_rank_high_better(series: pd.Series) -> pd.Series:
    """Map values to 0–100 by percentile rank; larger raw values score higher."""
    r = series.rank(pct=True, method="average", na_option="bottom")
    return r * 100.0


def compute_composite_scores(
    latest: pd.DataFrame,
    scoring_cfg: dict[str, Any],
) -> pd.DataFrame:
    """
    Build peer-relative health scores for one cross-section (latest fiscal year per ticker).

    Steps:
    1. For each pillar in ``scoring_cfg["pillar_metrics"]``, convert underlying ratios to
       0–100 percentile ranks **within this DataFrame** (the peer set). Higher is better;
       for debt/equity we rank ``-D/E`` (after filling missing D/E with ``inf`` so missing reads weak).
    2. Weight metrics inside each pillar, then weight pillars using ``composite_weights``.
    3. Blend with Piotroski: ``(1 - blend) * pillar_composite + blend * (F/9)*100``,
       with Piotroski term falling back to the pillar composite when F is missing.

    Returns ``df`` with added columns: ``score_*``, ``composite_score_raw``, ``piotroski_score_0_100``,
    ``composite_score``.
    """
    df = latest.copy()
    cw = scoring_cfg["composite_weights"]
    pm = scoring_cfg["pillar_metrics"]
    blend = float(scoring_cfg.get("piotroski_blend", 0.25))

    cw = _normalize_weights(cw)

    pillar_scores: dict[str, pd.Series] = {}

    # Profitability
    pw = _normalize_weights(pm["profitability"])
    sub = pd.DataFrame(
        {
            "roe": _pct_rank_high_better(df["roe"]),
            "roa": _pct_rank_high_better(df["roa"]),
            "net_profit_margin": _pct_rank_high_better(df["net_profit_margin"]),
        },
        index=df.index,
    )
    pillar_scores["profitability"] = sum(sub[k] * pw[k] for k in pw)

    # Liquidity
    lw = _normalize_weights(pm["liquidity"])
    sub = pd.DataFrame(
        {
            "current_ratio": _pct_rank_high_better(df["current_ratio"]),
            "quick_ratio": _pct_rank_high_better(df["quick_ratio"]),
        },
        index=df.index,
    )
    pillar_scores["liquidity"] = sum(sub[k] * lw[k] for k in lw)

    # Leverage (lower D/E better; higher interest coverage better)
    lev_w = _normalize_weights(pm["leverage"])
    de_inv = -df["debt_to_equity"].fillna(np.inf)
    ic = df["interest_coverage"].fillna(0.0)
    sub = pd.DataFrame(
        {
            "debt_to_equity": _pct_rank_high_better(de_inv),
            "interest_coverage": _pct_rank_high_better(ic),
        },
        index=df.index,
    )
    pillar_scores["leverage"] = sum(sub[k] * lev_w[k] for k in lev_w)

    # Efficiency
    ew = _normalize_weights(pm["efficiency"])
    inv_turn = df["inventory_turnover"].fillna(0.0)
    sub = pd.DataFrame(
        {
            "asset_turnover": _pct_rank_high_better(df["asset_turnover"]),
            "inventory_turnover": _pct_rank_high_better(inv_turn),
        },
        index=df.index,
    )
    pillar_scores["efficiency"] = sum(sub[k] * ew[k] for k in ew)

    composite = sum(pillar_scores[p] * cw[p] for p in cw)

    df["score_profitability"] = pillar_scores["profitability"]
    df["score_liquidity"] = pillar_scores["liquidity"]
    df["score_leverage"] = pillar_scores["leverage"]
    df["score_efficiency"] = pillar_scores["efficiency"]
    df["composite_score_raw"] = composite

    if "piotroski_f_score" in df.columns:
        f_scaled = (df["piotroski_f_score"] / 9.0) * 100.0
        df["piotroski_score_0_100"] = f_scaled
    else:
        df["piotroski_score_0_100"] = np.nan

    f_part = df["piotroski_score_0_100"].fillna(df["composite_score_raw"])
    df["composite_score"] = (1.0 - blend) * df["composite_score_raw"] + blend * f_part

    return df
