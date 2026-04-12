"""
End-to-end pipeline: load → validate → ratios → Piotroski → DuPont → composite → rank → export.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd

from features.dupont import dupont_decomposition
from features.ratios import compute_ratio_panel
from ranking.ranker import rank_companies
from scoring.composite import compute_composite_scores
from scoring.piotroski import compute_piotroski_panel
from src.config import load_config, project_root
from src.loader import load_multi_company_panel, validate_panel

logger = logging.getLogger(__name__)


def _latest_by_ticker(df: pd.DataFrame) -> pd.DataFrame:
    """Keep most recent fiscal_year per ticker (index becomes ticker)."""
    x = df.reset_index()
    return x.sort_values(["ticker", "fiscal_year"]).groupby("ticker", as_index=False).tail(1).set_index("ticker")


def run_pipeline(config_path: str = "configs/default.yaml") -> dict[str, Any]:
    root = project_root()
    cfg = load_config(config_path)

    data_cfg = cfg["data"]
    out_dir = root / cfg["output"]["dir"]
    out_dir.mkdir(parents=True, exist_ok=True)

    tickers = [str(t).strip().upper() for t in data_cfg["tickers"]]
    if len(tickers) < 5:
        raise ValueError("Configuration must include at least 5 tickers for multi-company ranking.")

    min_y = data_cfg.get("min_year")
    max_y = data_cfg.get("max_year")

    panel = load_multi_company_panel(
        tickers=tickers,
        cache_dir=root / data_cfg["cache_dir"],
        use_cache=bool(data_cfg.get("use_cache", True)),
        min_year=int(min_y) if min_y is not None else None,
        max_year=int(max_y) if max_y is not None else None,
    )

    for w in validate_panel(panel):
        logger.warning("Panel validation: %s", w)

    ratios = compute_ratio_panel(panel)
    piot = compute_piotroski_panel(panel, ratios)

    full = ratios.join(piot, how="left").join(panel, how="left")
    latest = _latest_by_ticker(full)

    latest = dupont_decomposition(latest)

    scoring_cfg = cfg["scoring"]
    scored = compute_composite_scores(latest, scoring_cfg)
    ranked = rank_companies(scored, score_column=cfg["ranking"]["score_column"])

    full.reset_index().to_csv(out_dir / "ratios_panel.csv", index=False)
    ranked.reset_index().to_csv(out_dir / "rankings_latest.csv", index=False)

    methodology = {
        "config_path": config_path,
        "tickers": tickers,
        "composite_weights": scoring_cfg["composite_weights"],
        "pillar_metrics": scoring_cfg["pillar_metrics"],
        "piotroski_blend": scoring_cfg.get("piotroski_blend"),
        "ranking": cfg["ranking"],
        "limitations": [
            "Market cap from yfinance is point-in-time at download; Altman X4 uses this value for all fiscal years shown — interpret historical Z-scores cautiously.",
            "Statement line items are mapped from yfinance labels; edge cases may yield NaN ratios.",
            "Piotroski signal 7 uses diluted_avg_shares when available; see piotroski_note on panel.",
        ],
    }
    (out_dir / "methodology.json").write_text(json.dumps(methodology, indent=2), encoding="utf-8")

    export_cols = [
        "ticker",
        "health_rank",
        "fiscal_year",
        "composite_score",
        "composite_score_raw",
        "score_profitability",
        "score_liquidity",
        "score_leverage",
        "score_efficiency",
        "piotroski_f_score",
        "roe",
        "roa",
        "current_ratio",
        "debt_to_equity",
        "altman_z_score",
    ]
    summary_df = ranked.reset_index()
    if "ticker" not in summary_df.columns:
        summary_df = summary_df.rename(columns={"index": "ticker"})
    summary_df = summary_df[[c for c in export_cols if c in summary_df.columns]]
    summary = {
        "n_companies": len(ranked),
        "rankings": summary_df.to_dict(orient="records"),
    }
    (out_dir / "run_summary.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")

    logger.info("Wrote outputs to %s", out_dir)
    return {"ranked": ranked, "full_panel": full, "output_dir": str(out_dir)}
