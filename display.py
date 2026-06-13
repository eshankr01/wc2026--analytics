# =============================================================
# display.py — all Streamlit rendering, zero calculation logic
# Every function: takes processed data, renders components
# Import and call from app.py only
# =============================================================

import streamlit as st
from processor import (
    get_team_summary,
    get_all_player_stats,
    get_comparison,
    get_probability_inputs,
)
from config import (
    RESULT_COLOURS,
    TEAM_COLOURS,
    PLAYER_CARD_QUICK_STATS,
    H2H_COMPARISON_STATS,
    ODDS_FORMAT,
    VALUE_THRESHOLD,
    MATCHES_TO_ANALYZE,
)


# ── Helpers ───────────────────────────────────────────────────

def result_badge(result):
    """
    Render a coloured W/D/L badge inline.
    Uses colours defined in config.RESULT_COLOURS.
    """
    colours = RESULT_COLOURS.get(result, RESULT_COLOURS["D"])
    st.markdown(
        f'<span style="'
        f'background:{colours["bg"]};'
        f'color:{colours["text"]};'
        f'padding:2px 10px;'
        f'border-radius:4px;'
        f'font-size:12px;'
        f'font-weight:500">'
        f'{result}</span>',
        unsafe_allow_html=True,
    )


def form_strip(strip, match_labels=None):
    """
    Render a row of W/D/L dots with tooltips.
    Most recent match on the left.
    """
    colours = {"W": "#3B6D11", "L": "#A32D2D", "D": "#888780"}
    dots = []
    for i, r in enumerate(strip):
        colour = colours.get(r, "#888780")
        label  = match_labels[i] if match_labels and i < len(match_labels) else r
        dots.append(
            f'<span title="{label}" style="'
            f'width:22px;height:22px;border-radius:50%;'
            f'background:{colour};color:white;'
            f'display:inline-flex;align-items:center;'
            f'justify-content:center;font-size:10px;'
            f'font-weight:500;margin-right:4px;'
            f'cursor:default">{r}</span>'
        )
    st.markdown(
        '<div style="display:flex;align-items:center;gap:2px">'
        + "".join(dots) + "</div>",
        unsafe_allow_html=True,
    )


def section_header(title):
    """Consistent section label styling throughout the dashboard."""
    st.markdown(
        f'<div style="font-size:11px;font-weight:500;'
        f'color:var(--text-color);opacity:0.5;'
        f'text-transform:uppercase;letter-spacing:.05em;'
        f'margin:1rem 0 .4rem">{title}</div>',
        unsafe_allow_html=True,
    )


def edge_indicator(edge, team_a_name, team_b_name):
    """
    Show which team has the statistical edge.
    Green for team A, blue for team B, gray for even.
    """
    if edge == "A":
        return f"✓ {team_a_name}"
    elif edge == "B":
        return f"✓ {team_b_name}"
    else:
        return "Even"


# ── Team header ───────────────────────────────────────────────

def show_team_header(team_data, summary):
    """
    Renders the team identity block at the top of the dashboard:
    flag, name, FIFA rank, manager, formation, form strip + trend.
    """
    form = summary["form"]

    col_flag, col_info, col_form = st.columns([1, 4, 3])

    with col_flag:
        st.markdown(
            f'<div style="font-size:52px;line-height:1">'
            f'{team_data.get("flag", "🏳")}</div>',
            unsafe_allow_html=True,
        )

    with col_info:
        st.markdown(
            f'### {team_data.get("name", "")} '
            f'<span style="font-size:14px;font-weight:400;'
            f'opacity:0.6">FIFA #{team_data.get("fifa", "—")}</span>',
            unsafe_allow_html=True,
        )
        st.caption(
            f'{team_data.get("manager", "—")} · '
            f'{team_data.get("formation", "—")}'
        )

    with col_form:
        st.caption("Form — last 5")
        form_strip(
            form["strip"],
            match_labels=team_data.get("formMatches", []),
        )
        st.caption(
            f'{form["points"]}pts · '
            f'{form["pointsPerGame"]} PPG · '
            f'{form["trend"]}'
        )

    st.divider()


