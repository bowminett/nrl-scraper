# NRL Scraper

A Selenium-based web scraper that extracts detailed per-player and team-level match statistics from [nrl.com](https://www.nrl.com), organised by season and round and combined into master CSVs for analysis and modelling.

## Project Structure

```
nrl-scraper/
├── run.py                      ← entry point — only file you run
├── config.py                   ← match details and settings — only file you edit
├── scrapers/
│   ├── driver.py               ← Chrome/Selenium setup
│   ├── match_scraper.py        ← per-player stats scraping
│   └── team_scraper.py         ← team-level stats scraping
├── processing/
│   └── combine.py              ← combines round CSVs into master files
└── data/
    ├── raw/
    │   └── 2026/
    │       └── round_20/
    │           ├── player_stats/
    │           │   ├── panthers.csv
    │           │   └── broncos.csv
    │           └── team_stats/
    │               └── panthers_v_broncos.csv
    └── processed/
        ├── player_stats_2026.csv
        └── team_stats_2026.csv
```

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/bowminett/nrl-scraper.git
cd nrl-scraper
```

**2. Install dependencies**
```bash
pip install selenium webdriver-manager pandas
```

Chrome must be installed. ChromeDriver is handled automatically — no manual setup needed.

## Usage

### Single Match

Edit the match details in `config.py`:
```python
HOME_TEAM = "Panthers"
AWAY_TEAM = "Broncos"
ROUND_NUM = "20"
YEAR = "2026"
```

Choose a mode at the bottom of `run.py` and run:
```bash
python run.py
```

### Available Scrape Modes

Swap the function call at the bottom of `run.py` to change what gets scraped:

| Function | What it does |
|---|---|
| `scrape_player_single()` | Player stats for one match (from config.py) |
| `scrape_player_multiple(ROUND_20)` | Player stats for a full round |
| `scrape_team_single()` | Team stats for one match (from config.py) |
| `scrape_team_multiple(ROUND_20)` | Team stats for a full round |
| `scrape_all_single()` | Both player and team stats for one match |
| `scrape_all_multiple(ROUND_20)` | Both player and team stats for a full round |
| `scrape_all_multiple(ALL_FIXTURES)` | Full season, both stat types |

Fixtures for every round of the 2026 season are pre-loaded in `run.py` as `ROUND_12` through `ROUND_27` and combined into `ALL_FIXTURES`.

### Combining into Master CSVs

After scraping, run `combine.py` to merge all round CSVs into master files:

```bash
python processing/combine.py
```

Change the year at the top of `combine.py` if needed:
```python
COMBINE_YEAR = 2026
```

This produces two files in `data/processed/`:
- `player_stats_2026.csv` — one row per player per match
- `team_stats_2026.csv` — one row per team per match

Both files can be joined on `Year`, `Round`, `Team`, and `Opponent` for combined analysis.

## Output

### Player Stats
Saved to `data/raw/{year}/round_{round}/player_stats/` — one CSV per team per match.

Each CSV contains one row per player with 62 columns:

| Column | Description |
|---|---|
| Year, Round, Team, Opponent, Player | Match and player metadata |
| Number, Position, Mins Played | Player details |
| Tries, Try Assists, Line Breaks, Line Break Assists | Attack |
| All Runs, All Run Metres, Post Contact Metres, Hit Ups | Running |
| Tackles Made, Missed Tackles, Tackle Efficiency | Defence |
| Kicks, Kicking Metres, Bomb Kicks, Grubbers, 40/20 | Kicking |
| Errors, Penalties, Sin Bins, Send Offs | Discipline |

### Team Stats
Saved to `data/raw/{year}/round_{round}/team_stats/` — one CSV per match containing both teams.

Each CSV contains two rows (one per team) with columns including:

| Column | Description |
|---|---|
| Year, Round, Team, Opponent, Is_Home | Match metadata |
| Score, Result | Final score and win/loss/draw |
| Tries, Conversions, Penalty Goals | Scoring breakdown |
| Possession, Completion Rate | Ball control |
| Total Run Metres, Missed Tackles, Errors | Key performance stats |
| Interchanges Used, Sin Bins, Send Offs | Discipline |

## Configuration

All settings live in `config.py`:

| Setting | Default | Description |
|---|---|---|
| `HEADLESS` | `False` | `True` runs Chrome in the background |
| `WAIT_TIMEOUT` | `15` | Seconds to wait for page elements to load |
| `DELAY` | `1.5` | Seconds between requests (multiple scrapes) |
| `OUTPUT_DIR` | `data/raw` | Root output directory |

Set `HEADLESS = True` when running full season scrapes in the background. Keep `False` while debugging so you can see what the browser is doing.

## Notes

- Team names must match nrl.com URL slugs — use the team's short name as it appears in match URLs. `Wests Tigers` is handled automatically.
- Scrapes each game sequentially with a delay between requests — skips a match on error and continues rather than crashing the whole run.
- `combine.py` deduplicates automatically so it's safe to re-run after scraping additional rounds.
