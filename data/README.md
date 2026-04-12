# Data directory

- **`cache/`** — Created automatically. Downloaded statement panels are cached as Parquet for reproducible re-runs (`configs/default.yaml` → `data.use_cache`).
- **Source** — Statements are pulled at runtime from **yfinance** (public Yahoo Finance data). No proprietary files are bundled.
- **Minimum** — Configure at least **five** tickers in `configs/default.yaml` under `data.tickers`.

To force a fresh download, delete `data/cache/*.parquet` or set `data.use_cache: false` (not recommended for large batches).
