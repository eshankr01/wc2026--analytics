# =============================================================
# app.py — entry point, layout and navigation only
# Run with: streamlit run app.py
# =============================================================

import streamlit as st
import json
from pathlib import Path
from config import (
    TOURNAMENT_NAME,
    GROUPS,
    FLAGS,
    DATA_FILE,
    MATCHES_TO_ANALYZE,
)
from display import (
    show_team_header,
    show_team_averages,
    show_match_cards,
    show_player_cards,
    show_comparison,
    show_h2h,
    show_probabilities,
)


# ── Page configuration ────────────────────────────────────────
# Must be the first Streamlit call in the script

st.set_page_config(
    page_title="WC 2026 Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Data loading ──────────────────────────────────────────────
# @st.cache_data tells Streamlit: run this function once,
# store the result in memory, reuse it on every rerun.
# Without this, the JSON file would be re-read on every
# single user interaction — slow and unnecessary.

@st.cache_data
def load_data():
    path = Path(DATA_FILE)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    # Convert list of teams into a dict keyed by name
    # so we can look up any team instantly: data["USA"]
    teams = {t["name"]: t for t in raw.get("teams", [])}
    return teams


# ── Load everything ───────────────────────────────────────────

all_teams = load_data()

# ── Session state defaults ────────────────────────────────────
# Streamlit reruns the script on every interaction.
# Session state persists values between reruns.
# We set defaults here so the main area always has
# something to render on the very first load.

if "page" not in st.session_state:
    st.session_state.page = "Team dashboard"
if "selected_group" not in st.session_state:
    st.session_state.selected_group = "B"
if "selected_team" not in st.session_state:
    st.session_state.selected_team = "USA"
if "team_a" not in st.session_state:
    st.session_state.team_a = "USA"
if "team_b" not in st.session_state:
    st.session_state.team_b = "Paraguay"


# ── Sidebar navigation ────────────────────────────────────────

with st.sidebar:
    st.title("⚽ WC 2026")
    st.divider()

    # Search bar — primary navigation
    search = st.text_input(
        "Search team",
        placeholder="🔍 Search any team...",
        label_visibility="collapsed",
    )

    page = st.radio(
        "Section",
        options=["Team dashboard", "Compare teams", "Probabilities"],
        label_visibility="collapsed",
        key="page",
    )

    st.divider()

    if page == "Team dashboard":

        # Search bar
        search = st.text_input(
            "Search team",
            placeholder="Type team name...",
            label_visibility="collapsed",
        )

        # Flatten all teams for search
        all_team_names = sorted([t for teams in GROUPS.values() for t in teams])

        if search:
            # Filter teams matching search
            matches_search = [
                t for t in all_team_names
                if search.lower() in t.lower()
            ]
            if matches_search:
                selected_team = st.radio(
                    "Results",
                    options=matches_search,
                    format_func=lambda t: f"{FLAGS.get(t,'🏳')} {t}",
                    label_visibility="collapsed",
                    key="search_result",
                )
                st.session_state.selected_team = selected_team
                # Find and set the group
                for g, teams in GROUPS.items():
                    if selected_team in teams:
                        st.session_state.selected_group = g
                        break
            else:
                st.caption("No teams found")

        else:
            # Group selector
            selected_group = st.selectbox(
                "Group",
                options=list(GROUPS.keys()),
                format_func=lambda g: f"Group {g}",
                key="selected_group",
            )

            # Team grid — show all teams in group as buttons
            st.caption(f"Group {selected_group} teams")
            group_teams = GROUPS[selected_group]

            for team in group_teams:
                has_data = team in all_teams
                flag = FLAGS.get(team, "🏳")
                is_selected = team == st.session_state.get("selected_team")

                # Highlight selected team
                label = f"{flag} {team} {'✓' if has_data else '—'}"
                if st.button(
                    label,
                    key=f"team_btn_{team}",
                    use_container_width=True,
                    type="primary" if is_selected else "secondary",
                ):
                    st.session_state.selected_team = team

    elif page == "Compare teams":
        all_team_names = [t for teams in GROUPS.values() for t in teams]

        team_a = st.selectbox(
            "Team A",
            options=all_team_names,
            format_func=lambda t: f"{FLAGS.get(t, '')} {t}",
            key="team_a",
        )
        team_b = st.selectbox(
            "Team B",
            options=all_team_names,
            format_func=lambda t: f"{FLAGS.get(t, '')} {t}",
            key="team_b",
        )


# ── Main content area ─────────────────────────────────────────
# Pull values from session state directly
# This guarantees variables always exist regardless of which
# sidebar branch ran

# ── Main content area ─────────────────────────────────────────

from display import (
    show_team_header,
    show_team_averages,
    show_match_cards,
    show_player_cards,
    show_comparison,
    show_h2h,
    show_probabilities,
)

current_page   = st.session_state.page
current_team   = st.session_state.get("selected_team", "USA")
current_team_a = st.session_state.get("team_a", "USA")
current_team_b = st.session_state.get("team_b", "Paraguay")

# ── Match count toggle ────────────────────────────────────────
col_toggle, _ = st.columns([2, 6])
with col_toggle:
    match_count = st.radio(
        "Analyze last",
        options=[5, 10],
        format_func=lambda x: f"Last {x} matches",
        horizontal=True,
        label_visibility="collapsed",
        key="match_count",
    )


if current_page == "Team dashboard":
    team_data = all_teams.get(current_team)

if current_page == "Team dashboard":
    team_data = all_teams.get(current_team)

    if team_data is None:
        st.title(f"{FLAGS.get(current_team, '')} {current_team}")
        st.warning(
            f"No data loaded for {current_team} yet. "
            f"Ask Claude to fetch their last {MATCHES_TO_ANALYZE} "
            f"matches and paste the JSON block into data/wc2026_data.json."
        )
    else:
        from processor import get_team_summary
        summary = get_team_summary(team_data)

        show_team_header(team_data, summary)

        tab_avg, tab_matches, tab_players, tab_h2h = st.tabs([
            "Averages", "Match cards", "Players", "H2H"
        ])

        with tab_avg:
            show_team_averages(summary)
        with tab_matches:
            show_match_cards(team_data)
        with tab_players:
            show_player_cards(team_data)
        with tab_h2h:
            show_h2h(team_data)

elif current_page == "Compare teams":
    data_a = all_teams.get(current_team_a)
    data_b = all_teams.get(current_team_b)

    if not data_a or not data_b:
        missing = current_team_a if not data_a else current_team_b
        st.warning(f"No data loaded for {missing} yet.")
    else:
        show_comparison(data_a, data_b)

elif current_page == "Probabilities":
    data_a = all_teams.get(current_team_a)
    data_b = all_teams.get(current_team_b)

    if not data_a or not data_b:
        st.warning("Select two teams with data loaded to run the model.")
        st.info("Go to Compare teams in the sidebar to pick your teams.")
    else:
        show_probabilities(data_a, data_b)