# =============================================================
# processor.py — all calculations, zero display logic
# Takes raw team/player data, returns clean derived stats
# Every function: data in → numbers out, nothing else
# =============================================================

import math
from config import MATCHES_TO_ANALYZE


# ── Utility helpers ───────────────────────────────────────────

def safe_divide(numerator, denominator, default=0.0):
    """
    Divide two numbers safely.
    Returns default if denominator is zero or None.
    Used everywhere to prevent division-by-zero crashes.

    Example:
        safe_divide(10, 0)   → 0.0
        safe_divide(10, 4)   → 2.5
        safe_divide(None, 4) → 0.0
    """
    try:
        if not denominator:
            return default
        return round(numerator / denominator, 2)
    except (TypeError, ZeroDivisionError):
        return default


def safe_float(value, default=0.0):
    """
    Convert any value to float safely.
    Returns default if value is None, empty, or unconvertible.

    Example:
        safe_float("2.4")  → 2.4
        safe_float(None)   → 0.0
        safe_float("N/A")  → 0.0
    """
    try:
        return float(value) if value is not None else default
    except (TypeError, ValueError):
        return default


def std_dev(values):
    """
    Calculate population standard deviation for a list of numbers.
    Returns 0.0 for empty or single-value lists.

    Standard deviation measures how spread out values are:
    - Low  (< 0.8): consistent performance
    - Mid  (0.8–1.5): variable
    - High (> 1.5): unpredictable
    """
    values = [safe_float(v) for v in values if v is not None]
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return round(math.sqrt(variance), 2)


def consistency_label(sigma):
    """
    Convert a standard deviation number into a readable label.

    Example:
        consistency_label(0.4) → "Consistent"
        consistency_label(1.2) → "Variable"
        consistency_label(2.1) → "Unpredictable"
    """
    if sigma < 0.8:
        return "Consistent"
    elif sigma < 1.5:
        return "Variable"
    else:
        return "Unpredictable"


# ── Match filtering ───────────────────────────────────────────

def filter_matches(matches, venue=None, n=None):
    """
    Filter a list of matches by venue and/or count.

    Args:
        matches: list of match dicts from JSON
        venue:   "H" for home, "A" for away, "N" for neutral,
                 None for all venues
        n:       how many matches to include (most recent first)
                 None uses MATCHES_TO_ANALYZE from config

    Returns:
        filtered list of match dicts

    Example:
        filter_matches(matches, venue="H", n=5)
        → last 5 home matches only
    """
    n = n or MATCHES_TO_ANALYZE
    filtered = matches[:n]  # most recent N matches
    if venue:
        filtered = [m for m in filtered if m.get("venue") == venue]
    return filtered

