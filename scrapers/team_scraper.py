# scrapers/team_scraper.py
import pandas as pd
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import WAIT_TIMEOUT, OUTPUT_DIR, TEAM_STAT_DEFAULTS, TEAM_STAT_SHOTS


class TeamScraper:
    """
    Scrapes team-level stats for both teams in a single NRL match.
    Reuses the same driver as MatchScraper.

    Usage:
        scraper = TeamScraper(driver)
        df = scraper.scrape("Eels", "Panthers", "21", "2026")
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
    ) -> pd.DataFrame:
        """Scrape team stats for both teams. Returns DataFrame and saves CSV."""
        url = f"https://www.nrl.com/draw/nrl-premiership/{year}/round-{round_num}/{home_team.lower().replace(' ', '-')}-v-{away_team.lower().replace(' ', '-')}/"
        print(f"  Scraping team stats: {home_team} vs {away_team} | Round {round_num} {year}...")
        self.driver.get(url)

        stats_home = {
            "Year": year, "Round": round_num,
            "Team": home_team, "Opponent": away_team, "Is_Home": True,
        }
        stats_away = {
            "Year": year, "Round": round_num,
            "Team": away_team, "Opponent": home_team, "Is_Home": False,
        }

        # Set default zeros
        for key in TEAM_STAT_DEFAULTS:
            stats_home[key] = 0
            stats_away[key] = 0

        for key in TEAM_STAT_SHOTS:
            stats_home[key] = 0
            stats_away[key] = 0

        self._scrape_summary(stats_home, stats_away)
        self._click_team_stats_tab()
        self._scrape_bar_charts(stats_home, stats_away)
        self._scrape_possession(stats_home, stats_away)
        self._scrape_donuts(stats_home, stats_away)
        self._calculate_score(stats_home, stats_away)

        df = pd.DataFrame([stats_home, stats_away])
        df = df.replace(r'\n', '', regex=True)
        df = df.rename(columns={"USED": "INTERCHANGES USED"})

        self._save(df, home_team, away_team, round_num, year)
        return df

    # ── Private methods ───────────────────────────────────────────────────────

    def _scrape_summary(self, stats_home, stats_away):
        """Scrape tries, conversions, sin bins etc from match summary."""
        wait = WebDriverWait(self.driver, 15)
        wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "match-centre-summary-group"))
    )
        groups = self.driver.find_elements(By.CLASS_NAME, "match-centre-summary-group")

        for group in groups:
            try:
                label = group.find_element(
                    By.CLASS_NAME, "match-centre-summary-group__name"
                ).get_attribute("innerText").strip()

                values = group.find_elements(
                    By.CLASS_NAME, "match-centre-summary-group__value"
                )
                home_val = values[0].get_attribute("innerText").strip() if len(values) >= 1 else 0
                away_val = values[1].get_attribute("innerText").strip() if len(values) >= 2 else 0

                stats_home[label] = home_val
                stats_away[label] = away_val
            except Exception:
                continue

    def _click_team_stats_tab(self):
        """Click the Team Stats tab."""
        btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(.,'Team Stats')]"))
        )
        btn.click()
        self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "stats-bar-chart"))
        )

    def _scrape_bar_charts(self, stats_home, stats_away):
        """Scrape all bar chart stats."""
        for figure in self.driver.find_elements(By.CLASS_NAME, "stats-bar-chart"):
            try:
                label = figure.find_element(
                    By.CLASS_NAME, "stats-bar-chart__title"
                ).get_attribute("innerText").strip()
            except Exception:
                continue

            try:
                home_val = figure.find_element(
                    By.XPATH, ".//*[contains(@class, '--home')]"
                ).get_attribute("innerText").strip()
            except Exception:
                home_val = None

            try:
                away_val = figure.find_element(
                    By.XPATH, ".//*[contains(@class, '--away')]"
                ).get_attribute("innerText").strip()
            except Exception:
                away_val = None

            stats_home[label] = home_val
            stats_away[label] = away_val

    def _scrape_possession(self, stats_home, stats_away):
        """Scrape possession from single donut chart."""
        try:
            stats_home["POSSESSION %"] = self.driver.find_element(
                By.CLASS_NAME, "match-centre-card-donut__value--home"
            ).get_attribute("innerText").strip()

            stats_away["POSSESSION %"] = self.driver.find_element(
                By.CLASS_NAME, "match-centre-card-donut__value--away"
            ).get_attribute("innerText").strip()
        except Exception:
            pass

    def _scrape_donuts(self, stats_home, stats_away):
        """Scrape double donut stats (completion rate, avg PTB speed etc)."""
        sections = self.driver.find_elements(
            By.CSS_SELECTOR, ".u-spacing-pb-24.u-spacing-pt-16.u-width-100"
        )
        for section in sections:
            try:
                label = section.find_element(
                    By.CLASS_NAME, "stats-bar-chart__title"
                ).get_attribute("innerText").strip()
            except Exception:
                continue

            donuts = section.find_elements(By.CLASS_NAME, "match-centre-card-donut")
            if len(donuts) < 2:
                continue

            try:
                home_val = donuts[0].find_element(
                    By.CLASS_NAME, "donut-chart-stat__value"
                ).get_attribute("innerText").strip()
            except Exception:
                home_val = None

            try:
                away_val = donuts[1].find_element(
                    By.CLASS_NAME, "donut-chart-stat__value"
                ).get_attribute("innerText").strip()
            except Exception:
                away_val = None

            stats_home[label] = home_val
            stats_away[label] = away_val

    def _calculate_score(self, stats_home, stats_away):
        """Calculate final score and result from scraped stats."""
        def calc(stats):
            tries = int(str(stats.get("TRIES", 0)).split("/")[0] or 0)
            conversions = int(str(stats.get("CONVERSIONS", 0)).split("/")[0] or 0)
            penalty_goals = int(str(stats.get("PENALTY GOALS", 0)).split("/")[0] or 0)
            field_goals_1pt = int(str(stats.get("1 POINT FIELD GOALS", 0)).split("/")[0] or 0)
            field_goals_2pt = int(str(stats.get("2 POINT FIELD GOALS", 0)).split("/")[0] or 0)
            return (tries * 4) + (conversions * 2) + (penalty_goals * 2) + field_goals_1pt + (field_goals_2pt * 2)

        stats_home["SCORE"] = calc(stats_home)
        stats_away["SCORE"] = calc(stats_away)

        if stats_home["SCORE"] > stats_away["SCORE"]:
            stats_home["RESULT"] = "WIN"
            stats_away["RESULT"] = "LOSS"
        elif stats_home["SCORE"] < stats_away["SCORE"]:
            stats_home["RESULT"] = "LOSS"
            stats_away["RESULT"] = "WIN"
        else:
            stats_home["RESULT"] = "DRAW"
            stats_away["RESULT"] = "DRAW"

    def _save(self, df, home_team, away_team, round_num, year):
        """Save to data/raw/{year}/round_{round}/team_stats/"""
        out_dir = Path(OUTPUT_DIR) / str(year) / f"round_{round_num}" / "team_stats"
        out_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{home_team.lower().replace(' ', '_')}_v_{away_team.lower().replace(' ', '_')}.csv"
        out_path = out_dir / filename
        df.to_csv(out_path, index=False)
        print(f"  Saved → {out_path}")