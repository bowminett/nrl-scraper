# scrapers/driver.py
# Handles Chrome/Selenium setup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def get_driver(headless: bool = False) -> webdriver.Chrome:
    """
    Create and return a configured Chrome WebDriver.
    headless=True runs Chrome in the background with no visible window.
    """
    options = webdriver.ChromeOptions()

    if headless:
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    return driver