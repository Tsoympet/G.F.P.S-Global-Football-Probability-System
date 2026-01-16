from __future__ import annotations

from typing import Dict, List, Optional


def _event_xg(event: Dict) -> float:
    val = event.get("xg")
    try:
        if val is not None:
            return max(float(val), 0.0)
    except (TypeError, ValueError):
        pass
    desc = (event.get("description") or event.get("type") or "").lower()
    if "penalty" in desc:
        return 0.75
    if "header" in desc:
        return 0.08
    if "shot" in desc or "goal" in desc:
        return 0.12
    return 0.0


def _team_for_event(event: Dict) -> Optional[str]:
    for key in ("team", "team_name", "teamName", "side"):
        val = event.get(key)
        if val:
            return str(val)
    return None


def compute_xg_summary(snapshot: Dict, fixture_id: Optional[str] = None) -> List[Dict]:
    fixtures = snapshot.get("fixtures", []) or []
    events = snapshot.get("events", {}) or {}
    summaries: List[Dict] = []

    for fx in fixtures:
        fid = str(fx.get("id"))
        if fixture_id and fid != str(fixture_id):
            continue

        home = fx.get("homeTeam") or "Home"
        away = fx.get("awayTeam") or "Away"

        rows = events.get(fid, []) or []
        home_xg = 0.0
        away_xg = 0.0
        home_shots = 0
        away_shots = 0
        timeline: List[Dict] = []

        for ev in rows:
            val = _event_xg(ev)
            team = _team_for_event(ev) or ""
            minute = ev.get("minute") or ev.get("time") or ev.get("clock")

            is_shot_like = val > 0
            if team and team.lower() == home.lower() and is_shot_like:
                home_xg += val
                home_shots += 1
            elif team and team.lower() == away.lower() and is_shot_like:
                away_xg += val
                away_shots += 1

            if is_shot_like:
                timeline.append(
                    {
                        "minute": minute,
                        "team": team or "Unknown",
                        "xg": round(val, 3),
                        "homeXg": round(home_xg, 3),
                        "awayXg": round(away_xg, 3),
                    }
                )

        summaries.append(
            {
                "fixtureId": fid,
                "homeTeam": home,
                "awayTeam": away,
                "xg": {"home": round(home_xg, 3), "away": round(away_xg, 3)},
                "shots": {"home": home_shots, "away": away_shots},
                "timeline": timeline,
            }
        )

    return summaries
