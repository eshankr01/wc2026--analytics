# =============================================================
# config.py — single source of truth for all app settings
# Change behaviour here, nowhere else
# =============================================================


# ── Tournament structure ──────────────────────────────────────

TOURNAMENT_NAME = "FIFA World Cup 2026"

# How many recent matches to analyze per team and player
# Change this one number to switch between 5, 10, or any N
MATCHES_TO_ANALYZE = 10

GROUPS = {
    "A": ["Qatar", "Canada", "Ecuador", "Netherlands"],
    "B": ["USA", "Paraguay", "Australia", "Turkey"],
    "C": ["Spain", "Croatia", "Morocco", "Japan"],
    "D": ["Argentina", "Chile", "Peru", "Canada"],
    "E": ["France", "Senegal", "Belgium", "Austria"],
    "F": ["Brazil", "Serbia", "Switzerland", "Cameroon"],
    "G": ["England", "Iran", "New Zealand", "Burkina Faso"],
    "H": ["Portugal", "Uruguay", "South Korea", "Ghana"],
}

FLAGS = {
    "USA": "🇺🇸", "Paraguay": "🇵🇾", "Australia": "🇦🇺", "Turkey": "🇹🇷",
    "Qatar": "🇶🇦", "Canada": "🇨🇦", "Ecuador": "🇪🇨", "Netherlands": "🇳🇱",
    "Spain": "🇪🇸", "Croatia": "🇭🇷", "Morocco": "🇲🇦", "Japan": "🇯🇵",
    "Argentina": "🇦🇷", "Chile": "🇨🇱", "Peru": "🇵🇪",
    "France": "🇫🇷", "Senegal": "🇸🇳", "Belgium": "🇧🇪", "Austria": "🇦🇹",
    "Brazil": "🇧🇷", "Serbia": "🇷🇸", "Switzerland": "🇨🇭", "Cameroon": "🇨🇲",
    "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Iran": "🇮🇷", "New Zealand": "🇳🇿", "Burkina Faso": "🇧🇫",
    "Portugal": "🇵🇹", "Uruguay": "🇺🇾", "South Korea": "🇰🇷", "Ghana": "🇬🇭",
}


# ── Player stat definitions ───────────────────────────────────
# Four categories, each with field name + display label + description
# This drives every player card and comparison table automatically

PLAYER_STAT_CATEGORIES = {

    "Attacking": [
        {"field": "goals",      "label": "Goals",       "desc": "Total goals scored"},
        {"field": "assists",    "label": "Assists",      "desc": "Final pass leading to a goal"},
        {"field": "shots",      "label": "Shots",        "desc": "Total attempts at goal"},
        {"field": "sot",        "label": "SOT",          "desc": "Shots on target"},
        {"field": "xg",         "label": "xG",           "desc": "Expected goals — shot quality metric"},
        {"field": "bigChances", "label": "Big chances",  "desc": "High-probability scoring opportunities"},
    ],

    "Passing": [
        {"field": "passes",         "label": "Passes",       "desc": "Total passes attempted"},
        {"field": "passesCompleted","label": "Pass comp.",    "desc": "Passes successfully received by teammate"},
        {"field": "passAcc",        "label": "Pass %",        "desc": "Passing accuracy percentage"},
        {"field": "keyPasses",      "label": "Key passes",    "desc": "Passes directly leading to a shot"},
        {"field": "chancesCreated", "label": "Chances cr.",   "desc": "Total opportunities created for teammates"},
        {"field": "xA",             "label": "xA",            "desc": "Expected assists — pass quality metric"},
    ],

    "Defending": [
        {"field": "tackles",      "label": "Tackles",       "desc": "Successful challenges to win the ball"},
        {"field": "interceptions","label": "Interceptions", "desc": "Passes cut out before reaching opponent"},
        {"field": "blocks",       "label": "Blocks",        "desc": "Shots or passes physically blocked"},
        {"field": "clearances",   "label": "Clearances",    "desc": "Ball cleared from danger area"},
        {"field": "aerialWon",    "label": "Aerial won",    "desc": "Headers won in contested situations"},
        {"field": "xgConceded",   "label": "xG conceded",   "desc": "Expected goals allowed while on pitch"},
    ],

    "Duels": [
        {"field": "duelsWon",     "label": "Duels won",     "desc": "Total ground and aerial duels won"},
        {"field": "duelsTotal",   "label": "Duels total",   "desc": "Total duels contested"},
        {"field": "aerialWon",    "label": "Aerial won",    "desc": "Aerial duels won"},
        {"field": "dribbles",     "label": "Dribbles",      "desc": "Successful dribbles past an opponent"},
        {"field": "foulsWon",     "label": "Fouls won",     "desc": "Times fouled by opponent"},
        {"field": "foulsCommitted","label": "Fouls",        "desc": "Fouls committed"},
    ],
}

