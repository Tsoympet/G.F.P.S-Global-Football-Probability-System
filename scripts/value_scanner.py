"""
scripts/value_scanner.py

GFPS Value Scanner

Χρησιμοποιεί τα ML μοντέλα (1X2, Over/Under, GG) + live odds από DB
για να βρει EV+ ευκαιρίες per league / bookmaker.

EV υπολογισμός:
  EV = odds * prob - 1

π.χ. odds 2.10, prob 0.55 -> EV = 2.10 * 0.55 - 1 = 0.155 (δηλαδή +15.5%)

Μπορείς να τρέξεις:
  python scripts/value_scanner.py --min-ev 0.05 --limit 50
"""

import argparse
from typing import List, Dict, Any

from backend.db import SessionLocal
from backend.models import LiveOdds  # adjust if needed
from backend import ml_predict


def compute_ev(odds: float, prob: float) -> float:
    if odds is None or odds <= 1.0 or prob <= 0.0:
        return -999.0
    return odds * prob - 1.0


def scan_value_bets(
    min_ev: float = 0.05,
    league_filter: str | None = None,
    bookmaker_filter: str | None = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        q = db.query(LiveOdds)
        # μόνο live ή upcoming
        q = q.filter(LiveOdds.is_live == True)

        if league_filter:
            q = q.filter(LiveOdds.league.ilike(f"%{league_filter}%"))
        if bookmaker_filter:
            q = q.filter(LiveOdds.bookmaker.ilike(f"%{bookmaker_filter}%"))

        rows = q.limit(2000).all()
    finally:
        db.close()

    print(f"[GFPS-VALUE] Loaded {len(rows)} live odds rows from DB.")

    results: List[Dict[str, Any]] = []

    for row in rows:
        league = row.league or "Unknown"

        try:
            # ML probabilities
            p1, px, p2 = ml_predict.predict_1x2_proba(
                league,
                row.odds_1,
                row.odds_x,
                row.odds_2,
                row.odds_over25,
                row.odds_under25,
                row.odds_gg,
                row.odds_ng,
            )
            pov = ml_predict.predict_over25_proba(
                league,
                row.odds_1,
                row.odds_x,
                row.odds_2,
                row.odds_over25,
                row.odds_under25,
                row.odds_gg,
                row.odds_ng,
            )
            pgg = ml_predict.predict_gg_proba(
                league,
                row.odds_1,
                row.odds_x,
                row.odds_2,
                row.odds_over25,
                row.odds_under25,
                row.odds_gg,
                row.odds_ng,
            )
        except Exception as e:
            print(f"[GFPS-VALUE] ML predict error on fixture {row.fixture_id}: {e}")
            continue

        # Υπολογισμός EV για κάθε outcome
        candidates = []

        ev_1 = compute_ev(row.odds_1, p1)
        ev_x = compute_ev(row.odds_x, px)
        ev_2 = compute_ev(row.odds_2, p2)
        ev_over = compute_ev(row.odds_over25, pov)
        ev_under = compute_ev(row.odds_under25, 1.0 - pov)
        ev_gg = compute_ev(row.odds_gg, pgg)
        ev_ng = compute_ev(row.odds_ng, 1.0 - pgg)

        candidates.extend(
            [
                ("1X2", "1", row.odds_1, p1, ev_1),
                ("1X2", "X", row.odds_x, px, ev_x),
                ("1X2", "2", row.odds_2, p2, ev_2),
                ("O/U 2.5", "Over 2.5", row.odds_over25, pov, ev_over),
                ("O/U 2.5", "Under 2.5", row.odds_under25, 1.0 - pov, ev_under),
                ("GG/NG", "GG", row.odds_gg, pgg, ev_gg),
                ("GG/NG", "NG", row.odds_ng, 1.0 - pgg, ev_ng),
            ]
        )

        for market, outcome, odds, prob, ev in candidates:
            if ev >= min_ev:
                results.append(
                    {
                        "fixture_id": row.fixture_id,
                        "league": row.league,
                        "league_id": row.league_id,
                        "home": row.home,
                        "away": row.away,
                        "bookmaker": row.bookmaker,
                        "market": market,
                        "outcome": outcome,
                        "odds": float(odds),
                        "prob": float(prob),
                        "ev": float(ev),
                    }
                )

    # sort by EV desc, limit
    results.sort(key=lambda x: x["ev"], reverse=True)
    return results[:limit]


def print_value_bets(bets: List[Dict[str, Any]]):
    if not bets:
        print("[GFPS-VALUE] No EV+ opportunities found for given filters.")
        return

    print("\n[GFPS-VALUE] Top EV+ opportunities:")
    for b in bets:
        print(
            f"[{b['league']} - {b['bookmaker']}] "
            f"{b['home']} vs {b['away']} | "
            f"{b['market']} {b['outcome']} @ {b['odds']:.2f} | "
            f"p={b['prob']:.3f} | EV={b['ev']:.3f}"
        )


def main():
    parser = argparse.ArgumentParser(description="GFPS Value Scanner")
    parser.add_argument(
        "--min-ev",
        type=float,
        default=0.05,
        help="Minimum EV threshold (e.g. 0.05 = +5%)",
    )
    parser.add_argument(
        "--league",
        type=str,
        default=None,
        help="Filter league name (contains)",
    )
    parser.add_argument(
        "--bookmaker",
        type=str,
        default=None,
        help="Filter bookmaker name (contains)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum number of results to show",
    )

    args = parser.parse_args()

    print(
        f"[GFPS-VALUE] Scanning for EV >= {args.min_ev:.3f} "
        f"(league={args.league}, bookmaker={args.bookmaker})"
    )

    bets = scan_value_bets(
        min_ev=args.min_ev,
        league_filter=args.league,
        bookmaker_filter=args.bookmaker,
        limit=args.limit,
    )
    print_value_bets(bets)


if __name__ == "__main__":
    main()
