"""
Streamlit UI: multi-company rankings, score breakdown, time series from cached pipeline outputs.
Run from project root: streamlit run src/dashboard.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _outputs_exist() -> bool:
    return (ROOT / "output" / "rankings_latest.csv").is_file() and (
        ROOT / "output" / "ratios_panel.csv"
    ).is_file()


def _run_pipeline() -> None:
    from src.pipeline import run_pipeline

    run_pipeline()


st.set_page_config(page_title="Peer financial rankings", layout="wide")
st.title("Peer financial rankings")
st.caption("Outputs mirror the batch pipeline: percentile pillars vs your config peer set + Piotroski blend · yfinance")

col_a, col_b = st.columns([1, 3])
with col_a:
    if st.button("Recompute pipeline", type="primary"):
        with st.spinner("Running pipeline…"):
            _run_pipeline()
        st.success("Done.")
with col_b:
    if not _outputs_exist():
        st.warning("No outputs yet — run **Recompute pipeline** (network if cache empty).")

if not _outputs_exist():
    st.stop()

rankings = pd.read_csv(ROOT / "output" / "rankings_latest.csv")
panel = pd.read_csv(ROOT / "output" / "ratios_panel.csv")

r_sorted = rankings.sort_values("health_rank")
top = r_sorted.iloc[0]
bot = r_sorted.iloc[-1]
st.info(
    f"**#1 (this peer set):** {top['ticker']} — composite **{top['composite_score']:.1f}** "
    f"(pillars: P {top['score_profitability']:.0f} · Lq {top['score_liquidity']:.0f} · "
    f"Lv {top['score_leverage']:.0f} · Ef {top['score_efficiency']:.0f}). "
    f"**Last:** {bot['ticker']} — **{bot['composite_score']:.1f}**."
)

st.subheader("Full table (export: output/rankings_latest.csv)")
display_cols = [
    c
    for c in [
        "ticker",
        "health_rank",
        "fiscal_year",
        "composite_score",
        "composite_score_raw",
        "piotroski_f_score",
        "score_profitability",
        "score_liquidity",
        "score_leverage",
        "score_efficiency",
        "roe",
        "roa",
        "current_ratio",
        "debt_to_equity",
        "altman_z_score",
    ]
    if c in rankings.columns
]
st.dataframe(rankings[display_cols].sort_values("health_rank"), use_container_width=True, hide_index=True)

tickers = sorted(panel["ticker"].unique().tolist())
sel = st.multiselect("Compare companies over time", options=tickers, default=tickers[: min(3, len(tickers))])
metric = st.selectbox(
    "Metric",
    options=[
        "roe",
        "roa",
        "current_ratio",
        "debt_to_equity",
        "composite_score_raw",
        "piotroski_f_score",
        "altman_z_score",
    ],
    format_func=lambda x: x.replace("_", " ").title(),
)

if sel:
    sub = panel[panel["ticker"].isin(sel)].sort_values(["ticker", "fiscal_year"])
    if metric in sub.columns and sub[metric].notna().any():
        fig = px.line(
            sub,
            x="fiscal_year",
            y=metric,
            color="ticker",
            markers=True,
            title=f"{metric.replace('_', ' ').title()} — fiscal year",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Selected metric not available for these rows.")

st.subheader("DuPont identity check (latest fiscal year)")
dup_cols = [c for c in ["ticker", "fiscal_year", "roe", "roe_dupont", "roe_dupont_residual"] if c in rankings.columns]
if dup_cols:
    st.dataframe(rankings[dup_cols].sort_values("ticker"), use_container_width=True, hide_index=True)

with st.expander("Methodology"):
    p = ROOT / "output" / "methodology.json"
    if p.is_file():
        st.code(p.read_text(encoding="utf-8"), language="json")
