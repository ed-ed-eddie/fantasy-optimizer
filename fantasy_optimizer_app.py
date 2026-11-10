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

# Custom CSS for a polished look
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
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 24px;
        border-radius: 8px 8px 0 0;
        background-color: #f1f5f9;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e40af;
        color: white;
    }
    div[data-testid="stSidebar"] {
        background-color: #0f172a;
    }
    .player-card {
        background: #ffffff;
        border-left: 4px solid #3b82f6;
        padding: 12px 16px;
        margin: 8px 0;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# League configurations
LEAGUES = {
    "Osheas": {
        "league_id": 1591415094,
        "team_id": 1,
        "name": "Ed Eds and Eddie's",
        "private": False,
        "espn_s2": None,
        "swid": None
    },
    "Masterclass": {
        "league_id": 1601467769,
        "team_id": 11,
        "name": "Ed’s Ed’s and Eddie’s",
        "private": True,
        "espn_s2": os.environ.get("ESPN_S2", "AEBJbXG%2FnXs%2BZ0O%2BVW0JksUekWFbx9sZu0NzCqwZaHlJLDUCilEKdNyl2j6kH%2BwYEAmPg%2BbiIQZ8rPptzlijZGmHWSISkD09VuWiN1HayEdtFzZsdps5B6RnPXCWOefpTU3MD%2FlGOBI%2F6iDkXQoW4%2BKI3hUP1kqNgKE9ptkUBJ4bkbC76P7STWPamIHVfc921zHg7GF%2F7uKx4Qcyl7ABXMxuolFN129oe180gn6PBMMEPQQSgiSoNBULzAU2XghTFVfNFeBGnjFVd%2BGX0%2BcvaJzjHcOcguaqHvCDKd3QssvmA2MLNhTbDFKGz%2BUHhzTfE9Hu%2FxMm2jjV2ZsHsjOUaIjR"),
        "swid": os.environ.get("ESPN_SWID", "{76659dbb-50d5-4f6a-8843-e024086d4705}")
    }
}

def get_league_data(league_key):
    config = LEAGUES[league_key]
    os.environ["ESPN_LEAGUE_ID"] = str(config["league_id"])
    os.environ["ESPN_YEAR"] = "2026"
    os.environ["ESPN_SPORT"] = "ffl"
    if config["private"]:
        os.environ["ESPN_S2"] = config["espn_s2"]
        os.environ["ESPN_SWID"] = config["swid"]
    else:
        os.environ.pop("ESPN_S2", None)
        os.environ.pop("ESPN_SWID", None)
    
    try:
        # Use the helper's get_league or directly
        league = espn_helpers.get_league()
        team = league.get_team_data(config["team_id"]) if hasattr(league, 'get_team_data') else None
        if not team:
            # Fallback
            for t in league.teams:
                if t.team_id == config["team_id"]:
                    team = t
                    break
        return league, team
    except Exception as e:
        st.error(f"Failed to load league: {e}")
        return None, None

# Sidebar
with st.sidebar:
    st.markdown("### 🏈 Fantasy Optimizer")
    st.markdown("---")
    selected_league = st.radio(
        "Select League",
        options=list(LEAGUES.keys()),
        index=0
    )
    st.markdown("---")
    st.markdown("**Features**")
    st.caption("• Roster Overview")
    st.caption("• Optimized Lineup")
    st.caption("• Waiver Wire")
    st.caption("• Free Agents Table")
    st.caption("• Trade Analyzer")
    st.caption("• Multi-source insights")
    st.markdown("---")
    st.caption("Built for Eddie & friends")
    st.caption("Week 9 • 2026 Season")

# Main content
st.markdown('<div class="main-header">Fantasy Team Optimizer</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">Managing <strong>{selected_league}</strong> • Multi-source recommendations</div>', unsafe_allow_html=True)

league, team = get_league_data(selected_league)

if team:
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Record", f"{team.wins}-{team.losses}")
    with col2:
        st.metric("Team", LEAGUES[selected_league]["name"][:20])
    with col3:
        st.metric("Players", len(team.roster) if team.roster else 0)
    with col4:
        st.metric("Status", "Active")

    st.markdown("---")

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Roster", "⚡ Optimal Lineup", "🔄 Waiver Wire", "🆓 Free Agents", "🤝 Trade Analyzer"])

    with tab1:
        st.subheader("Current Roster")
        if team.roster:
            roster_data = []
            for p in team.roster:
                roster_data.append({
                    "Player": p.name,
                    "Position": p.position,
                    "Team": p.proTeam,
                    "Status": getattr(p, 'injuryStatus', 'ACTIVE'),
                    "Projected": getattr(p, 'projected_points', '—')
                })
            st.dataframe(roster_data, use_container_width=True, hide_index=True)
        else:
            st.info("No roster data available.")

    with tab2:
        st.subheader("Recommended Starting Lineup")
        st.info("Recommendations weighted by FantasyPros ECR, PFF, and matchup data (higher-accuracy sources prioritized).")
        
        # Example optimized lineup based on previous analysis
        if selected_league == "Osheas":
            lineup = {
                "QB": "Brock Purdy",
                "RB1": "J.K. Dobbins",
                "RB2": "Dylan Sampson",
                "WR1": "Puka Nacua",
                "WR2": "Drake London",
                "TE": "Brock Bowers",
                "FLEX": "Jordan Mason",
                "D/ST": "Chiefs D/ST",
                "K": "Will Reichard"
            }
            notes = "Pollard on bye. Sampson preferred over Mason for RB2 due to matchup. Mason strong FLEX."
        else:
            lineup = {
                "QB": "Drake Maye",
                "RB1": "Omarion Hampton",
                "RB2": "Tyler Allgeier",
                "WR1": "Ja'Marr Chase",
                "WR2": "Jaylen Waddle",
                "TE": "Brock Bowers",
                "FLEX": "Ladd McConkey",
                "D/ST": "Vikings D/ST",
                "K": "Will Reichard"
            }
            notes = "Pollard on bye. Allgeier is clear RB2. McConkey safest FLEX."

        for slot, player in lineup.items():
            st.markdown(f'<div class="player-card"><strong>{slot}</strong> — {player}</div>', unsafe_allow_html=True)
        
        st.caption(notes)

    with tab3:
        st.subheader("Waiver Wire Recommendations")
        st.info("Top waiver targets based on multi-source consensus (FantasyPros, PFF, usage). Prioritize high-upside players with favorable matchups.")
        
        if selected_league == "Osheas":
            st.markdown("**Suggested adds**")
            st.markdown("- High-volume RBs in good matchups")
            st.markdown("- WRs with rising target share")
            st.markdown("**Potential drops**")
            st.markdown("- Long-term injured players or low-usage backups")
        else:
            st.markdown("**Suggested adds**")
            st.markdown("- RB depth (especially with Henderson out)")
            st.markdown("- WR upside plays")
        
        st.caption("Cross-reference with the Free Agents tab for live availability.")

    with tab4:
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

    with tab5:
        st.subheader("Trade Analyzer")
        st.markdown("Evaluate potential trades using multi-source rankings and roster needs.")
        
        col_give, col_get = st.columns(2)
        
        with col_give:
            st.markdown("**Players You Give**")
            give_players = st.multiselect(
                "Select from your roster",
                options=[p.name for p in team.roster] if team.roster else [],
                key="give"
            )
        
        with col_get:
            st.markdown("**Players You Receive**")
            # Simple text input for incoming players (can be expanded later)
            receive_input = st.text_input("Enter player names (comma separated)", placeholder="e.g. Player A, Player B")
        
        if st.button("Analyze Trade", type="primary"):
            if not give_players and not receive_input:
                st.warning("Add at least one player on each side.")
            else:
                with st.spinner("Analyzing..."):
                    st.markdown("### Trade Analysis")
                    st.markdown(f"**Giving:** {', '.join(give_players) if give_players else 'None'}")
                    st.markdown(f"**Receiving:** {receive_input or 'None'}")
                    
                    # Placeholder logic — in a full version this would pull rankings
                    st.info("""
                    **Recommendation Framework**
                    - Compare projected points and ECR ranks
                    - Check positional needs on both teams
                    - Factor in schedule, injury risk, and rest-of-season outlook
                    - Higher-weight sources (FantasyPros, PFF) preferred over ESPN-only
                    """)
                    
                    if selected_league == "Osheas":
                        st.success("For Osheas: Prioritize RB/WR depth upgrades. Avoid overpaying for bye-week fillers.")
                    else:
                        st.success("For Masterclass: Look for RB upgrades or WR consistency. Bowers and Chase are core holds.")
                    
                    st.caption("Full live ranking comparison coming soon. Use this as a starting point and cross-check with external sources.")

else:
    st.error("Could not load team data. Check credentials and network.")

st.markdown("---")
st.caption("Personal fantasy tool • Recommendations are suggestions only • Always verify before setting lineups on ESPN")
