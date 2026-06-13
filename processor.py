# =============================================================
# processor.py — all calculations, zero display logic
# Takes raw team/player data, returns clean derived stats
# Every function: data in → numbers out, nothing else
# =============================================================

import math
from config import MATCHES_TO_ANALYZE


# ── Utility helpers ───────────────────────────────────────────

def safe_divide(numerator, denominator, default=0.0):
    try:
        if not denominator:
            return default
        return round(numerator / denominator, 2)
    except (TypeError, ZeroDivisionError):
        return default


def safe_float(value, default=0.0):
    try:
        return float(value) if value is not None else default
    except (TypeError, ValueError):
        return default


def std_dev(values):
    values = [safe_float(v) for v in values if v is not None]
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return round(math.sqrt(variance), 2)


def consistency_label(sigma):
    if sigma < 0.8:
        return "Consistent"
    elif sigma < 1.5:
        return "Variable"
    else:
        return "Unpredictable"


# ── Match filtering ───────────────────────────────────────────

def filter_matches(matches, venue=None, n=None):
    """
    Filter matches by venue and count.
    n defaults to MATCHES_TO_ANALYZE from config.
    Pass n explicitly from app.py to respect the toggle.
    """
    n = n or MATCHES_TO_ANALYZE
    filtered = matches[:n]
    if venue:
        filtered = [m for m in filtered if m.get("venue") == venue]
    return filtered


def parse_goals_from_score(match):
    """
    Extract goals scored from score string e.g. '3-2' + 'W' → 3
    Falls back to 'goals' or 'gf' field if parsing fails.
    """
    result = match.get("result", match.get("r", ""))
    score  = match.get("score", "")
    try:
        home, away = score.split("-")
        home, away = int(home), int(away)
        if result == "W":
            return max(home, away)
        elif result == "L":
            return min(home, away)
        else:
            return home
    except (ValueError, AttributeError):
        return safe_float(match.get("goals", match.get("gf", 0)))


# ── Team calculations ─────────────────────────────────────────

def calc_match_averages(matches):
    """Calculate per-game averages across a list of matches."""
    if not matches:
        return {}

    count = len(matches)

    goals      = [safe_float(parse_goals_from_score(m)) for m in matches]
    conceded   = [safe_float(m.get("ga",         0))    for m in matches]
    xg         = [safe_float(m.get("xg",         0))    for m in matches]
    shots      = [safe_float(m.get("shots",      0))    for m in matches]
    sot        = [safe_float(m.get("sot",        0))    for m in matches]
    poss_raw   = [m.get("poss", "0%")                   for m in matches]
    possession = [safe_float(p.replace("%", ""))         for p in poss_raw]
    corners    = [safe_float(m.get("corners",    0))    for m in matches]
    passes     = [safe_float(m.get("passes",     0))    for m in matches]
    bc         = [safe_float(m.get("bigChances", m.get("bc", 0))) for m in matches]

    return {
        "goals":            round(sum(goals)      / count, 2),
        "goalsAgainst":     round(sum(conceded)   / count, 2),
        "xg":               round(sum(xg)         / count, 2),
        "shots":            round(sum(shots)       / count, 2),
        "sot":              round(sum(sot)         / count, 2),
        "possession":       round(sum(possession)  / count, 1),
        "corners":          round(sum(corners)     / count, 2),
        "passes":           round(sum(passes)      / count, 0),
        "bigChances":       round(sum(bc)          / count, 2),
        "shotConversion":   safe_divide(sum(goals), sum(shots)) * 100,
        "sotConversion":    safe_divide(sum(goals), sum(sot))   * 100,
        "goalsStdDev":      std_dev(goals),
        "goalsConsistency": consistency_label(std_dev(goals)),
        "xgStdDev":         std_dev(xg),
        "xgConsistency":    consistency_label(std_dev(xg)),
        "matchCount":       count,
    }


def get_team_summary(team_data, n=None):
    """
    Main entry point for team stats.
    Pass n from app.py to respect the match count toggle.

    Returns all, home, and away averages plus form.
    """
    matches = team_data.get("matches", [])

    all_matches  = filter_matches(matches, n=n)
    home_matches = filter_matches(matches, venue="H", n=n)
    away_matches = filter_matches(matches, venue="A", n=n)

    return {
        "all":  calc_match_averages(all_matches),
        "home": calc_match_averages(home_matches),
        "away": calc_match_averages(away_matches),
        "form": get_form(matches, n=n),
    }


# ── Form calculations ─────────────────────────────────────────

