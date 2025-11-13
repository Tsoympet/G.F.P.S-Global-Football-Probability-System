import math
from typing import Dict


def poisson_p(k: int, lam: float) -> float:
    return math.exp(-lam) * lam**k / math.factorial(k)


def goal_dist(lam: float, max_goals: int = 10) -> Dict[int, float]:
    probs: Dict[int, float] = {}
    total = 0.0
    for k in range(0, max_goals + 1):
        p = poisson_p(k, lam)
        probs[k] = p
        total += p
    for k in probs:
        probs[k] /= total
    return probs


def prob_1x2(lam_home: float, lam_away: float, max_goals: int = 10) -> Dict[str, float]:
    dh = goal_dist(lam_home, max_goals)
    da = goal_dist(lam_away, max_goals)
    p1 = px = p2 = 0.0
    for i, pi in dh.items():
        for j, pj in da.items():
            p = pi * pj
            if i > j:
                p1 += p
            elif i == j:
                px += p
            else:
                p2 += p
    return {"1": p1, "X": px, "2": p2}


def prob_over_under(lam_home: float, lam_away: float, line: float = 2.5, max_goals: int = 10) -> Dict[str, float]:
    total_lam = lam_home + lam_away
    dt = goal_dist(total_lam, max_goals)
    p_over = p_under = 0.0
    for k, p in dt.items():
        if k > line:
            p_over += p
        else:
            p_under += p
    return {f"over {line}": p_over, f"under {line}": p_under}


def prob_gg(lam_home: float, lam_away: float, max_goals: int = 10) -> Dict[str, float]:
    dh = goal_dist(lam_home, max_goals)
    da = goal_dist(lam_away, max_goals)
    p_gg = p_ng = 0.0
    for i, pi in dh.items():
        for j, pj in da.items():
            p = pi * pj
            if i >= 1 and j >= 1:
                p_gg += p
            else:
                p_ng += p
    return {"GG": p_gg, "NG": p_ng}


def base_prob_from_odds(odds: float) -> float:
    if odds <= 0:
        return 0.5
    return max(0.01, min(0.99, 1.0 / odds))


def ev(prob: float, odds: float) -> float:
    return prob * odds - 1.0


def predict_market(market: str, selections: Dict[str, float], context: Dict) -> Dict[str, Dict]:
    """
    selections: { outcome_label: odds }
    context: may include
      - lam_home, lam_away
      - home_attack, away_attack
      - home_defense, away_defense
      - avg_goals_home_league, avg_goals_away_league
    """
    out: Dict[str, Dict] = {}

    lam_home = context.get("lam_home")
    lam_away = context.get("lam_away")

    if lam_home is None or lam_away is None:
        home_attack = context.get("home_attack", 1.0)
        away_attack = context.get("away_attack", 1.0)
        home_defense = context.get("home_defense", 1.0)
        away_defense = context.get("away_defense", 1.0)
        avg_home = context.get("avg_goals_home_league", 1.5)
        avg_away = context.get("avg_goals_away_league", 1.2)

        lam_home = avg_home * home_attack * (1.0 / (away_defense or 1.0))
        lam_away = avg_away * away_attack * (1.0 / (home_defense or 1.0))

    m_lower = (market or "").lower()

    # 1X2
    if m_lower in ["1x2", "match winner", "full time result"]:
        probs_1x2 = prob_1x2(lam_home, lam_away)
        for label, odds in selections.items():
            base_label = label.strip().upper()
            p = probs_1x2.get(base_label)
            if p is None:
                p = base_prob_from_odds(odds)
            out[label] = {"prob": p, "ev": ev(p, odds)}
        return out

    # Over/Under
    if m_lower.startswith("over/under") or "over" in m_lower or "under" in m_lower:
        line = 2.5
        for k in selections.keys():
            txt = k.lower()
            for candidate in [0.5, 1.5, 2.5, 3.5, 4.5]:
                if str(candidate) in txt:
                    line = candidate
                    break
        probs_ou = prob_over_under(lam_home, lam_away, line)
        for label, odds in selections.items():
            base_label = label.lower()
            key = None
            if "over" in base_label:
                key = f"over {line}"
            elif "under" in base_label:
                key = f"under {line}"
            if key is None:
                p = base_prob_from_odds(odds)
            else:
                p = probs_ou.get(key, base_prob_from_odds(odds))
            out[label] = {"prob": p, "ev": ev(p, odds)}
        return out

    # GG / NG
    if "gg" in m_lower or "both teams to score" in m_lower:
        probs_gg_ = prob_gg(lam_home, lam_away)
        for label, odds in selections.items():
            base_label = label.strip().upper()
            if base_label in ["GG", "BTTS YES", "YES"]:
                key = "GG"
            elif base_label in ["NG", "BTTS NO", "NO"]:
                key = "NG"
            else:
                key = None
            if key:
                p = probs_gg_.get(key, base_prob_from_odds(odds))
            else:
                p = base_prob_from_odds(odds)
            out[label] = {"prob": p, "ev": ev(p, odds)}
        return out

    # Fallback
    for label, odds in selections.items():
        p = base_prob_from_odds(odds)
        out[label] = {"prob": p, "ev": ev(p, odds)}

    return out
