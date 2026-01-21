from __future__ import annotations

import argparse
import json

from .ingestion_pipeline import build_features, ingest_fixtures, ingest_live


def main():
    parser = argparse.ArgumentParser(description="GFPS ingestion pipeline")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("ingest_fixtures")
    sub.add_parser("ingest_live")
    sub.add_parser("build_features")
    sub.add_parser("ingest_historical_odds", help="Load historical matches with bookmaker odds")
    sub.add_parser("scrape_predict")
    args = parser.parse_args()

    if args.command == "ingest_fixtures":
        result = ingest_fixtures()
    elif args.command == "ingest_live":
        result = ingest_live()
    elif args.command == "build_features":
        result = build_features()
    elif args.command == "ingest_historical_odds":
        from backend.ingestion_pipeline import ingest_historical_odds

        result = ingest_historical_odds()
    elif args.command == "scrape_predict":
        from backend.web_scraper_engine import run_web_scraper_engine

        result = run_web_scraper_engine()
    else:
        raise SystemExit(1)
    print(json.dumps(result, default=str, indent=2))


if __name__ == "__main__":
    main()