# ── Team averages ─────────────────────────────────────────────

def show_team_averages(summary):
    """
    Renders four rows of metric cards — Attack, Passing,
    Defense, Duels — with home/away toggle at the top.

    The toggle lets the user switch between overall,
    home-only, and away-only averages instantly.
    """
    # Venue toggle
    venue = st.radio(
        "View averages for",
        options=["All matches", "Home only", "Away only"],
        horizontal=True,
        label_visibility="collapsed",
    )

    # Pick the right averages based on selection
    venue_map = {
        "All matches": summary["all"],
        "Home only":   summary["home"],
        "Away only":   summary["away"],
    }
    avg = venue_map[venue]

    if not avg:
        st.info(f"No {venue.lower()} matches in the last {MATCHES_TO_ANALYZE} games.")
        return

    sample = avg.get("matchCount", "?")
    st.caption(f"Based on {sample} matches")

    # ── Attack ──
    section_header("Attack")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Goals / game",       avg.get("goals",      "—"))
    c2.metric("xG / game",          avg.get("xg",         "—"))
    c3.metric("Shots / game",       avg.get("shots",      "—"))
    c4.metric("Shots on tgt / game",avg.get("sot",        "—"))

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Big chances / game", avg.get("bigChances", "—"))
    c6.metric("Shot conversion %",  avg.get("shotConversion", "—"))
    c7.metric("SOT conversion %",   avg.get("sotConversion",  "—"))
    c8.metric("Goals consistency",  avg.get("goalsConsistency","—"))

    # ── Passing ──
    section_header("Passing & possession")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Possession %",  avg.get("possession", "—"))
    c2.metric("Passes / game", avg.get("passes",     "—"))
    c3.metric("Corners / game",avg.get("corners",    "—"))
    c4.metric("xG consistency",avg.get("xgConsistency", "—"))

    # ── Defense ──
    section_header("Defense")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Goals conceded / game", avg.get("goalsAgainst", "—"))
    c2.metric("xGA / game",            avg.get("xgAgainst",    "—"))
    c3.metric("Goals std dev",         avg.get("goalsStdDev",  "—"))
    c4.metric("xG std dev",            avg.get("xgStdDev",     "—"))


# ── Match cards ───────────────────────────────────────────────