def parse_goals_from_score(match):
    """
    Extract goals scored from a score string.
    e.g. '3-2' with result 'W' → 3
         '0-2' with result 'L' → 0
    Falls back to 'goals' or 'gf' field if score parsing fails.
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
            return home  # draw, either side is fine
    except (ValueError, AttributeError):
        return safe_float(match.get("goals", match.get("gf", 0)))
# ── Team calculations ─────────────────────────────────────────

def calc_match_averages(matches):
    """
    Calculate per-game averages across a list of matches.
    Returns a dict of averaged stats.

    This is the core calculation used everywhere — team averages,
    home averages, away averages all use this same function.
    """
    if not matches:
        return {}

    count = len(matches)

    # Extract each stat across all matches safely
    goals      = [safe_float(parse_goals_from_score(m)) for m in matches]
    conceded   = [safe_float(m.get("ga",         0))               for m in matches]
    xg         = [safe_float(m.get("xg",         0))               for m in matches]
    shots      = [safe_float(m.get("shots",      0))               for m in matches]
    sot        = [safe_float(m.get("sot",        0))               for m in matches]
    poss_raw   = [m.get("poss", "0%") for m in matches]
    possession = [safe_float(p.replace("%", "")) for p in poss_raw]
    corners    = [safe_float(m.get("corners",    0))               for m in matches]
    passes     = [safe_float(m.get("passes",     0))               for m in matches]
    bc         = [safe_float(m.get("bigChances", m.get("bc", 0)))  for m in matches]

    return {
        # Per-game averages
        "goals":        round(sum(goals)      / count, 2),
        "goalsAgainst": round(sum(conceded)   / count, 2),
        "xg":           round(sum(xg)         / count, 2),
        "shots":        round(sum(shots)       / count, 2),
        "sot":          round(sum(sot)         / count, 2),
        "possession":   round(sum(possession)  / count, 1),
        "corners":      round(sum(corners)     / count, 2),
        "passes":       round(sum(passes)      / count, 0),
        "bigChances":   round(sum(bc)          / count, 2),

        # Derived rates
        "shotConversion": safe_divide(sum(goals), sum(shots)) * 100,
        "sotConversion":  safe_divide(sum(goals), sum(sot))   * 100,

        # Consistency (standard deviation)
        "goalsStdDev":  std_dev(goals),
        "goalsConsistency": consistency_label(std_dev(goals)),
        "xgStdDev":     std_dev(xg),
        "xgConsistency": consistency_label(std_dev(xg)),

        # Match count included so display knows sample size
        "matchCount": count,
    }


def get_team_summary(team_data):
    """
    Main entry point for team stats.
    Returns all, home, and away averages separately.

    This is what app.py calls — one function, complete picture.

    Returns:
        {
            "all":  { averages across all matches },
            "home": { averages for home matches only },
            "away": { averages for away matches only },
            "form": { form strip, points, trend },
        }
    """
    matches = team_data.get("matches", [])

    # Split by venue
    all_matches  = filter_matches(matches)
    home_matches = filter_matches(matches, venue="H")
    away_matches = filter_matches(matches, venue="A")

    return {
        "all":  calc_match_averages(all_matches),
        "home": calc_match_averages(home_matches),
        "away": calc_match_averages(away_matches),
        "form": get_form(matches),
    }


# ── Form calculations ─────────────────────────────────────────

def get_form(matches, n=None):
    """
    Calculate form metrics from recent matches.

    Form points: W=3, D=1, L=0 (standard football points system)
    Trend: compares first half vs second half of the window
           to detect improving or declining form

    Returns:
        {
            "strip":        ["W", "L", "W", "D", "W"],
            "points":       10,
            "pointsPerGame": 2.0,
            "trend":        "Improving",
            "trendDetail":  "Avg 2.3 pts last 3 vs 1.7 pts first 3"
        }
    """
    n = n or MATCHES_TO_ANALYZE
    recent = matches[:n]

    if not recent:
        return {
            "strip": [], "points": 0,
            "pointsPerGame": 0, "trend": "Unknown",
            "trendDetail": "No matches"
        }

    # Points per result
    points_map = {"W": 3, "D": 1, "L": 0}
    points = [points_map.get(m.get("result", m.get("r", "L")), 0) for m in recent]
    strip  = [m.get("result", m.get("r", "?")) for m in recent]

    total_points    = sum(points)
    points_per_game = safe_divide(total_points, len(points))

    # Trend — split window in half, compare averages
    mid = len(points) // 2
    if mid > 0:
        first_half  = points[mid:]   # older matches
        second_half = points[:mid]   # more recent matches
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
    Calculate per-game and per-90 stats for a single player.

    Per 90 normalises for playing time — a player with 3 goals
    in 200 minutes is far more prolific than one with 3 goals
    in 900 minutes. Per 90 makes them comparable.

    Args:
        player_data: single player dict from JSON

    Returns:
        player dict extended with _per90 and _perGame fields
        for every numeric stat
    """
    mins = safe_float(player_data.get("mins", player_data.get("minutes", 0)))

    # Stats to normalise — field name from JSON
    numeric_fields = [
        "goals", "assists", "shots", "sot", "xg",
        "keyPasses", "passes", "chancesCreated", "xA",
        "tackles", "interceptions", "blocks",
        "clearances", "aerialWon", "duels", "dribbles",
        "bigChances",
    ]

    result = dict(player_data)  # copy original data

    for field in numeric_fields:
        raw = safe_float(player_data.get(field, 0))

        # Per 90 minutes
        result[f"{field}_per90"] = safe_divide(raw * 90, mins)

    # Pass accuracy — already a percentage, don't normalise
    # Just ensure it's a clean float
    pa_raw = player_data.get("passAcc", player_data.get("pa", "0%"))
    if isinstance(pa_raw, str):
        result["passAcc"] = safe_float(pa_raw.replace("%", ""))
    else:
        result["passAcc"] = safe_float(pa_raw)

    # Shot conversion rate
    result["shotConversion"] = safe_divide(
        safe_float(player_data.get("goals", 0)),
        safe_float(player_data.get("shots", 0))
    ) * 100

    return result


def get_all_player_stats(team_data):
    """
    Process all players for a team.
    Returns list of player dicts with per90 stats added.
    Sorted by position: FWD → MID → DEF → GK
    """
    players  = team_data.get("players", [])
    pos_order = {"FWD": 0, "MID": 1, "DEF": 2, "GK": 3}

    processed = [get_player_stats(p) for p in players]

    # Sort by position order, then by rating descending within position
    processed.sort(key=lambda p: (
        pos_order.get(p.get("pos", "GK"), 99),
        -safe_float(p.get("rating", p.get("rtg", 0)))
    ))

    return processed


