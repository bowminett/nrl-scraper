from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from pathlib import Path

HOME_TEAM = "Eels"
AWAY_TEAM = "Panthers"
ROUND_NUM = "21"
YEAR = "2026"

def get_url_name(team_name):
    return team_name.lower().replace(" ", "-")

GAME_LINK = f"https://www.nrl.com/draw/nrl-premiership/{YEAR}/round-{ROUND_NUM}/{get_url_name(HOME_TEAM)}-v-{get_url_name(AWAY_TEAM)}/"

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get(GAME_LINK)

try:
    # Initialise with match metadata
    stats_home = {
        "Year": YEAR, "Round": ROUND_NUM,
        "Team": HOME_TEAM, "Opponent": AWAY_TEAM, "Is_Home": True
    }
    stats_away = {
        "Year": YEAR, "Round": ROUND_NUM,
        "Team": AWAY_TEAM, "Opponent": HOME_TEAM, "Is_Home": False
    }
    # ── Score + Match Events (scrape before clicking any tab) ────────────
    # ── Defaults — always present in CSV even if stat didn't occur ────────
    for key in ["TRIES", "CONVERSIONS", "1 POINT FIELD GOALS", 
                "2 POINT FIELD GOALS", "PENALTY GOALS", 
                "SIN BINS", "SEND OFFS", "HALF TIME"]:
        stats_home[key] = 0
        stats_away[key] = 0

# ── Scrape summary group ──────────────────────────────────────────────
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "match-centre-summary-group"))
    )

    summary_groups = driver.find_elements(By.CLASS_NAME, "match-centre-summary-group")

    for group in summary_groups:
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
    
    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(.,'Team Stats')]"))
    )
    button.click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "stats-bar-chart"))
    )

    

    # ── Section 1: Bar charts ─────────────────────────────────────────
    for figure in driver.find_elements(By.CLASS_NAME, "stats-bar-chart"):
        try:
            label = figure.find_element(
                By.CLASS_NAME, "stats-bar-chart__title"
            ).get_attribute("innerText").strip()
        except:
            continue

        try:
            home_val = figure.find_element(
                By.XPATH, ".//*[contains(@class, '--home')]"
            ).get_attribute("innerText").strip()
        except:
            home_val = None

        try:
            away_val = figure.find_element(
                By.XPATH, ".//*[contains(@class, '--away')]"
            ).get_attribute("innerText").strip()
        except:
            away_val = None

        stats_home[label] = home_val
        stats_away[label] = away_val

    # ── Section 2: Possession (single donut) ─────────────────────────
    try:
        stats_home["POSSESSION %"] = driver.find_element(
            By.CLASS_NAME, "match-centre-card-donut__value--home"
        ).get_attribute("innerText").strip()

        stats_away["POSSESSION %"] = driver.find_element(
            By.CLASS_NAME, "match-centre-card-donut__value--away"
        ).get_attribute("innerText").strip()
    except:
        print("  [WARN] Possession not found")

    # ── Section 3: Double donuts ──────────────────────────────────────
    for section in driver.find_elements(
        By.CSS_SELECTOR, ".u-spacing-pb-24.u-spacing-pt-16.u-width-100"
    ):
        try:
            label = section.find_element(
                By.CLASS_NAME, "stats-bar-chart__title"
            ).get_attribute("innerText").strip()
        except:
            continue

        donuts = section.find_elements(By.CLASS_NAME, "match-centre-card-donut")
        if len(donuts) < 2:
            continue

        try:
            home_val = donuts[0].find_element(
                By.CLASS_NAME, "donut-chart-stat__value"
            ).get_attribute("innerText").strip()
        except:
            home_val = None

        try:
            away_val = donuts[1].find_element(
                By.CLASS_NAME, "donut-chart-stat__value"
            ).get_attribute("innerText").strip()
        except:
            away_val = None

        stats_home[label] = home_val
        stats_away[label] = away_val

    # ── Calculate final score ─────────────────────────────────────────────
    def calc_score(stats: dict) -> int:
        tries = int(str(stats.get("TRIES", 0)).split("/")[0] or 0)
        conversions = int(str(stats.get("CONVERSIONS", 0)).split("/")[0] or 0)
        penalty_goals = int(str(stats.get("PENALTY GOALS", 0)).split("/")[0] or 0)
        field_goals_1pt = int(str(stats.get("1 POINT FIELD GOALS", 0)).split("/")[0] or 0)
        field_goals_2pt = int(str(stats.get("2 POINT FIELD GOALS", 0)).split("/")[0] or 0)

        return (tries * 4) + (conversions * 2) + (penalty_goals * 2) + field_goals_1pt + (field_goals_2pt * 2)

    stats_home["SCORE"] = calc_score(stats_home)
    stats_away["SCORE"] = calc_score(stats_away)

    # Derive result
    if stats_home["SCORE"] > stats_away["SCORE"]:
        stats_home["RESULT"] = "WIN"
        stats_away["RESULT"] = "LOSS"
    elif stats_home["SCORE"] < stats_away["SCORE"]:
        stats_home["RESULT"] = "LOSS"
        stats_away["RESULT"] = "WIN"
    else:
        stats_home["RESULT"] = "DRAW"
        stats_away["RESULT"] = "DRAW"

    # ── Save to CSV ───────────────────────────────────────────────────
    df = pd.DataFrame([stats_home, stats_away])

    out_dir = Path(f"data/raw/{YEAR}/round_{ROUND_NUM}/team_stats")
    out_dir.mkdir(parents=True, exist_ok=True)
    # ── Clean up ──────────────────────────────────────────────────────────
    df = df.replace(r'\n', '', regex=True)
    df = df.rename(columns={"USED": "INTERCHANGES USED"})

    filename = f"{get_url_name(HOME_TEAM)}_v_{get_url_name(AWAY_TEAM)}.csv"
    out_path = out_dir / filename
    df.to_csv(out_path, index=False)

    print(f"\nSaved → {out_path}")

finally:
    driver.quit()