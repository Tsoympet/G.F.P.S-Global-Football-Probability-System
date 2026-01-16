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
    args = parser.parse_args()

    if args.command == "ingest_fixtures":
        result = ingest_fixtures()
    elif args.command == "ingest_live":
        result = ingest_live()
    elif args.command == "build_features":
        result = build_features()
    else:
        raise SystemExit(1)
    print(json.dumps(result, default=str, indent=2))


if __name__ == "__main__":
    main()