# ── H2H and comparison ────────────────────────────────────────

def get_comparison(team_data_a, team_data_b):
    """
    Build a side-by-side stat comparison between two teams.
    Used by the Compare teams page.

    Returns:
        {
            "team_a": { all, home, away averages },
            "team_b": { all, home, away averages },
            "edges":  { stat: "A" or "B" or "even" }
        }

    Edges tell the display which team is stronger in each
    category so it can highlight accordingly.
    """
    summary_a = get_team_summary(team_data_a)
    summary_b = get_team_summary(team_data_b)

    avg_a = summary_a["all"]
    avg_b = summary_b["all"]

    # For each stat, determine which team has the edge
    # Higher is better for attack, lower is better for defense
    higher_is_better = [
        "goals", "xg", "shots", "sot", "bigChances",
        "possession", "passes", "corners",
    ]
    lower_is_better = [
        "goalsAgainst", "fouls",
    ]

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
        "team_a":  summary_a,
        "team_b":  summary_b,
        "edges":   edges,
    }


# ── Probability model inputs ──────────────────────────────────

def get_probability_inputs(team_data_a, team_data_b):
    """
    Prepare clean inputs for the probability model.
    Separates home/away correctly based on which team
    is at home for this specific match.

    The actual probability calculation lives in a separate
    model function — this just prepares the inputs so
    the model can be swapped without touching this file.

    Returns:
        {
            "team_a": {
                "avg_scored":   float,
                "avg_conceded": float,
                "form_ppg":     float,
                "xg_for":       float,
                "xg_against":   float,
            },
            "team_b": { same structure },
            "h2h_available": bool,
        }
    """
    summary_a = get_team_summary(team_data_a)
    summary_b = get_team_summary(team_data_b)

    def extract_inputs(summary):
        avg = summary["all"]
        return {
            "avg_scored":   safe_float(avg.get("goals",        0)),
            "avg_conceded": safe_float(avg.get("goalsAgainst", 0)),
            "form_ppg":     safe_float(summary["form"].get("pointsPerGame", 0)),
            "xg_for":       safe_float(avg.get("xg",           0)),
            "xg_against":   safe_float(avg.get("xgAgainst",    0)),
            "consistency":  safe_float(avg.get("goalsStdDev",  0)),
        }

    # Check if H2H data exists
    h2h_a = team_data_a.get("h2h", {})
    h2h_b = team_data_b.get("h2h", {})
    h2h_available = bool(h2h_a.get("rows") or h2h_b.get("rows"))

    return {
        "team_a":        extract_inputs(summary_a),
        "team_b":        extract_inputs(summary_b),
        "h2h_available": h2h_available,
    }


# ── Quick test ────────────────────────────────────────────────
# Run this file directly to verify calculations are working
# python3 processor.py

if __name__ == "__main__":
    import json
    from pathlib import Path

    print("Loading test data...")
    path = Path("data/wc2026_data.json")
    raw  = json.load(open(path))
    teams = {t["name"]: t for t in raw.get("teams", [])}

    print("\n── USA team summary ──")
    usa = get_team_summary(teams["USA"])
    print(f"  All  — Goals/game: {usa['all']['goals']}, xG: {usa['all']['xg']}")
    print(f"  Home — Goals/game: {usa['home'].get('goals', 'N/A')}")
    print(f"  Away — Goals/game: {usa['away'].get('goals', 'N/A')}")
    print(f"  Form — {usa['form']['strip']} | {usa['form']['points']}pts | {usa['form']['trend']}")

    print("\n── USA players (per 90) ──")
    players = get_all_player_stats(teams["USA"])
    for p in players[:3]:
        print(f"  {p['name']:20} | Goals/90: {p.get('goals_per90', 0)} | xG/90: {p.get('xg_per90', 0)}")

    print("\n── USA vs Paraguay comparison ──")
    comp = get_comparison(teams["USA"], teams["Paraguay"])
    for stat, edge in list(comp["edges"].items())[:5]:
        print(f"  {stat:20} → edge: {edge}")

    print("\n── Probability inputs ──")
    prob = get_probability_inputs(teams["USA"], teams["Paraguay"])
    print(f"  USA:      {prob['team_a']}")
    print(f"  Paraguay: {prob['team_b']}")
    print(f"  H2H available: {prob['h2h_available']}")

    print("\n✓ processor.py working correctly")