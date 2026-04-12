#!/usr/bin/env python3
"""Run the full financial intelligence pipeline (batch scoring + rankings)."""

from __future__ import annotations

import logging

from src.pipeline import run_pipeline

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    run_pipeline()
    print("Pipeline finished. See output/ for rankings_latest.csv and methodology.json.")
