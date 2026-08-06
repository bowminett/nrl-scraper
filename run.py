# run.py
# ── Entry point — edit config.py to change teams/round/year ──────────────────
#
# Options:
#   scrape_player_single()    — one match, player stats
#   scrape_player_multiple()  — multiple matches, player stats
#   scrape_team_single()      — one match, team stats
#   scrape_team_multiple()    — multiple matches, team stats
#   scrape_all_single()       — one match, both player and team stats
#   scrape_all_multiple()     — multiple matches, both player and team stats
#
# Change the function call at the bottom to switch modes.

from scrapers.driver import get_driver
from scrapers.match_scraper import MatchScraper
from scrapers.team_scraper import TeamScraper
from config import HOME_TEAM, AWAY_TEAM, ROUND_NUM, YEAR, HEADLESS
import time
from scrapers.draw_2026 import *



# ── Player stats only ─────────────────────────────────────────────────────────

def scrape_player_single():
    """Scrape player stats for one match (uses config.py values)."""
    print(f"\nPlayer stats: {HOME_TEAM} vs {AWAY_TEAM} | Round {ROUND_NUM} {YEAR}")
    driver = get_driver(headless=HEADLESS)
    try:
        scraper = MatchScraper(driver)
        scraper.scrape(HOME_TEAM, AWAY_TEAM, ROUND_NUM, YEAR)
    finally:
        driver.quit()


def scrape_player_multiple(fixtures: list):
    """Scrape player stats for multiple matches."""
    print(f"\nScraping player stats for {len(fixtures)} matches...")
    driver = get_driver(headless=HEADLESS)
    scraper = MatchScraper(driver)
    try:
        for i, (home, away, round_num, year) in enumerate(fixtures):
            print(f"\n[{i+1}/{len(fixtures)}] {home} vs {away} | Round {round_num} {year}")
            try:
                scraper.scrape(home, away, round_num, year)
            except Exception as e:
                print(f"  [ERROR] Skipping — {e}")
            time.sleep(1.5)
    finally:
        driver.quit()
    print("\nDone.")


# ── Team stats only ───────────────────────────────────────────────────────────

def scrape_team_single():
    """Scrape team stats for one match (uses config.py values)."""
    print(f"\nTeam stats: {HOME_TEAM} vs {AWAY_TEAM} | Round {ROUND_NUM} {YEAR}")
    driver = get_driver(headless=HEADLESS)
    try:
        scraper = TeamScraper(driver)
        scraper.scrape(HOME_TEAM, AWAY_TEAM, ROUND_NUM, YEAR)
    finally:
        driver.quit()


def scrape_team_multiple(fixtures: list):
    """Scrape team stats for multiple matches."""
    print(f"\nScraping team stats for {len(fixtures)} matches...")
    driver = get_driver(headless=HEADLESS)
    scraper = TeamScraper(driver)
    try:
        for i, (home, away, round_num, year) in enumerate(fixtures):
            print(f"\n[{i+1}/{len(fixtures)}] {home} vs {away} | Round {round_num} {year}")
            try:
                scraper.scrape(home, away, round_num, year)
            except Exception as e:
                print(f"  [ERROR] Skipping — {e}")
            time.sleep(1.5)
    finally:
        driver.quit()
    print("\nDone.")


# ── Both player and team stats ────────────────────────────────────────────────

def scrape_all_single():
    """Scrape both player and team stats for one match (uses config.py values)."""
    print(f"\nFull scrape: {HOME_TEAM} vs {AWAY_TEAM} | Round {ROUND_NUM} {YEAR}")
    driver = get_driver(headless=HEADLESS)
    try:
        MatchScraper(driver).scrape(HOME_TEAM, AWAY_TEAM, ROUND_NUM, YEAR)
        TeamScraper(driver).scrape(HOME_TEAM, AWAY_TEAM, ROUND_NUM, YEAR)
    finally:
        driver.quit()


def scrape_all_multiple(fixtures: list):
    """Scrape both player and team stats for multiple matches."""
    print(f"\nFull scrape for {len(fixtures)} matches...")
    driver = get_driver(headless=HEADLESS)
    match_scraper = MatchScraper(driver)
    team_scraper = TeamScraper(driver)
    try:
        for i, (home, away, round_num, year) in enumerate(fixtures):
            print(f"\n[{i+1}/{len(fixtures)}] {home} vs {away} | Round {round_num} {year}")
            try:
                match_scraper.scrape(home, away, round_num, year)
                team_scraper.scrape(home, away, round_num, year)
            except Exception as e:
                print(f"  [ERROR] Skipping — {e}")
            time.sleep(1.5)
    finally:
        driver.quit()
    print("\nDone.")


# ── Run ───────────────────────────────────────────────────────────────────────
# Swap the function call below to change mode:
#
#   scrape_player_single()            one match, player stats (from config.py)
#   scrape_player_multiple(ROUND_21)  one round, player stats
#   scrape_player_multiple(ALL_FIXTURES) full season, player stats
#
#   scrape_team_single()              one match, team stats (from config.py)
#   scrape_team_multiple(ROUND_21)    one round, team stats
#   scrape_team_multiple(ALL_FIXTURES)   full season, team stats
#
#   scrape_all_single()               one match, both
#   scrape_all_multiple(ROUND_21)     one round, both

if __name__ == "__main__":
    scrape_team_multiple(ROUND_17)