# Stats shown in the compact player card grid (subset of above)
PLAYER_CARD_QUICK_STATS = [
    "goals", "assists", "shots", "xg",
    "keyPasses", "passAcc", "tackles", "interceptions",
    "aerialWon", "rating",
]


# ── Team stat definitions ─────────────────────────────────────

TEAM_STAT_CATEGORIES = {

    "Attack": [
        {"field": "goals",      "label": "Goals / game"},
        {"field": "xg",         "label": "xG / game"},
        {"field": "shots",      "label": "Shots / game"},
        {"field": "sot",        "label": "SOT / game"},
        {"field": "bigChances", "label": "Big chances / game"},
        {"field": "shotConv",   "label": "Shot conversion %"},
    ],

    "Passing": [
        {"field": "possession", "label": "Avg possession %"},
        {"field": "passAcc",    "label": "Pass accuracy %"},
        {"field": "passes",     "label": "Passes / game"},
        {"field": "keyPasses",  "label": "Key passes / game"},
        {"field": "corners",    "label": "Corners / game"},
    ],

    "Defense": [
        {"field": "goalsAgainst",    "label": "Goals conceded / game"},
        {"field": "xgAgainst",       "label": "xGA / game"},
        {"field": "saves",           "label": "Saves / game"},
        {"field": "cleanSheets",     "label": "Clean sheets"},
        {"field": "tackles",         "label": "Tackles / game"},
        {"field": "interceptions",   "label": "Interceptions / game"},
    ],

    "Duels": [
        {"field": "duelsWon",  "label": "Duels won / game"},
        {"field": "aerialWon", "label": "Aerial win %"},
        {"field": "fouls",     "label": "Fouls / game"},
    ],
}


# ── H2H comparison settings ───────────────────────────────────

# Categories shown in the side-by-side team comparison
# Order matters — this is the order they appear in the table
H2H_COMPARISON_STATS = [
    {"field": "goals",        "label": "Goals / game",         "category": "Attack"},
    {"field": "xg",           "label": "xG / game",            "category": "Attack"},
    {"field": "shots",        "label": "Shots / game",         "category": "Attack"},
    {"field": "sot",          "label": "SOT / game",           "category": "Attack"},
    {"field": "bigChances",   "label": "Big chances / game",   "category": "Attack"},
    {"field": "possession",   "label": "Possession %",         "category": "Passing"},
    {"field": "passAcc",      "label": "Pass accuracy %",      "category": "Passing"},
    {"field": "keyPasses",    "label": "Key passes / game",    "category": "Passing"},
    {"field": "goalsAgainst", "label": "Goals conceded / game","category": "Defense"},
    {"field": "xgAgainst",    "label": "xGA / game",           "category": "Defense"},
    {"field": "cleanSheets",  "label": "Clean sheets",         "category": "Defense"},
    {"field": "tackles",      "label": "Tackles / game",       "category": "Defense"},
    {"field": "interceptions","label": "Interceptions / game", "category": "Defense"},
    {"field": "duelsWon",     "label": "Duels won / game",     "category": "Duels"},
    {"field": "aerialWon",    "label": "Aerial win %",         "category": "Duels"},
    {"field": "fouls",        "label": "Fouls / game",         "category": "Duels"},
]

# Whether to show H2H match history when available
SHOW_H2H_HISTORY = True

# Minimum H2H matches needed to show the history section
H2H_MIN_MATCHES = 1