def show_match_cards(team_data):
    """
    Renders a card for each of the last N matches.
    Shows: opponent, date, venue, score, result badge,
    and key stats in a compact row.
    """
    matches = team_data.get("matches", [])[:MATCHES_TO_ANALYZE]

    if not matches:
        st.info("No match data available.")
        return

    for m in matches:
        result  = m.get("result", m.get("r", "?"))
        score   = m.get("score",  "?-?")
        opp     = m.get("opp",    "Unknown")
        date    = m.get("date",   "")
        venue   = m.get("venue",  "")
        venue_label = {"H": "Home", "A": "Away", "N": "Neutral"}.get(venue, venue)

        colours = RESULT_COLOURS.get(result, RESULT_COLOURS["D"])

        with st.container():
            col_res, col_match, col_stats = st.columns([1, 3, 4])

            with col_res:
                st.markdown(
                    f'<div style="background:{colours["bg"]};'
                    f'color:{colours["text"]};'
                    f'border-radius:8px;padding:8px;'
                    f'text-align:center">'
                    f'<div style="font-size:20px;font-weight:500">{score}</div>'
                    f'<div style="font-size:11px;font-weight:500">{result}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            with col_match:
                st.markdown(f"**vs {opp}**")
                st.caption(f"{date} · {venue_label}")

            with col_stats:
                s1, s2, s3, s4, s5 = st.columns(5)
                s1.metric("Shots",    m.get("shots",      "—"))
                s2.metric("SOT",      m.get("sot",        "—"))
                s3.metric("xG",       m.get("xg",         "—"))
                s4.metric("Poss",     m.get("poss",       "—"))
                s5.metric("Corners",  m.get("corners",    "—"))

        st.divider()


# ── Player cards ──────────────────────────────────────────────

def show_player_cards(team_data):
    """
    Renders a card per player sorted FWD→MID→DEF→GK.
    Shows per-90 stats with a toggle between totals and per90.
    Injured players shown with red border and [INJ] badge.
    """
    from processor import get_all_player_stats

    players = get_all_player_stats(team_data)

    if not players:
        st.info("No player data available.")
        return

    # Display mode toggle
    mode = st.radio(
        "Stat display",
        options=["Totals", "Per 90 mins"],
        horizontal=True,
        label_visibility="collapsed",
    )

    pos_colours = {
        "FWD": ("#FCEBEB", "#791F1F"),
        "MID": ("#E6F1FB", "#0C447C"),
        "DEF": ("#EAF3DE", "#27500A"),
        "GK":  ("#F1EFE8", "#5F5E5A"),
    }

    current_pos = None

    for p in players:
        pos = p.get("pos", "GK")

        # Position section header when position changes
        if pos != current_pos:
            current_pos = pos
            section_header(
                {"FWD": "Forwards", "MID": "Midfielders",
                 "DEF": "Defenders", "GK": "Goalkeepers"}.get(pos, pos)
            )

        injured  = p.get("injured", False)
        name     = p.get("name",    p.get("n", "Unknown"))
        initials = p.get("initials",p.get("i", "?"))
        club     = p.get("club",    "")
        mins     = p.get("mins",    p.get("minutes", 0))
        rating   = p.get("rating", p.get("rtg", 0))
        note     = p.get("note",   "")

        pos_bg, pos_txt = pos_colours.get(pos, ("#F1EFE8", "#5F5E5A"))
        border = "#E24B4A" if injured else "#e0e0e0"

        with st.container():
            st.markdown(
                f'<div style="border:.5px solid {border};'
                f'border-radius:8px;padding:12px;'
                f'margin-bottom:8px;background:white">',
                unsafe_allow_html=True,
            )

            # Player header row
            h1, h2 = st.columns([1, 6])
            with h1:
                st.markdown(
                    f'<div style="width:38px;height:38px;'
                    f'border-radius:50%;background:{pos_bg};'
                    f'color:{pos_txt};display:flex;'
                    f'align-items:center;justify-content:center;'
                    f'font-size:12px;font-weight:500">'
                    f'{initials}</div>',
                    unsafe_allow_html=True,
                )
            with h2:
                inj_badge = ' <span style="color:#A32D2D;font-size:11px">[INJ]</span>' if injured else ""
                pos_badge = (
                    f'<span style="background:{pos_bg};color:{pos_txt};'
                    f'font-size:9px;padding:1px 5px;border-radius:3px;'
                    f'font-weight:500;margin-left:6px">{pos}</span>'
                )
                st.markdown(
                    f'<div style="font-size:14px;font-weight:500">'
                    f'{name}{inj_badge}{pos_badge}</div>'
                    f'<div style="font-size:11px;color:gray">'
                    f'{club} · {mins}min · Rating {rating}</div>',
                    unsafe_allow_html=True,
                )

            # Stat grid
            suffix = "_per90" if mode == "Per 90 mins" else ""
            stats_to_show = [
                ("Goals",    f"goals{suffix}"),
                ("Shots",    f"shots{suffix}"),
                ("xG",       f"xg{suffix}"),
                ("Key pass", f"keyPasses{suffix}"),
                ("Passes",   f"passes{suffix}"),
                ("Pass %",   "passAcc"),
                ("Tackles",  f"tackles{suffix}"),
                ("Intercept",f"interceptions{suffix}"),
                ("Duels",    f"duels{suffix}"),
                ("Rating",   "rating"),
            ]

            cols = st.columns(len(stats_to_show))
            for col, (label, field) in zip(cols, stats_to_show):
                val = p.get(field, p.get(field.replace("_per90",""), 0))
                if isinstance(val, float):
                    val = round(val, 2)
                col.metric(label, val)

            # Scouting note
            if note:
                st.caption(note)

            st.markdown("</div>", unsafe_allow_html=True)


# ── Team comparison ───────────────────────────────────────────

def show_comparison(team_data_a, team_data_b):
    """
    Side-by-side stat comparison between two teams.
    Highlights the team with the edge in each category.
    Shows form strips for both teams.
    """
    name_a = team_data_a.get("name", "Team A")
    name_b = team_data_b.get("name", "Team B")
    flag_a = team_data_a.get("flag", "🏳")
    flag_b = team_data_b.get("flag", "🏳")

    comp = get_comparison(team_data_a, team_data_b)
    avg_a = comp["team_a"]["all"]
    avg_b = comp["team_b"]["all"]
    edges = comp["edges"]
    form_a = comp["team_a"]["form"]
    form_b = comp["team_b"]["form"]

    # Team headers
    col_a, col_vs, col_b = st.columns([5, 1, 5])
    with col_a:
        st.markdown(f"### {flag_a} {name_a}")
        form_strip(form_a["strip"],
                   match_labels=team_data_a.get("formMatches", []))
        st.caption(
            f'{form_a["points"]}pts · '
            f'{form_a["pointsPerGame"]} PPG · '
            f'{form_a["trend"]}'
        )
    with col_vs:
        st.markdown(
            '<div style="text-align:center;font-size:18px;'
            'font-weight:300;padding-top:8px">vs</div>',
            unsafe_allow_html=True,
        )
    with col_b:
        st.markdown(f"### {flag_b} {name_b}")
        form_strip(form_b["strip"],
                   match_labels=team_data_b.get("formMatches", []))
        st.caption(
            f'{form_b["points"]}pts · '
            f'{form_b["pointsPerGame"]} PPG · '
            f'{form_b["trend"]}'
        )

    st.divider()

    # Stat comparison table
    for stat_def in H2H_COMPARISON_STATS:
        field    = stat_def["field"]
        label    = stat_def["label"]
        category = stat_def.get("category", "")
        edge     = edges.get(field, "even")

        val_a = avg_a.get(field, "—")
        val_b = avg_b.get(field, "—")

        col_val_a, col_label, col_val_b = st.columns([2, 3, 2])

        # Highlight winning side
        highlight_a = edge == "A"
        highlight_b = edge == "B"

        with col_val_a:
            style = "font-weight:600;color:#185FA5" if highlight_a else "color:gray"
            st.markdown(
                f'<div style="text-align:right;{style}">{val_a}</div>',
                unsafe_allow_html=True,
            )
        with col_label:
            st.markdown(
                f'<div style="text-align:center;font-size:12px;'
                f'color:gray">{label}</div>',
                unsafe_allow_html=True,
            )
        with col_val_b:
            style = "font-weight:600;color:#3B6D11" if highlight_b else "color:gray"
            st.markdown(
                f'<div style="text-align:left;{style}">{val_b}</div>',
                unsafe_allow_html=True,
            )


# ── H2H table ─────────────────────────────────────────────────

def show_h2h(team_data):
    """
    Renders the H2H match result and full stat table
    if H2H data exists in the team's JSON.
    """
    h2h = team_data.get("h2h", {})

    if not h2h:
        st.info("No head-to-head data available for this team.")
        return

    opp      = h2h.get("opp",     "Opponent")
    opp_flag = h2h.get("oppFlag", "🏳")
    date     = h2h.get("date",    "")
    venue    = h2h.get("venue",   "")
    score    = h2h.get("score",   "?-?")
    winner   = h2h.get("winner",  "")
    scorers  = h2h.get("scorers", "")

    team_name = team_data.get("name", "")
    team_flag = team_data.get("flag", "🏳")

    # Match summary header
    is_winner = winner == team_name
    colours   = RESULT_COLOURS["W"] if is_winner else RESULT_COLOURS["L"]

    st.markdown(
        f'<div style="background:{colours["bg"]};'
        f'border-radius:8px;padding:12px 16px;'
        f'margin-bottom:1rem;display:flex;'
        f'align-items:center;gap:12px">'
        f'<span style="font-size:20px;font-weight:500">'
        f'{team_flag} {team_name} {score} {opp_flag} {opp}</span>'
        f'<span style="background:{colours["bg"]};'
        f'color:{colours["text"]};font-size:12px;'
        f'font-weight:500;padding:2px 8px;border-radius:4px;'
        f'border:1px solid {colours["text"]}">'
        f'{winner} win</span>'
        f'<span style="font-size:12px;color:gray">'
        f'{date} · {venue}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if scorers:
        st.caption(f"Goals: {scorers}")

    # Full stat table
    rows = h2h.get("rows", [])
    if rows:
        st.markdown("---")
        col_l, col_m, col_r = st.columns([3, 4, 3])
        col_l.markdown(f"**{team_flag} {team_name}**")
        col_m.markdown('<div style="text-align:center"><b>Metric</b></div>',
                       unsafe_allow_html=True)
        col_r.markdown(f"**{opp_flag} {opp}**")

        for row in rows:
            highlight = row.get("highlight", False)
            left  = row.get("left",   "—")
            mid   = row.get("metric", "")
            right = row.get("right",  "—")

            weight = "font-weight:600" if highlight else ""
            bg     = "background:#f8f8f8;" if highlight else ""

            c1, c2, c3 = st.columns([3, 4, 3])
            with c1:
                st.markdown(
                    f'<div style="text-align:right;{weight};{bg}'
                    f'color:#0C447C;padding:3px 0">{left}</div>',
                    unsafe_allow_html=True,
                )
            with c2:
                st.markdown(
                    f'<div style="text-align:center;font-size:12px;'
                    f'color:gray;{bg}padding:3px 0">{mid}</div>',
                    unsafe_allow_html=True,
                )
            with c3:
                st.markdown(
                    f'<div style="text-align:left;{weight};{bg}'
                    f'color:#27500A;padding:3px 0">{right}</div>',
                    unsafe_allow_html=True,
                )

    # Insights
    insights = h2h.get("insights", [])
    if insights:
        st.markdown("---")
        section_header("Key takeaways")
        for insight in insights:
            with st.expander(insight.get("title", "Insight")):
                st.write(insight.get("body", ""))


# ── Probabilities ─────────────────────────────────────────────

def show_probabilities(team_data_a, team_data_b):
    """
    Renders the probability model output.
    Foundation layer — simple form-based model now,
    Poisson/advanced models slot in later.

    Shows: win/draw/loss %, implied fair odds,
    bookmaker odds input, value indicator.
    """
    import math

    prob_inputs = get_probability_inputs(team_data_a, team_data_b)
    inp_a = prob_inputs["team_a"]
    inp_b = prob_inputs["team_b"]

    name_a = team_data_a.get("name", "Team A")
    name_b = team_data_b.get("name", "Team B")
    flag_a = team_data_a.get("flag", "🏳")
    flag_b = team_data_b.get("flag", "🏳")

    # ── Simple model ──────────────────────────────────────────
    # Weighted score combining form, xG, and goals
    # Weights can be tuned in config later
    def team_strength(inp):
        return (
            inp["form_ppg"]     * 0.35 +
            inp["xg_for"]       * 0.35 +
            inp["avg_scored"]   * 0.20 +
            (3 - inp["avg_conceded"]) * 0.10
        )

    strength_a = max(team_strength(inp_a), 0.01)
    strength_b = max(team_strength(inp_b), 0.01)
    total      = strength_a + strength_b

    # Raw win probabilities
    raw_win_a  = strength_a / total
    raw_win_b  = strength_b / total

    # Draw probability — higher when teams are close in strength
    closeness   = 1 - abs(raw_win_a - raw_win_b)
    draw_prob   = round(closeness * 0.28, 3)   # 28% max draw probability

    # Normalise to sum to 1
    remaining   = 1 - draw_prob
    win_a_prob  = round(raw_win_a * remaining, 3)
    win_b_prob  = round(raw_win_b * remaining, 3)

    # Implied fair odds (decimal)
    def to_decimal_odds(prob):
        if prob <= 0:
            return "—"
        return round(1 / prob, 2)

    odds_a    = to_decimal_odds(win_a_prob)
    odds_draw = to_decimal_odds(draw_prob)
    odds_b    = to_decimal_odds(win_b_prob)

    # ── Display ───────────────────────────────────────────────
    st.markdown(
        f'<div style="text-align:center;font-size:18px;'
        f'font-weight:500;margin-bottom:1rem">'
        f'{flag_a} {name_a} vs {flag_b} {name_b}</div>',
        unsafe_allow_html=True,
    )

    # Probability bars
    section_header("Win probabilities")
    col_a, col_d, col_b = st.columns(3)

    with col_a:
        st.metric(f"{flag_a} {name_a} win", f"{win_a_prob*100:.1f}%")
        st.metric("Fair odds", odds_a)

    with col_d:
        st.metric("Draw", f"{draw_prob*100:.1f}%")
        st.metric("Fair odds", odds_draw)

    with col_b:
        st.metric(f"{flag_b} {name_b} win", f"{win_b_prob*100:.1f}%")
        st.metric("Fair odds", odds_b)

    # Visual probability bar
    st.markdown(
        f'<div style="display:flex;height:28px;'
        f'border-radius:6px;overflow:hidden;margin:1rem 0">'
        f'<div style="width:{win_a_prob*100:.1f}%;'
        f'background:#185FA5;display:flex;align-items:center;'
        f'justify-content:center;color:white;font-size:12px">'
        f'{win_a_prob*100:.1f}%</div>'
        f'<div style="width:{draw_prob*100:.1f}%;'
        f'background:#888780;display:flex;align-items:center;'
        f'justify-content:center;color:white;font-size:12px">'
        f'{draw_prob*100:.1f}%</div>'
        f'<div style="width:{win_b_prob*100:.1f}%;'
        f'background:#3B6D11;display:flex;align-items:center;'
        f'justify-content:center;color:white;font-size:12px">'
        f'{win_b_prob*100:.1f}%</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Bookmaker odds input for value calculation
    st.divider()
    section_header("Value calculator — enter bookmaker odds")
    st.caption("Enter decimal odds from your bookmaker to check for value")

    bc1, bc2, bc3 = st.columns(3)
    with bc1:
        bk_a = st.number_input(
            f"{name_a} win odds",
            min_value=1.0, value=float(odds_a) if isinstance(odds_a, float) else 2.0,
            step=0.05, key="bk_a"
        )
    with bc2:
        bk_draw = st.number_input(
            "Draw odds",
            min_value=1.0, value=float(odds_draw) if isinstance(odds_draw, float) else 3.0,
            step=0.05, key="bk_draw"
        )
    with bc3:
        bk_b = st.number_input(
            f"{name_b} win odds",
            min_value=1.0, value=float(odds_b) if isinstance(odds_b, float) else 2.0,
            step=0.05, key="bk_b"
        )

    # Value calculation
    section_header("Value analysis")

    def calc_value(our_prob, bk_odds, label):
        implied_prob = 1 / bk_odds
        edge = our_prob - implied_prob
        ev   = (our_prob * (bk_odds - 1)) - (1 - our_prob)

        if edge > VALUE_THRESHOLD:
            colour = "#3B6D11"
            verdict = f"✓ Value bet — {edge*100:.1f}% edge"
        elif edge < -VALUE_THRESHOLD:
            colour = "#A32D2D"
            verdict = f"✗ No value — bookmaker has {abs(edge)*100:.1f}% edge"
        else:
            colour = "#888780"
            verdict = "~ Fair price"

        st.markdown(
            f'<div style="border-left:3px solid {colour};'
            f'padding:.5rem .75rem;margin-bottom:.5rem;'
            f'background:#f9f9f9;border-radius:0 6px 6px 0">'
            f'<strong>{label}</strong><br>'
            f'<span style="color:{colour}">{verdict}</span><br>'
            f'<span style="font-size:12px;color:gray">'
            f'Our prob: {our_prob*100:.1f}% · '
            f'Implied: {implied_prob*100:.1f}% · '
            f'EV: {ev:+.3f}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    calc_value(win_a_prob, bk_a,   f"{flag_a} {name_a} win")
    calc_value(draw_prob,  bk_draw, "Draw")
    calc_value(win_b_prob, bk_b,   f"{flag_b} {name_b} win")

    st.caption(
        "⚠️ Model uses form, xG, and goals scored/conceded. "
        "Advanced Poisson model coming next. "
        "Not financial advice."
    )




