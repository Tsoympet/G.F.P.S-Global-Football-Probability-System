"""
scripts/value_scanner.py

GFPS Value Scanner

Χρησιμοποιεί τα ML μοντέλα + live odds από DB για να βρει EV+ bets
και τα γράφει στον πίνακα value_picks, ώστε να είναι ορατά στο API.

EV = odds * prob - 1
"""

import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Any

from backend.db import SessionLocal
from backend.models import LiveOdds, ValuePick  # adjust import if needed
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
                        "fixture_id": str(row.fixture_id),
                        "league": row.league,
                        "league_id": str(row.league_id),
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

    results.sort(key=lambda x: x["ev"], reverse=True)
    return results[:limit]


def store_value_bets(bets: List[Dict[str, Any]], ttl_hours: int = 24):
    """
    Σβήνει παλιά picks και σώζει τα current EV+.
    """
    db = SessionLocal()
    try:
        # καθάρισμα παλιών > ttl_hours
        cutoff = datetime.utcnow() - timedelta(hours=ttl_hours)
        deleted = (
            db.query(ValuePick)
            .filter(ValuePick.created_at < cutoff)
            .delete(synchronize_session=False)
        )
        if deleted:
            print(f"[GFPS-VALUE] Deleted {deleted} old value picks.")

        for b in bets:
            vp = ValuePick(
                fixture_id=b["fixture_id"],
                league=b["league"],
                league_id=b["league_id"],
                home=b["home"],
                away=b["away"],
                bookmaker=b["bookmaker"],
                market=b["market"],
                outcome=b["outcome"],
                odds=b["odds"],
                prob=b["prob"],
                ev=b["ev"],
                source="ml_scanner",
                is_live=True,
            )
            db.add(vp)

        db.commit()
        print(f"[GFPS-VALUE] Stored {len(bets)} value picks.")
    finally:
        db.close()


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
        help="Maximum number of results to keep/show",
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
    store_value_bets(bets)


if __name__ == "__main__":
    main()