# ── Data sources ──────────────────────────────────────────────

DATA_FILE = "data/wc2026_data.json"

ESPN_BASE_URL    = "https://site.api.espn.com/apis/site/v2/sports/soccer"
ESPN_SCOREBOARD  = f"{ESPN_BASE_URL}/fifa.world/scoreboard"
ESPN_TEAM_URL    = f"{ESPN_BASE_URL}/fifa.world/teams"

# Cache durations — how long before re-fetching from source
CACHE_SECONDS_LIVE     = 60      # live match: every minute
CACHE_SECONDS_PREMATCH = 3600    # pre-match: every hour
CACHE_SECONDS_STATIC   = 86400   # historical: once per day


# ── Live score settings ───────────────────────────────────────

LIVE_REFRESH_INTERVAL = 60   # seconds between auto-refresh during matches


# ── Probability & odds model settings ────────────────────────

# Which inputs feed the probability model
PROB_MODEL_INPUTS = [
    "form",
    "xg_for",
    "xg_against",
    "goals_for",
    "goals_against",
    "h2h_record",
    "home_advantage",
    "fifa_ranking",
    "injuries",
]

# Result labels
RESULT_LABELS = ["Home win", "Draw", "Away win"]

# Minimum matches needed before model runs
PROB_MIN_MATCHES = 3

# Odds format
ODDS_FORMAT = "decimal"

# Value threshold
VALUE_THRESHOLD = 0.05

# ── Model weights ─────────────────────────────────────────────
# These three control how much each factor influences strength score
# Must sum to 1.0 across form/xg/goals weights
# Adjust here to tune the model — never hardcode in processor.py

WEIGHT_FORM_PPG   = 0.30   # recent form points per game
WEIGHT_XG_FOR     = 0.35   # xG quality of chances created
WEIGHT_GOALS_FOR  = 0.20   # raw goals scored
WEIGHT_DEFENSE    = 0.15   # goals conceded (inverted)

# ── Home advantage ────────────────────────────────────────────
# Added directly to home team's strength score
# 0.15 means home team gets ~15% boost — calibrated to football data
# Set to 0.0 to disable entirely
HOME_ADVANTAGE_WEIGHT = 0.15

# ── FIFA ranking adjustment ───────────────────────────────────
# Scales how much FIFA rank influences the probability
# Higher = ranking matters more, lower = form matters more
# 0.0 disables ranking adjustment entirely
FIFA_RANKING_WEIGHT = 0.10

# Best possible FIFA ranking (used for normalisation)
# Rank 1 gets full boost, rank 200 gets zero boost
FIFA_RANKING_MAX = 200

# ── Injury model ──────────────────────────────────────────────
# How much each injured key player reduces attack strength
# A team with 2 injured forwards loses 2 * INJURY_PENALTY_ATTACK
INJURY_PENALTY_ATTACK  = 0.08   # per injured FWD
INJURY_PENALTY_MID     = 0.05   # per injured MID
INJURY_PENALTY_DEF     = 0.03   # per injured DEF

# Maximum total injury penalty (cap so it doesn't over-penalise)
INJURY_PENALTY_MAX = 0.20

# ── Draw probability ──────────────────────────────────────────
# Maximum draw probability when teams are perfectly matched
# Football average is ~26-28% draws in tournament play
DRAW_PROB_MAX = 0.28

# ── Display settings ──────────────────────────────────────────

DEFAULT_PLAYERS_SHOWN = 8

RESULT_COLOURS = {
    "W": {"bg": "#EAF3DE", "text": "#27500A"},
    "L": {"bg": "#FCEBEB", "text": "#791F1F"},
    "D": {"bg": "#F1EFE8", "text": "#5F5E5A"},
}

# Colours used across charts and comparison bars
TEAM_COLOURS = {
    "primary":   "#185FA5",   # blue  — home team / left side
    "secondary": "#3B6D11",   # green — away team / right side
    "neutral":   "#888780",   # gray  — draws / neutral
    "positive":  "#3B6D11",   # green — good stat / value bet
    "negative":  "#A32D2D",   # red   — bad stat / no value
}