def get_form(matches, n=None):
    """
    Calculate form metrics from recent matches.
    W=3pts, D=1pt, L=0pts
    """
    n = n or MATCHES_TO_ANALYZE
    recent = matches[:n]

    if not recent:
        return {
            "strip": [], "points": 0,
            "pointsPerGame": 0, "trend": "Unknown",
            "trendDetail": "No matches"
        }

    points_map = {"W": 3, "D": 1, "L": 0}
    points = [points_map.get(m.get("result", m.get("r", "L")), 0) for m in recent]
    strip  = [m.get("result", m.get("r", "?")) for m in recent]

    total_points    = sum(points)
    points_per_game = safe_divide(total_points, len(points))

    mid = len(points) // 2
    if mid > 0:
        first_half  = points[mid:]
        second_half = points[:mid]
        first_avg   = safe_divide(sum(first_half),  len(first_half))
        second_avg  = safe_divide(sum(second_half), len(second_half))
        diff = second_avg - first_avg

        if diff > 0.5:
            trend = "Improving"
        elif diff < -0.5:
            trend = "Declining"
        else:
            trend = "Stable"

        trend_detail = (
            f"Avg {second_avg} pts last {mid} "
            f"vs {first_avg} pts prior {len(first_half)}"
        )
    else:
        trend        = "Stable"
        trend_detail = "Insufficient matches for trend"

    return {
        "strip":         strip,
        "points":        total_points,
        "pointsPerGame": points_per_game,
        "trend":         trend,
        "trendDetail":   trend_detail,
    }


# ── Player calculations ───────────────────────────────────────

def get_player_stats(player_data):
    """
    Calculate per-90 stats for a single player.
    Adds _per90 field for every numeric stat.
    """
    mins = safe_float(player_data.get("mins", player_data.get("minutes", 0)))

    numeric_fields = [
        "goals", "assists", "shots", "sot", "xg",
        "keyPasses", "passes", "chancesCreated", "xA",
        "tackles", "interceptions", "blocks",
        "clearances", "aerialWon", "duels", "dribbles",
        "bigChances",
    ]

    result = dict(player_data)

    for field in numeric_fields:
        raw = safe_float(player_data.get(field, 0))
        result[f"{field}_per90"] = safe_divide(raw * 90, mins)

    pa_raw = player_data.get("passAcc", player_data.get("pa", "0%"))
    if isinstance(pa_raw, str):
        result["passAcc"] = safe_float(pa_raw.replace("%", ""))
    else:
        result["passAcc"] = safe_float(pa_raw)

    result["shotConversion"] = safe_divide(
        safe_float(player_data.get("goals", 0)),
        safe_float(player_data.get("shots", 1))
    ) * 100

    return result


def get_all_player_stats(team_data, sort_by="goals"):
    """
    Process all players for a team.
    sort_by: any stat field — defaults to goals descending.
    """
    players = team_data.get("players", [])
    processed = [get_player_stats(p) for p in players]

    processed.sort(
        key=lambda p: -safe_float(p.get(sort_by, p.get(f"{sort_by}_per90", 0)))
    )

    return processed


# ── H2H and comparison ────────────────────────────────────────

def get_comparison(team_data_a, team_data_b, n=None):
    """Side-by-side stat comparison with edge indicators."""
    summary_a = get_team_summary(team_data_a, n=n)
    summary_b = get_team_summary(team_data_b, n=n)

    avg_a = summary_a["all"]
    avg_b = summary_b["all"]

    higher_is_better = [
        "goals", "xg", "shots", "sot", "bigChances",
        "possession", "passes", "corners",
    ]
    lower_is_better = ["goalsAgainst", "fouls"]

    edges = {}
    for stat in higher_is_better:
        val_a = safe_float(avg_a.get(stat, 0))
        val_b = safe_float(avg_b.get(stat, 0))
        if val_a > val_b + 0.1:
            edges[stat] = "A"
        elif val_b > val_a + 0.1:
            edges[stat] = "B"
        else:
            edges[stat] = "even"

    for stat in lower_is_better:
        val_a = safe_float(avg_a.get(stat, 0))
        val_b = safe_float(avg_b.get(stat, 0))
        if val_a < val_b - 0.1:
            edges[stat] = "A"
        elif val_b < val_a - 0.1:
            edges[stat] = "B"
        else:
            edges[stat] = "even"

    return {
        "team_a": summary_a,
        "team_b": summary_b,
        "edges":  edges,
    }


# ── Probability model inputs ──────────────────────────────────

