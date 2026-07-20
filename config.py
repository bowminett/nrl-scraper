# config.py
# ── The only file you need to edit ───────────────────────────────────────────

# Match details
HOME_TEAM = "Wests Tigers"
AWAY_TEAM = "Warriors"
ROUND_NUM = "19"
YEAR = "2026"

# Scraper settings
HEADLESS = True         # True = browser runs in background, False = visible window
WAIT_TIMEOUT = 10       # seconds to wait for page elements
DELAY = 1.5             # seconds between requests when scraping multiple games

# Output
OUTPUT_DIR = "data/raw"

# ── Stat headers (do not edit unless NRL.com adds/removes columns) ────────────
STAT_HEADERS = [
    "Number",
    "Position",
    "Mins Played",
    "Points",
    "Tries",
    "Conversions",
    "Conversion Attempts",
    "Penalty Goals",
    "Goal Conversion Rate",
    "1 Point Field Goals",
    "2 Point Field Goals",
    "Total Points",
    "All Runs",
    "All Run Metres",
    "Kick Return Metres",
    "Post Contact Metres",
    "Line Breaks",
    "Line Break Assists",
    "Try Assists",
    "Line Engaged Runs",
    "Tackle Breaks",
    "Hit Ups",
    "Play The Ball",
    "Average Play The Ball Speed",
    "Dummy Half Runs",
    "Dummy Half Run Metres",
    "One on One Steal",
    "Offloads",
    "Dummy Passes",
    "Passes",
    "Receipts",
    "Passes To Run Ratio",
    "Tackle Efficiency",
    "Tackles Made",
    "Missed Tackles",
    "Ineffective Tackles",
    "Intercepts",
    "Kicks Defused",
    "Kicks",
    "Kicking Metres",
    "Forced Drop Outs",
    "Bomb Kicks",
    "Grubbers",
    "40/20",
    "20/40",
    "Cross Field Kicks",
    "Kicked Dead",
    "Errors",
    "Handling Errors",
    "One on One Lost",
    "Penalties",
    "Ruck Infringements",
    "Inside 10 Metres",
    "On Report",
    "Sin Bins",
    "Send Offs",
    "Stint One",
    "Stint Two",
]