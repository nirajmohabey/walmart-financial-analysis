"""Command-line entry: run scoring pipeline."""

from __future__ import annotations

import argparse
import logging

from src.config import project_root
from src.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Financial health scoring and ranking pipeline")
    parser.add_argument(
        "--config",
        default="configs/default.yaml",
        help="Path to YAML config (relative to project root)",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    out = run_pipeline(args.config)
    root = project_root()
    print(f"Done. Outputs written under {out['output_dir']}")
    print(f"Project root: {root}")


if __name__ == "__main__":
    main()
