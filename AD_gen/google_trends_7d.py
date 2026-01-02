# AD_gen/google_trends_7d.py

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# use relative imports now that AD_gen is a package
from .trend_research_agent import google_search
from .trend_summarizer_agent import summarize_trend
from .insert_db import insert_trends_to_db



def scrape_daily_trends_7d():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # optionally headless
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    url = "https://trends.google.com/trending?geo=IN&hours=168"
    driver.get(url)
    time.sleep(3)

    try:
        cookie_btn = driver.find_element(By.XPATH, "//button[text()='I agree']")
        cookie_btn.click()
        time.sleep(2)
    except NoSuchElementException:
        pass

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//tr[@role='row']"))
        )
        rows = driver.find_elements(By.XPATH, "//tr[@role='row']")
    except TimeoutException:
        with open("debug_7d.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        driver.quit()
        return

    trends = []
    for row in rows:
        try:
            title = row.find_element(By.CSS_SELECTOR, "div.mZ3RIc").text.strip()
        except Exception:
            continue

        volume = "N/A"
        try:
            volume = row.find_element(By.CSS_SELECTOR, "div.lqv0Cb").text.strip()
        except NoSuchElementException:
            pass

        start_time = "N/A"
        try:
            start_time = row.find_element(By.CSS_SELECTOR, "div.vdw3Ld").text.strip()
        except NoSuchElementException:
            pass

        trends.append({
            "topic": title,
            "volume": volume,
            "start_time": start_time
        })

    # Enrich & insert
    for trend in trends:
        topic = trend["topic"]
        results = google_search(topic)
        trend["summary"] = summarize_trend(topic, results)

    insert_trends_to_db(trends, table_name="google_trends_7d")
    driver.quit()


if __name__ == "__main__":
    scrape_daily_trends_7d()
