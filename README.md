# NRL Player Stats Scraper

A Selenium-based web scraper that extracts detailed per-player match statistics from [nrl.com](https://www.nrl.com) and saves them as CSVs, organised by season and round.

## Project Structure

```
nrl-analysis/
├── run.py                  ← entry point — only file you run
├── config.py               ← match details and settings — only file you edit
├── scrapers/
│   ├── driver.py           ← Chrome/Selenium setup
│   └── match_scraper.py    ← scraping logic
└── data/
    └── raw/
        └── 2026/
            └── round/
```

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/bowminett/nrl-analysis.git
cd nrl-analysis
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

Make sure the last line of `run.py` says `scrape_single()`, then run:
```bash
python run.py
```

### Multiple Matches

Edit the `FIXTURES` list in `run.py`:
```python
FIXTURES = [
    ("Panthers", "Rabbitohs", "18", "2026"),
    ("Cowboys", "Panthers", "17", "2026"),
    ("Titans", "Panthers", "16", "2026"),
]
```

Change the last line of `run.py` to `scrape_multiple()`, then run:
```bash
python run.py
```

Scrapes each game sequentially with a 1.5 second delay between requests. Skips a match on error and continues rather than crashing the whole run.

## Output

CSVs are saved to `data/raw/{year}/round_{round}/` — folders are created automatically.

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

## Configuration

All settings live in `config.py`:

| Setting | Default | Description |
|---|---|---|
| `HEADLESS` | `False` | `True` runs Chrome in the background |
| `WAIT_TIMEOUT` | `10` | Seconds to wait for page elements to load |
| `DELAY` | `1.5` | Seconds between requests (multiple scrapes) |
| `OUTPUT_DIR` | `data/raw` | Root output directory |
