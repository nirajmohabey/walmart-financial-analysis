"""Rank companies by composite score (higher = better financial health in this framework)."""

from __future__ import annotations

import pandas as pd


def rank_companies(scores: pd.DataFrame, score_column: str = "composite_score") -> pd.DataFrame:
    """Sort by ``score_column`` descending and assign ``health_rank`` starting at 1 for the leader."""
    out = scores.copy()
    if score_column not in out.columns:
        raise KeyError(f"Missing score column {score_column}")
    out = out.sort_values(score_column, ascending=False, na_position="last")
    out["health_rank"] = range(1, len(out) + 1)
    return out
