import os
import psycopg2
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_top_trends_from_db(limit=5):
    conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT", "5432")  # Default to 5432 if not set
)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT topic, summary FROM google_trends_now
        ORDER BY scraped_date DESC, id ASC
        LIMIT %s;
    """, (limit,))
    trends = cursor.fetchall()
    cursor.close()
    conn.close()
    return trends

def generate_ads(product, description, trends):
    prompt = (
        f"You are a trend-savvy AI ad salesman. Create short, relevant ad copy for a product named **{product}**.\n"
        f"Product Description: {description}\n\n"
        f"Write one creative, engaging ad for each of the following trending topics.\n\n"
    )

    for i, (topic, summary) in enumerate(trends, 1):
        prompt += f"{i}. Trend: {topic}\nSummary: {summary}\nAd:"

    prompt += "\n\nNow write all 5 ads."

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You write creative ad copy that connects products to current trending topics."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=600,
        temperature=0.85
    )

    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    product_name = input("Enter product name: ")
    product_desc = input("Enter product description: ")

    trends = get_top_trends_from_db()
    ads = generate_ads(product_name, product_desc, trends)

    print("\n📢 Generated Ads:\n")
    print(ads)
