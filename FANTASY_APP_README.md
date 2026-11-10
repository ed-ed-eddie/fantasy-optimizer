# Fantasy Optimizer Dashboard

A clean, visually polished Streamlit dashboard for managing and optimizing your ESPN Fantasy Football teams (Osheas & Masterclass).

## Features
- League switcher (Osheas / Masterclass)
- Roster overview
- Recommended optimal lineup (multi-source weighted)
- Waiver wire recommendations
- **Live free agents table** (filter by position)
- **Trade analyzer** (compare players you give vs receive)
- Insights & decision framework

## How to Run

```bash
# From the artifacts directory
streamlit run fantasy_optimizer_app.py
```

The app will open in your browser (usually http://localhost:8501).

## Notes
- Masterclass league uses stored cookies for private access.
- Full live free-agent pulls and real-time multi-source scraping can be expanded.
- This is a personal tool for you and friends — not a public multi-tenant service.
- Always double-check lineups on ESPN before locking.

## Next Improvements
- Live free agent table
- Trade analyzer
- Weekly matchup projections
- Historical performance tracking
