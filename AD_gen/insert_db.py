import psycopg2
from datetime import datetime, timedelta, date

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def clean_volume(vol_str):
    try:
        vol_str = vol_str.replace("+", "").strip().upper()
        if "M" in vol_str:
            return int(float(vol_str.replace("M", "")) * 1_000_000)
        elif "K" in vol_str:
            return int(float(vol_str.replace("K", "")) * 1_000)
        else:
            return int(vol_str)
    except:
        return 0

def parse_start_time(start_str):
    now = datetime.now()
    start_str = start_str.strip().lower()

    try:
        if "hour" in start_str:
            num = int(start_str.split()[0])
            return now - timedelta(hours=num)
        elif "minute" in start_str:
            num = int(start_str.split()[0])
            return now - timedelta(minutes=num)
        elif "yesterday" in start_str:
            return now - timedelta(days=1)
        elif "day" in start_str:
            num = int(start_str.split()[0])
            return now - timedelta(days=num)
        else:
            # Try parsing absolute format
            return datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
    except:
        return now  # fallback

def insert_trends_to_db(trends, table_name="google_trends_now"):
    conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT", "5432")  # Default to 5432 if not set
)
    cursor = conn.cursor()

    for trend in trends:
        topic = trend["topic"]
        volume = clean_volume(trend.get("volume", "0"))
        start_time = parse_start_time(trend.get("start_time", "now"))
        summary = trend.get("summary", "N/A")

        cursor.execute(f"""
            INSERT INTO {table_name} (topic, volume, start_time, scraped_date, summary)
            VALUES (%s, %s, %s, %s, %s)
        """, (topic, volume, start_time, date.today(), summary))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Inserted {len(trends)} trends into table: {table_name}")
