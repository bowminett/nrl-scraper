from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

HOME_TEAM = "Panthers"
AWAY_TEAM = "Broncos"
ROUND_NUM = "20"
YEAR = "2026"

def get_url_name(team_name):
    return team_name.replace(" ", "-")

HOME_URL_NAME = get_url_name(HOME_TEAM)
AWAY_URL_NAME = get_url_name(AWAY_TEAM)

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
    "Stint Two"
]

GAME_LINK = f"https://www.nrl.com/draw/nrl-premiership/{YEAR}/round-{ROUND_NUM}/{HOME_URL_NAME}-v-{AWAY_URL_NAME}/"


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

driver.get(GAME_LINK)

# Wait up to 10 seconds for the element to appear

try:
    button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(.,'Player Stats')]")))
    button.click()

    wait = WebDriverWait(driver, 5)
   

    # Find the Panthers table
    home_table = driver.find_element(
    By.XPATH,
    f"//caption[contains(., '{HOME_TEAM} Player Stats')]/parent::table"
)

    home_rows = home_table.find_elements(
        By.CSS_SELECTOR,
        "tr.table-tbody__tr"
    )

    players_home = []

    for row in home_rows:

        # Player name
        name = row.find_element(
            By.CSS_SELECTOR,
            "td.table-tbody__td--player-name a"
        ).get_attribute("innerText").strip()

        # All stat cells
        stats = []

        cells = row.find_elements(By.TAG_NAME, "td")

        for cell in cells:

            if "table-tbody__td--player-name" in cell.get_attribute("class"):
                continue

            value = cell.get_attribute("innerText").strip()

            if value != "":
                stats.append(value)

        player = {
            "Year": YEAR,
            "Round": ROUND_NUM,
            "Team": HOME_TEAM,
            "Opponent": AWAY_TEAM,
            "Player": name
        }

        for header, value in zip(STAT_HEADERS, stats):
            player[header] = value

        players_home.append(player)

    df_home = pd.DataFrame(players_home)

    df_home.to_csv(f"data/{HOME_URL_NAME}_{ROUND_NUM}_{YEAR}.csv", index=False)


    #Scrape away-team data
    
    button = driver.find_element(By.XPATH, f"//button[contains(.,'{AWAY_TEAM}')]")
    

    button.click()

    away_table = driver.find_element(
    By.XPATH,
    f"//caption[contains(., '{AWAY_TEAM} Player Stats')]/parent::table"
)

    away_rows = away_table.find_elements(
        By.CSS_SELECTOR,
        "tr.table-tbody__tr"
    )

    players_away = []

    for row in away_rows:

        # Player name
        name = row.find_element(
            By.CSS_SELECTOR,
            "td.table-tbody__td--player-name a"
        ).get_attribute("innerText").strip()

        # All stat cells
        stats = []

        cells = row.find_elements(By.TAG_NAME, "td")

        for cell in cells:
            if "table-tbody__td--player-name" in cell.get_attribute("class"):
                continue

            value = cell.get_attribute("innerText").strip()

            if value != "":
                stats.append(value)

        player = {
            "Year": YEAR,
            "Round": ROUND_NUM,
            "Team": AWAY_TEAM,
            "Opponent": HOME_TEAM,
            "Player": name
        }

        for header, value in zip(STAT_HEADERS, stats):
            player[header] = value

        players_away.append(player)

    df_away = pd.DataFrame(players_away)
    df_away.to_csv(f"data/{AWAY_URL_NAME}_{ROUND_NUM}_{YEAR}.csv", index=False)



finally:
    driver.quit()