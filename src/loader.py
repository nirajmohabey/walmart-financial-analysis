"""
Load and normalize multi-company financial statements.

Uses yfinance (public market data). Results are cached under config data.cache_dir
for reproducible re-runs without re-downloading.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

# yfinance row labels vary by ticker; try candidates in order
_ROW_ALIASES: dict[str, list[str]] = {
    "total_current_assets": [
        "Current Assets",
        "Total Current Assets",
    ],
    "total_current_liabilities": [
        "Current Liabilities",
        "Total Current Liabilities",
    ],
    "inventory": ["Inventory"],
    "total_assets": ["Total Assets"],
    "total_debt": ["Total Debt", "Long Term Debt And Capital Lease Obligation"],
    "total_liabilities": ["Total Liabilities Net Minority Interest", "Total Liabilities"],
    "shareholders_equity": [
        "Stockholders Equity",
        "Common Stock Equity",
        "Total Equity Gross Minority Interest",
    ],
    "retained_earnings": ["Retained Earnings"],
    "revenue": ["Total Revenue", "Operating Revenue"],
    "net_income": ["Net Income", "Net Income Common Stockholders"],
    "operating_income": ["Operating Income", "EBIT"],
    "cogs": ["Cost Of Revenue", "Reconciled Cost Of Revenue", "Cost of Revenue"],
    "interest_expense": ["Interest Expense", "Interest Expense Non Operating"],
    "operating_cash_flow": [
        "Operating Cash Flow",
        "Cash Flow From Continuing Operating Activities",
    ],
    "capex": [
        "Capital Expenditure",
        "Capital Expenditures",
    ],
    "diluted_avg_shares": [
        "Diluted Average Shares",
        "Basic Average Shares",
    ],
    "cash_and_equivalents": [
        "Cash And Cash Equivalents",
        "Cash Cash Equivalents And Short Term Investments",
        "Cash Financial",
    ],
}

# Diluted shares often not on BS; we get from income statement or ticker.info
_INFO_KEYS_FOR_SHARES = ("sharesOutstanding", "impliedSharesOutstanding")


def _norm_key(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def _get_row_value(df: pd.DataFrame, candidates: list[str], year_col) -> float:
    """Extract scalar for fiscal column `year_col` from statement df (index = line items)."""
    if df is None or df.empty:
        return np.nan
    index_map = {_norm_key(i): i for i in df.index.astype(str)}
    for cand in candidates:
        nk = _norm_key(cand)
        if nk in index_map:
            raw = df.loc[index_map[nk], year_col]
            try:
                return float(raw)
            except (TypeError, ValueError):
                return np.nan
    return np.nan


def _fiscal_year_from_col(col: Any) -> int | None:
    if hasattr(col, "year"):
        return int(col.year)
    try:
        return int(pd.Timestamp(col).year)
    except Exception:
        return None


def _statement_years(*frames: pd.DataFrame) -> list[int]:
    years: set[int] = set()
    for df in frames:
        if df is None or df.empty:
            continue
        for c in df.columns:
            fy = _fiscal_year_from_col(c)
            if fy is not None:
                years.add(fy)
    return sorted(years)


def _pick_year_column(df: pd.DataFrame, year: int):
    for c in df.columns:
        fy = _fiscal_year_from_col(c)
        if fy == year:
            return c
    return None


def load_ticker_statements(
    ticker: str,
    min_year: int | None = None,
    max_year: int | None = None,
) -> pd.DataFrame:
    """
    Return panel rows: index (ticker, fiscal_year), columns = standardized fields.
    """
    t = yf.Ticker(ticker)
    bs = t.balance_sheet
    fin = t.financials
    cf = t.cashflow

    years = _statement_years(bs, fin, cf)
    if min_year is not None:
        years = [y for y in years if y >= min_year]
    if max_year is not None:
        years = [y for y in years if y <= max_year]

    rows = []
    info = {}
    try:
        info = t.info or {}
    except Exception as e:
        logger.warning("Could not fetch info for %s: %s", ticker, e)

    market_cap = float(info.get("marketCap") or np.nan)
    shares_out = None
    for k in _INFO_KEYS_FOR_SHARES:
        v = info.get(k)
        if v is not None:
            try:
                shares_out = float(v)
                break
            except (TypeError, ValueError):
                continue

    for year in years:
        bs_c = _pick_year_column(bs, year) if bs is not None and not bs.empty else None
        fin_c = _pick_year_column(fin, year) if fin is not None and not fin.empty else None
        cf_c = _pick_year_column(cf, year) if cf is not None and not cf.empty else None

        if bs_c is None and fin_c is None and cf_c is None:
            continue

        record: dict[str, Any] = {"ticker": ticker.upper(), "fiscal_year": int(year)}

        for field, cands in _ROW_ALIASES.items():
            val = np.nan
            if field in (
                "total_current_assets",
                "total_current_liabilities",
                "inventory",
                "total_assets",
                "total_debt",
                "total_liabilities",
                "shareholders_equity",
                "retained_earnings",
            ):
                val = _get_row_value(bs, cands, bs_c) if bs_c is not None else np.nan
            elif field in (
                "revenue",
                "net_income",
                "operating_income",
                "cogs",
                "interest_expense",
            ):
                val = _get_row_value(fin, cands, fin_c) if fin_c is not None else np.nan
            elif field in ("operating_cash_flow", "capex"):
                val = _get_row_value(cf, cands, cf_c) if cf_c is not None else np.nan
            elif field == "diluted_avg_shares":
                val = _get_row_value(fin, cands, fin_c) if fin_c is not None else np.nan
            elif field == "cash_and_equivalents":
                val = _get_row_value(bs, cands, bs_c) if bs_c is not None else np.nan
            record[field] = val

        if shares_out is not None and np.isnan(record.get("diluted_avg_shares", np.nan)):
            record["diluted_avg_shares"] = shares_out

        record["market_cap"] = market_cap
        rows.append(record)

    if not rows:
        return pd.DataFrame()

    out = pd.DataFrame(rows)
    out = out.sort_values("fiscal_year").reset_index(drop=True)
    return out


def _cache_key(tickers: list[str], min_y: Any, max_y: Any) -> str:
    raw = json.dumps({"t": sorted(tickers), "min": min_y, "max": max_y}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def load_multi_company_panel(
    tickers: list[str],
    cache_dir: Path,
    use_cache: bool,
    min_year: int | None = None,
    max_year: int | None = None,
) -> pd.DataFrame:
    """
    Concatenate per-ticker panels. Validate non-empty overlap.
    """
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = _cache_key([t.upper() for t in tickers], min_year, max_year)
    cache_path = cache_dir / f"panel_{key}.parquet"

    if use_cache and cache_path.exists():
        logger.info("Loading panel from cache %s", cache_path)
        cached = pd.read_parquet(cache_path)
        return cached.set_index(["ticker", "fiscal_year"]).sort_index()

    parts = []
    for raw in tickers:
        t = raw.strip().upper()
        logger.info("Downloading statements for %s", t)
        df = load_ticker_statements(t, min_year=min_year, max_year=max_year)
        if df.empty:
            logger.error("No statement data for ticker %s", t)
            raise ValueError(f"No financial statement data returned for {t}. Check ticker symbol.")
        parts.append(df)

    panel = pd.concat(parts, ignore_index=True)
    panel = panel.set_index(["ticker", "fiscal_year"]).sort_index()

    # Integrity checks
    if panel.index.duplicated().any():
        dup = panel.index[panel.index.duplicated()].tolist()
        raise ValueError(f"Duplicate ticker/year rows: {dup[:5]}")

    if use_cache:
        panel.reset_index().to_parquet(cache_path, index=False)

    return panel


def validate_panel(panel: pd.DataFrame) -> list[str]:
    """Return list of validation warnings (empty if OK)."""
    warnings: list[str] = []
    required = [
        "total_assets",
        "shareholders_equity",
        "revenue",
        "net_income",
    ]
    for col in required:
        if col not in panel.columns:
            warnings.append(f"Missing column {col}")
        elif panel[col].isna().all():
            warnings.append(f"Column {col} is all NaN")

    latest = panel.reset_index().groupby("ticker")["fiscal_year"].max()
    if latest.nunique() == 1 and len(latest) > 1:
        pass  # fine
    return warnings
