#!/usr/bin/env python3
"""
ESPN Fantasy helpers.
Usage:
  python espn_helpers.py roster [team_id]
  python espn_helpers.py freeagents [position] [size]
  python espn_helpers.py standings
  python espn_helpers.py matchup [week]

Requires: pip install espn_api
Env: ESPN_LEAGUE_ID, ESPN_YEAR, ESPN_S2, ESPN_SWID, ESPN_SPORT (ffl|fba)
"""

import os
import sys
import json

try:
    from espn_api.football import League as FootballLeague
    from espn_api.basketball import League as BasketballLeague
except ImportError:
    print("Install with: pip install espn_api", file=sys.stderr)
    sys.exit(1)


def get_league():
    league_id = int(os.environ.get("ESPN_LEAGUE_ID", "0"))
    year = int(os.environ.get("ESPN_YEAR", str(2026)))
    espn_s2 = os.environ.get("ESPN_S2") or None
    swid = os.environ.get("ESPN_SWID") or None
    sport = os.environ.get("ESPN_SPORT", "ffl").lower()

    if league_id == 0:
        print("Error: ESPN_LEAGUE_ID not set", file=sys.stderr)
        sys.exit(1)

    kwargs = {"league_id": league_id, "year": year, "espn_s2": espn_s2, "swid": swid}
    if sport in ("fba", "basketball", "nba"):
        return BasketballLeague(**kwargs)
    return FootballLeague(**kwargs)


def cmd_roster(args):
    league = get_league()
    team_id = int(args[0]) if args else None
    team = league.get_team_data(team_id) if team_id else league.teams[0]
    if not team:
        print("Team not found", file=sys.stderr)
        return
    data = {
        "team_name": team.team_name,
        "wins": getattr(team, "wins", None),
        "losses": getattr(team, "losses", None),
        "roster": [
            {
                "name": p.name,
                "position": p.position,
                "playerId": getattr(p, "playerId", None),
                "proTeam": getattr(p, "proTeam", ""),
                "injuryStatus": getattr(p, "injuryStatus", ""),
            }
            for p in getattr(team, "roster", [])
        ],
    }
    print(json.dumps(data, indent=2))


def cmd_freeagents(args):
    league = get_league()
    position = args[0] if args else None
    size = int(args[1]) if len(args) > 1 else 20
    fas = league.free_agents(size=size, position=position)
    data = [
        {
            "name": p.name,
            "position": getattr(p, "position", ""),
            "playerId": getattr(p, "playerId", None),
            "proTeam": getattr(p, "proTeam", ""),
            "projected_points": getattr(p, "projected_points", None),
        }
        for p in fas
    ]
    print(json.dumps(data, indent=2))


def cmd_standings(args):
    league = get_league()
    standings = league.standings()
    data = [
        {
            "rank": i + 1,
            "team_name": t.team_name,
            "wins": t.wins,
            "losses": t.losses,
            "points_for": getattr(t, "points_for", None),
        }
        for i, t in enumerate(standings)
    ]
    print(json.dumps(data, indent=2))


def cmd_matchup(args):
    league = get_league()
    week = int(args[0]) if args else None
    scoreboard = league.scoreboard(week=week)
    data = []
    for m in scoreboard:
        data.append({
            "home": m.home_team.team_name if m.home_team else None,
            "away": m.away_team.team_name if m.away_team else None,
            "home_score": m.home_score,
            "away_score": m.away_score,
        })
    print(json.dumps(data, indent=2))


COMMANDS = {
    "roster": cmd_roster,
    "freeagents": cmd_freeagents,
    "standings": cmd_standings,
    "matchup": cmd_matchup,
}


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print("Usage: espn_helpers.py <command> [args]")
        print("Commands:", ", ".join(COMMANDS))
        sys.exit(1)
    cmd = sys.argv[1]
    COMMANDS[cmd](sys.argv[2:])