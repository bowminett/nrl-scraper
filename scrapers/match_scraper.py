# scrapers/match_scraper.py
# Scrapes player stats for a single NRL match

import pandas as pd
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import STAT_HEADERS, OUTPUT_DIR, WAIT_TIMEOUT


class MatchScraper:
    """
    Scrapes per-player stats for both teams in a single NRL match.

    Usage:
        scraper = MatchScraper(driver)
        df_home, df_away = scraper.scrape("Panthers", "Broncos", "20", "2026")
    """

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, WAIT_TIMEOUT)

    def scrape(
        self,
        home_team: str,
        away_team: str,
        round_num: str,
        year: str,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Scrape one match. Returns (df_home, df_away).
        Also saves both CSVs to OUTPUT_DIR.
        """
        url = self._build_url(home_team, away_team, round_num, year)
        print(f"  Navigating to: {url}")
        self.driver.get(url)

        self._click_player_stats_tab()

        df_home = self._scrape_team(home_team, away_team, round_num, year)
        self._switch_to_away_team(away_team)
        df_away = self._scrape_team(away_team, home_team, round_num, year)

        self._save(df_home, home_team, round_num, year)
        self._save(df_away, away_team, round_num, year)

        return df_home, df_away

    # ── Private methods ───────────────────────────────────────────────────────

    def _build_url(self, home_team, away_team, round_num, year) -> str:
        home_slug = home_team.lower().replace(" ", "-")
        away_slug = away_team.lower().replace(" ", "-")
        return (
            f"https://www.nrl.com/draw/nrl-premiership/{year}/"
            f"round-{round_num}/{home_slug}-v-{away_slug}/"
        )

    def _click_player_stats_tab(self):
        """Click the Player Stats tab on the match centre page."""
        btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(.,'Player Stats')]"))
        )
        btn.click()

    def _switch_to_away_team(self, away_team: str):
        """Click the away team button to switch the stats table."""
        btn = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//button[contains(.,'{away_team}')]")
            )
        )
        btn.click()
        # Wait for away table to render
        self.wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                f"//caption[contains(., '{away_team} Player Stats')]",
            ))
        )

    def _scrape_team(
        self,
        team: str,
        opponent: str,
        round_num: str,
        year: str,
    ) -> pd.DataFrame:
        """Extract all player rows for one team."""
        table = self.driver.find_element(
            By.XPATH,
            f"//caption[contains(., '{team} Player Stats')]/parent::table",
        )
        rows = table.find_elements(By.CSS_SELECTOR, "tr.table-tbody__tr")

        players = []
        for row in rows:
            player = self._parse_row(row, team, opponent, round_num, year)
            if player:
                players.append(player)

        print(f"    {team}: {len(players)} players scraped")
        return pd.DataFrame(players)

    def _parse_row(
        self,
        row,
        team: str,
        opponent: str,
        round_num: str,
        year: str,
    ) -> dict | None:
        """Parse a single player row into a dict. Returns None if row is invalid."""
        try:
            name = row.find_element(
                By.CSS_SELECTOR, "td.table-tbody__td--player-name a"
            ).get_attribute("innerText").strip()
        except Exception:
            return None

        cells = row.find_elements(By.TAG_NAME, "td")
        stats = [
            cell.get_attribute("innerText").strip()
            for cell in cells
            if "table-tbody__td--player-name" not in (cell.get_attribute("class") or "")
            and cell.get_attribute("innerText").strip() != ""
        ]

        player = {
            "Year": year,
            "Round": round_num,
            "Team": team,
            "Opponent": opponent,
            "Player": name,
        }
        for header, value in zip(STAT_HEADERS, stats):
            player[header] = value

        return player

    def _save(self, df: pd.DataFrame, team: str, round_num: str, year: str):
        """Save a team's stats to CSV."""
        out_dir = Path(OUTPUT_DIR) / year / f"round_{round_num}"
        out_dir.mkdir(parents=True, exist_ok=True)

        slug = team.lower().replace(" ", "_")
        path = out_dir / f"{slug}.csv"
        df.to_csv(path, index=False)
        print(f"    Saved → {path}")