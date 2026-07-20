# run.py
# ── Entry point — edit config.py to change teams/round/year ──────────────────
#
# Single match:   python run.py
# Multiple games: set FIXTURES below and run python run.py
#
# Output saved to data/raw/{year}/round_{round}/

from scrapers.driver import get_driver
from scrapers.match_scraper import MatchScraper
from config import HOME_TEAM, AWAY_TEAM, ROUND_NUM, YEAR, HEADLESS
import time

# ── Option 1: Single match (uses config.py values) ───────────────────────────
def scrape_single():
    print(f"\nScraping: {HOME_TEAM} vs {AWAY_TEAM} | Round {ROUND_NUM} {YEAR}")
    driver = get_driver(headless=HEADLESS)
    try:
        scraper = MatchScraper(driver)
        df_home, df_away = scraper.scrape(HOME_TEAM, AWAY_TEAM, ROUND_NUM, YEAR)
        print(f"\nDone. {len(df_home) + len(df_away)} players scraped.")
    finally:
        driver.quit()


# ── Option 2: Multiple matches ────────────────────────────────────────────────
# Add fixtures as (home_team, away_team, round_num, year)
FIXTURES = [
    ("Panthers", "Rabbitohs", "18", "2026"),
    ("Cowboys", "Panthers", "17", "2026"),
    ("Titans", "Panthers", "16", "2026"),
]

def scrape_multiple():
    print(f"\nScraping {len(FIXTURES)} matches...")
    driver = get_driver(headless=HEADLESS)
    scraper = MatchScraper(driver)

    try:
        for i, (home, away, round_num, year) in enumerate(FIXTURES):
            print(f"\n[{i+1}/{len(FIXTURES)}] {home} vs {away} | Round {round_num} {year}")
            try:
                scraper.scrape(home, away, round_num, year)
            except Exception as e:
                print(f"  [ERROR] Skipping — {e}")
            time.sleep(1.5)  # be polite between requests

    finally:
        driver.quit()

    print("\nAll done.")


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    scrape_multiple()       # swap to scrape_multiple() for a full round or scrape_single() for a single match