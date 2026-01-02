import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
# from trend_research_agent import google_search
# from trend_summarizer_agent import summarize_trend


def scrape_daily_trends():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Use this to run without opening browser
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    url = "https://trends.google.com/trends/trendingsearches/daily?geo=IN"
    driver.get(url)

    time.sleep(3)
    try:
        cookie_btn = driver.find_element(By.XPATH, "//button[text()='I agree']")
        cookie_btn.click()
        print("Clicked cookie consent button.")
        time.sleep(2)
    except NoSuchElementException:
        print("No cookie popup found, continuing...")

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//tr[@role='row']"))
        )
        rows = driver.find_elements(By.XPATH, "//tr[@role='row']")
    except TimeoutException:
        print("Timed out waiting for trend rows.")
        with open("debug_daily.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        driver.quit()
        return

    print(f"\n Found {len(rows)} trending rows:\n")

    trends = []

    for i, row in enumerate(rows, start=1):
        try:
            title = row.find_element(By.CSS_SELECTOR, "div.mZ3RIc").text.strip()

            try:
                volume = row.find_element(By.CSS_SELECTOR, "div.lqv0Cb").text.strip()
            except NoSuchElementException:
                volume = "N/A"

            try:
                started = row.find_element(By.CSS_SELECTOR, "div.vdw3Ld").text.strip()
            except NoSuchElementException:
                started = "N/A"

            trends.append({
                "topic": title,
                "volume": volume,
                "start_time": started
            })

        except Exception as e:
            print(f"Error processing row {i}: {str(e)[:100]}")
            continue

    print(f"\nCollected {len(trends)} trends.\n")

    from trend_research_agent import google_search
    from trend_summarizer_agent import summarize_trend
    from insert_db import insert_trends_to_db

    # Enrich each trend with a summary
    for trend in trends:
        topic = trend["topic"]
        print(f"\n Searching: {topic}")
        search_results = google_search(topic)

        print(f"Summarizing: {topic}")
        summary = summarize_trend(topic, search_results)
        trend["summary"] = summary

    insert_trends_to_db(trends, table_name="google_trends_now")

    driver.quit()

if __name__ == "__main__":
    scrape_daily_trends()