def get_probability_inputs(team_data_a, team_data_b, team_a_is_home=True, n=None):
    """
    Prepare inputs for probability model.
    Includes home advantage, FIFA ranking, injury penalty.
    """
    from config import (
        WEIGHT_FORM_PPG, WEIGHT_XG_FOR, WEIGHT_GOALS_FOR, WEIGHT_DEFENSE,
        HOME_ADVANTAGE_WEIGHT, FIFA_RANKING_WEIGHT, FIFA_RANKING_MAX,
        INJURY_PENALTY_ATTACK, INJURY_PENALTY_MID, INJURY_PENALTY_DEF,
        INJURY_PENALTY_MAX,
    )

    summary_a = get_team_summary(team_data_a, n=n)
    summary_b = get_team_summary(team_data_b, n=n)

    def calc_injury_penalty(team_data):
        penalty = 0.0
        for player in team_data.get("players", []):
            if player.get("injured", False):
                pos = player.get("pos", "MID")
                if pos == "FWD":
                    penalty += INJURY_PENALTY_ATTACK
                elif pos == "MID":
                    penalty += INJURY_PENALTY_MID
                elif pos == "DEF":
                    penalty += INJURY_PENALTY_DEF
        return min(penalty, INJURY_PENALTY_MAX)

    def calc_ranking_boost(fifa_rank):
        rank  = safe_float(fifa_rank, default=100)
        boost = max(0.0, (FIFA_RANKING_MAX - rank) / FIFA_RANKING_MAX)
        return round(boost, 3)

    def extract_inputs(summary, team_data, is_home):
        avg = summary["all"]
        base_strength = (
            safe_float(summary["form"].get("pointsPerGame", 0)) * WEIGHT_FORM_PPG +
            safe_float(avg.get("xg",           0))              * WEIGHT_XG_FOR   +
            safe_float(avg.get("goals",         0))              * WEIGHT_GOALS_FOR +
            max(0, 3 - safe_float(avg.get("goalsAgainst", 0)))  * WEIGHT_DEFENSE
        )
        home_boost     = HOME_ADVANTAGE_WEIGHT if is_home else 0.0
        rank_boost     = calc_ranking_boost(team_data.get("fifa", 100)) * FIFA_RANKING_WEIGHT
        injury_pen     = calc_injury_penalty(team_data)
        total_strength = max(0.01, base_strength + home_boost + rank_boost - injury_pen)

        return {
            "avg_scored":   safe_float(avg.get("goals",        0)),
            "avg_conceded": safe_float(avg.get("goalsAgainst", 0)),
            "form_ppg":     safe_float(summary["form"].get("pointsPerGame", 0)),
            "xg_for":       safe_float(avg.get("xg",           0)),
            "xg_against":   safe_float(avg.get("xgAgainst",    0)),
            "consistency":  safe_float(avg.get("goalsStdDev",  0)),
            "home_boost":   round(home_boost, 3),
            "rank_boost":   round(rank_boost, 3),
            "injury_pen":   round(injury_pen, 3),
            "strength":     round(total_strength, 3),
        }

    h2h_a = team_data_a.get("h2h", {})
    h2h_b = team_data_b.get("h2h", {})
    h2h_available = bool(h2h_a.get("rows") or h2h_b.get("rows"))

    return {
        "team_a":        extract_inputs(summary_a, team_data_a, is_home=team_a_is_home),
        "team_b":        extract_inputs(summary_b, team_data_b, is_home=not team_a_is_home),
        "h2h_available": h2h_available,
    }


# ── Quick test ────────────────────────────────────────────────

if __name__ == "__main__":
    import json
    from pathlib import Path

    print("Loading test data...")
    raw   = json.load(open(Path("data/wc2026_data.json")))
    teams = {t["name"]: t for t in raw.get("teams", [])}

    print("\n── USA team summary ──")
    usa = get_team_summary(teams["USA"])
    print(f"  All  — Goals/game: {usa['all']['goals']}, xG: {usa['all']['xg']}")
    print(f"  Home — Goals/game: {usa['home'].get('goals', 'N/A')}")
    print(f"  Away — Goals/game: {usa['away'].get('goals', 'N/A')}")
    print(f"  Form — {usa['form']['strip']} | {usa['form']['points']}pts | {usa['form']['trend']}")

    print("\n── USA players sorted by goals ──")
    players = get_all_player_stats(teams["USA"], sort_by="goals")
    for p in players[:3]:
        print(f"  {p.get('name','?'):20} | Goals: {p.get('goals',0)} | Goals/90: {p.get('goals_per90',0)}")

    print("\n── USA vs Paraguay comparison ──")
    comp = get_comparison(teams["USA"], teams["Paraguay"])
    for stat, edge in list(comp["edges"].items())[:5]:
        print(f"  {stat:20} → {edge}")

    print("\n── Probability inputs (USA at home) ──")
    prob = get_probability_inputs(teams["USA"], teams["Paraguay"], team_a_is_home=True)
    print(f"  USA strength:      {prob['team_a']['strength']}")
    print(f"  Paraguay strength: {prob['team_b']['strength']}")

    print("\n✓ processor.py working correctly")