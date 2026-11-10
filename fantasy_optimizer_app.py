import streamlit as st
import os
import sys
import json
from pathlib import Path

# Robust path handling for local + Streamlit Cloud
def add_helpers_to_path():
    possible_paths = [
        Path(__file__).parent / "espn-fantasy" / "scripts",
        Path(__file__).parent / "scripts",
        Path.cwd() / "espn-fantasy" / "scripts",
        Path.cwd() / "scripts",
    ]
    for p in possible_paths:
        if p.exists() and (p / "espn_helpers.py").exists():
            sys.path.insert(0, str(p))
            return True
    return False

if not add_helpers_to_path():
    st.error("""
    **Could not find espn_helpers.py**
    
    Make sure your GitHub repo has this structure:
    ```
    your-repo/
    ├── fantasy_optimizer_app.py
    ├── requirements.txt
    └── espn-fantasy/
        └── scripts/
            └── espn_helpers.py
    ```
    """)
    st.stop()

try:
    import espn_helpers
except ImportError as e:
    st.error(f"Import failed even after finding the file: {e}")
    st.stop()

# Page config
st.set_page_config(
    page_title="Fantasy Optimizer",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e3a5f;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #64748b;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    div[data-testid="stSidebar"] {
        background-color: #0f172a;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for profiles
if "profiles" not in st.session_state:
    st.session_state.profiles = {}
if "active_profile" not in st.session_state:
    st.session_state.active_profile = None
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Cookie instructions
COOKIE_INSTRUCTIONS = """
### How to get your ESPN cookies (espn_s2 and SWID)

1. Open **Safari** or **Chrome** on your computer and go to [fantasy.espn.com](https://fantasy.espn.com)
2. Log in to your ESPN account
3. Open Developer Tools:
   - **Chrome**: Press `F12` or right-click → Inspect
   - **Safari**: Enable Develop menu first (Safari → Settings → Advanced → Show Develop menu), then Develop → Show Web Inspector
4. Go to the **Application** (Chrome) or **Storage** (Safari) tab
5. Click **Cookies** → `https://fantasy.espn.com`
6. Find and copy these two values:
   - `espn_s2` (long string)
   - `SWID` (looks like `{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}`)
7. Paste them into the form below

**Note:** These cookies act like a password. Only share them with people you trust, and never post them publicly.
"""

# Login / Profile Setup Screen
if not st.session_state.authenticated:
    st.markdown('<div class="main-header">Fantasy Optimizer</div>', unsafe_allow_html=True)
    st.markdown("Connect your own ESPN fantasy team. Your data stays private to this session.")
    
    tab_login, tab_help = st.tabs(["Set Up Profile", "How to Get Cookies"])
    
    with tab_help:
        st.markdown(COOKIE_INSTRUCTIONS)
    
    with tab_login:
        st.subheader("Create or Load a Profile")
        
        profile_name = st.text_input("Profile Name", placeholder="e.g. My Team, Eddie's Osheas")
        league_id = st.text_input("League ID", placeholder="From the URL: leagueId=...")
        team_id = st.text_input("Team ID", placeholder="From the URL: teamId=...")
        espn_s2 = st.text_area("espn_s2 cookie", height=100, placeholder="Paste your espn_s2 value here")
        swid = st.text_input("SWID cookie", placeholder="{xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save & Connect", type="primary", use_container_width=True):
                if profile_name and league_id and team_id:
                    st.session_state.profiles[profile_name] = {
                        "league_id": league_id,
                        "team_id": team_id,
                        "espn_s2": espn_s2 or None,
                        "swid": swid or None,
                        "name": profile_name
                    }
                    st.session_state.active_profile = profile_name
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.warning("Profile name, League ID, and Team ID are required.")
        
        with col2:
            if st.session_state.profiles:
                existing = st.selectbox("Or load existing profile", [""] + list(st.session_state.profiles.keys()))
                if existing and st.button("Load Profile", use_container_width=True):
                    st.session_state.active_profile = existing
                    st.session_state.authenticated = True
                    st.rerun()
    
    st.stop()

# Once authenticated, load the active profile
profile = st.session_state.profiles.get(st.session_state.active_profile, {})

def get_league_data():
    if not profile:
        return None, None
    os.environ["ESPN_LEAGUE_ID"] = str(profile.get("league_id", "0"))
    os.environ["ESPN_YEAR"] = "2026"
    os.environ["ESPN_SPORT"] = "ffl"
    if profile.get("espn_s2"):
        os.environ["ESPN_S2"] = profile["espn_s2"]
        os.environ["ESPN_SWID"] = profile.get("swid", "")
    else:
        os.environ.pop("ESPN_S2", None)
        os.environ.pop("ESPN_SWID", None)
    
    try:
        league = espn_helpers.get_league()
        team_id = int(profile.get("team_id", 1))
        team = None
        for t in league.teams:
            if t.team_id == team_id:
                team = t
                break
        return league, team
    except Exception as e:
        st.error(f"Failed to load league: {e}")
        return None, None

# Sidebar
with st.sidebar:
    st.markdown("### 🏈 Fantasy Optimizer")
    st.caption(f"Profile: **{st.session_state.active_profile}**")
    if st.button("Switch Profile / Log Out", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.active_profile = None
        st.rerun()
    st.markdown("---")
    page = st.radio(
        "Navigate",
        options=[
            "📋 Roster",
            "⚡ Optimal Lineup",
            "🔄 Waiver Wire",
            "🆓 Free Agents",
            "🤝 Trade Analyzer",
            "📊 Insights"
        ],
        index=0
    )
    st.markdown("---")
    st.caption("Built for Eddie & friends")

# Main content
st.markdown('<div class="main-header">Fantasy Team Optimizer</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">Profile: <strong>{st.session_state.active_profile}</strong></div>', unsafe_allow_html=True)

league, team = get_league_data()

if team:
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Record", f"{getattr(team, 'wins', 0)}-{getattr(team, 'losses', 0)}")
    with col2:
        st.metric("Team", getattr(team, 'team_name', 'N/A')[:20])
    with col3:
        st.metric("Players", len(team.roster) if team.roster else 0)
    with col4:
        st.metric("Status", "Connected")

    st.markdown("---")

    # Page content based on sidebar selection
    if page == "📋 Roster":
        st.subheader("Current Roster")
        if team.roster:
            roster_data = []
            for p in team.roster:
                roster_data.append({
                    "Player": p.name,
                    "Position": p.position,
                    "Team": getattr(p, "proTeam", ""),
                    "Status": getattr(p, 'injuryStatus', 'ACTIVE'),
                    "Projected": getattr(p, 'projected_points', '—')
                })
            st.dataframe(roster_data, use_container_width=True, hide_index=True)
        else:
            st.info("No roster data available.")

    elif page == "⚡ Optimal Lineup":
        st.subheader("Recommended Starting Lineup")
        st.info("Lineup recommendations will appear here once multi-source data is integrated. For now, review your roster and use the Free Agents and Waiver sections.")
        st.caption("Full optimal lineup engine coming in the next update.")

    elif page == "🔄 Waiver Wire":
        st.subheader("Waiver Wire Recommendations")
        st.info("Check the Free Agents section for available players, then cross-reference with FantasyPros and PFF for the best adds.")

    elif page == "🆓 Free Agents":
        st.subheader("Free Agents")
        col_pos, col_size = st.columns([1, 1])
        with col_pos:
            position_filter = st.selectbox("Position", ["All", "QB", "RB", "WR", "TE", "K", "D/ST"], index=0)
        with col_size:
            size = st.slider("How many to show", 5, 30, 15)
        
        if st.button("Load Free Agents", type="primary"):
            with st.spinner("Fetching free agents from ESPN..."):
                try:
                    pos = None if position_filter == "All" else position_filter
                    fas = league.free_agents(size=size, position=pos)
                    if fas:
                        fa_data = []
                        for p in fas:
                            fa_data.append({
                                "Player": p.name,
                                "Pos": getattr(p, "position", ""),
                                "NFL Team": getattr(p, "proTeam", ""),
                                "Projected Pts": getattr(p, "projected_points", "—"),
                                "Injury": getattr(p, "injuryStatus", "ACTIVE")
                            })
                        st.dataframe(fa_data, use_container_width=True, hide_index=True)
                        st.success(f"Loaded {len(fa_data)} free agents")
                    else:
                        st.info("No free agents found for that filter.")
                except Exception as e:
                    st.error(f"Could not load free agents: {e}")

    elif page == "🤝 Trade Analyzer":
        st.subheader("Trade Analyzer")
        st.markdown("Evaluate potential trades.")
        
        if team.roster:
            give_players = st.multiselect(
                "Players you would give",
                options=[p.name for p in team.roster]
            )
            receive_input = st.text_input("Players you would receive (comma separated)")
            
            if st.button("Analyze Trade", type="primary"):
                st.markdown(f"**Giving:** {', '.join(give_players) if give_players else 'None'}")
                st.markdown(f"**Receiving:** {receive_input or 'None'}")
                st.info("Compare projected points, positional needs, and rest-of-season outlook. Cross-check with FantasyPros ECR and PFF.")
        else:
            st.info("Load your roster first.")

    elif page == "📊 Insights":
        st.subheader("Multi-Source Insights")
        st.markdown("""
        **How recommendations are made**
        - Highest weight: FantasyPros Expert Consensus Rankings and PFF
        - Medium weight: Usage (targets, snaps), matchups, injury reports
        - Lower weight: ESPN projections alone
        
        Always verify final decisions on ESPN before locking your lineup.
        """)

else:
    st.error("Could not load team data. Double-check your League ID, Team ID, and cookies.")

st.markdown("---")
st.caption("Personal fantasy tool • Profiles are saved for this browser session only")
