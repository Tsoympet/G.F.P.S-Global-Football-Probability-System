import asyncio
import os
from typing import Optional, List, Dict

import httpx
from sqlalchemy.orm import Session
from sqlalchemy import select

from .db import SessionLocal
from .models import AlertRule, AlertEvent, Device
from .prediction_engine import predict_market
from .stats_context import build_poisson_context
from .push_notify import send_fcm_push

ALERT_ENGINE_ENABLED = os.getenv("ALERT_ENGINE", "false").lower() in ("1", "true", "yes")
ALERT_ENGINE_INTERVAL_SEC = int(os.getenv("ALERT_ENGINE_INTERVAL_SEC", "120"))

APIFOOTBALL_KEY = os.getenv("APIFOOTBALL_KEY", "")


async def fetch_live_candidates() -> List[dict]:
    """
    Fetch live fixtures + odds from API-Football.
    This is a simplified version: it pulls all live fixtures, then odds for each.
    """
    if not APIFOOTBALL_KEY:
        return []

    headers = {"x-apisports-key": APIFOOTBALL_KEY}

    async with httpx.AsyncClient(timeout=20) as client:
        # 1) get live fixtures
        try:
            r_fx = await client.get(
                "https://v3.football.api-sports.io/fixtures",
                headers=headers,
                params={"live": "all"},
            )
            r_fx.raise_for_status()
            data_fx = r_fx.json()
        except Exception as e:
            print("[alert_engine] fixtures error:", e)
            return []

        fixtures = []
        for item in data_fx.get("response", []):
            f = item["fixture"]
            l = item["league"]
            h = item["teams"]["home"]
            a = item["teams"]["away"]
            fixtures.append(
                {
                    "fixture_id": f["id"],
                    "league_id": l["id"],
                    "league": l["name"],
                    "home": h["name"],
                    "away": a["name"],
                }
            )

        candidates: List[dict] = []

        # 2) for each fixture, get odds (could be heavy in real use)
        for fx in fixtures:
            try:
                r_odds = await client.get(
                    "https://v3.football.api-sports.io/odds",
                    headers=headers,
                    params={"fixture": fx["fixture_id"]},
                )
                r_odds.raise_for_status()
                data_odds = r_odds.json()
            except Exception as e:
                print("[alert_engine] odds error:", e)
                continue

            markets: List[dict] = []
            for resp in data_odds.get("response", []):
                for book in resp.get("bookmakers", []):
                    bname = book.get("name", "UnknownBook")
                    for m in book.get("bets", []):
                        mname = m.get("name", "Unknown")
                        selections = []
                        for v in m.get("values", []):
                            try:
                                price = float(v.get("odd") or 0)
                            except Exception:
                                continue
                            if price <= 0:
                                continue
                            selections.append(
                                {
                                    "outcome": v.get("value"),
                                    "odds": price,
                                }
                            )
                        markets.append(
                            {
                                "bookmaker": bname,
                                "market": mname,
                                "selections": selections,
                            }
                        )

            if markets:
                cand = fx.copy()
                cand["markets"] = markets
                candidates.append(cand)

        return candidates


def match_text_filter(value: Optional[str], subject: str) -> bool:
    if not value:
        return True
    return value.lower() in subject.lower()


def evaluate_rule(rule: AlertRule, cand: dict, db: Session) -> List[AlertEvent]:
    """
    Given a rule and a candidate (fixture + markets),
    return a list of AlertEvent objects (not committed) for matches.
    """
    events: List[AlertEvent] = []

    # basic filters (league, team)
    if rule.league_filter and not match_text_filter(rule.league_filter, cand["league"]):
        return events

    if rule.team_filter:
        team_ok = (
            match_text_filter(rule.team_filter, cand["home"])
            or match_text_filter(rule.team_filter, cand["away"])
        )
        if not team_ok:
            return events

    league_id = str(cand["league_id"])
    home = cand["home"]
    away = cand["away"]

    for m in cand.get("markets", []):
        mname = m["market"]

        if rule.market_filter and not match_text_filter(rule.market_filter, mname):
            continue

        # build Poisson context once per fixture
        ctx = build_poisson_context(db, league_id, home, away)

        # map outcome->odds
        sel_map: Dict[str, float] = {
            s["outcome"]: s["odds"] for s in m.get("selections", [])
        }

        # Let prediction engine calculate:
        preds = predict_market(mname, sel_map, ctx)

        for outcome, odds in sel_map.items():
            if rule.outcome_filter and not match_text_filter(rule.outcome_filter, outcome):
                continue

            info = preds.get(outcome)
            if not info:
                continue
            prob = info["prob"]
            ev = info["ev"]

            if rule.min_odds is not None and odds < rule.min_odds:
                continue
            if rule.max_odds is not None and odds > rule.max_odds:
                continue
            if rule.min_ev is not None and ev < rule.min_ev:
                continue

            e = AlertEvent(
                rule_id=rule.id,
                user_id=rule.user_id,
                fixture_id=str(cand["fixture_id"]),
                market=mname,
                outcome=outcome,
                odds=odds,
                prob=prob,
                ev=ev,
                meta={
                    "league": cand["league"],
                    "league_id": cand["league_id"],
                    "home": home,
                    "away": away,
                },
            )
            events.append(e)

    return events


async def alert_worker_loop():
    if not ALERT_ENGINE_ENABLED:
        print("[alert_engine] Disabled via ALERT_ENGINE env")
        return

    print("[alert_engine] Started")
    while True:
        try:
            candidates = await fetch_live_candidates()
            if not candidates:
                await asyncio.sleep(ALERT_ENGINE_INTERVAL_SEC)
                continue

            with SessionLocal() as db:
                rules = db.scalars(
                    select(AlertRule).where(AlertRule.is_active == True)  # noqa: E712
                ).all()

                for cand in candidates:
                    for rule in rules:
                        events = evaluate_rule(rule, cand, db)
                        if not events:
                            continue

                        for evt in events:
                            db.add(evt)
                        db.commit()

                        # push notifications
                        from .models import Device

                        devices = db.scalars(
                            select(Device).where(Device.user_id == rule.user_id)
                        ).all()
                        tokens = [d.token for d in devices if d.platform in ("android", "ios")]

                        if tokens:
                            # just describe first event in push text
                            e0 = events[0]
                            body = (
                                f"{e0.meta.get('home')}–{e0.meta.get('away')}: "
                                f"{e0.market} {e0.outcome} @ {e0.odds:.2f} "
                                f"(EV≈{e0.ev:.2f})"
                            )
                            await send_fcm_push(
                                tokens,
                                title="GFPS Alert",
                                body=body,
                                data={"fixture_id": e0.fixture_id, "rule_id": e0.rule_id},
                            )

        except Exception as e:
            print("[alert_engine] ERROR:", e)

        await asyncio.sleep(ALERT_ENGINE_INTERVAL_SEC)


def start_alert_engine_background(loop: asyncio.AbstractEventLoop):
    if not ALERT_ENGINE_ENABLED:
        return
    loop.create_task(alert_worker_loop())
