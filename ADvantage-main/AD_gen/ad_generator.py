#!/usr/bin/env python
# AD_gen/ad_generator.py

import sys
import os
import re
import io
import psycopg2
import openai
from dotenv import load_dotenv
import logging
from typing import List, Tuple, Optional

# Configure UTF-8 safe output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class AdGenerator:
    def __init__(self):
        """Initialize with configurable parameters"""
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.db_config = {
            "dbname": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT"),
        }
        self.model = os.getenv("AD_MODEL", "gpt-4o")
        self.max_tokens = int(os.getenv("AD_MAX_TOKENS", 500))
        self.temperature = float(os.getenv("AD_TEMP", 0.8))
        
        if not openai.api_key:
            logger.error("OPENAI_API_KEY not found in environment variables")
            raise ValueError("API key not configured")

    def fetch_trends(self, limit: int = 5) -> List[Tuple[str, str]]:
        """Fetch trending topics from database"""
        try:
            with psycopg2.connect(**self.db_config) as conn, conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT topic, summary
                    FROM google_trends_7d
                    ORDER BY scraped_date DESC, id ASC
                    LIMIT %s
                    """,
                    (limit,)
                )
                trends = cur.fetchall()
                logger.info(f"Fetched {len(trends)} trends from database")
                return trends
        except psycopg2.Error as e:
            logger.error(f"Database error: {e}")
            return []

    def _generate_hashtags(self, text: str, max_tags: int = 3) -> str:
        """Generate simple hashtags from text"""
        words = []
        for w in re.findall(r"\b\w{4,}\b", text.lower()):
            if w not in words:
                words.append(w)
            if len(words) >= max_tags:
                break
        return " ".join(f"#{w.capitalize()}" for w in words)

    def generate(
        self,
        product: str,
        description: str,
        trends: List[Tuple[str, str]],
        tone: str = "casual",
        include_tags: bool = False
    ) -> List[str]:
        """Generate ads connecting product to current trends"""
        tone_map = {
            "casual": "a regular tone",
            "formal": "a professional, formal tone",
            "gen-z": "an enthusiastic Gen-Z tone (slang welcome!)",
        }
        tone_phrase = tone_map.get(tone.lower(), tone_map["casual"])

        prompt = (
            f"You are a world-class salesman,you are extremely witty.\n"
            f"Write each ad in **{tone_phrase}**.\n"
            f"The client sells **{product}**.\n"
            f"Description: {description}\n\n"
            "For each of the 5 trends below, deliver ONE punchy social-media style ad (≤25 words):\n\n"
            "Make sure the ad starts with 'Ad:' and does not include the trend name itself in the ad.\n"
            "The ad should be formatted as follows: \n"
            "- Always start with 'Ad:' followed by the ad copy.\n"
            "- Only include relevant information from the trend (do not copy the trend description verbatim).\n"
            "- Do not mix the trend and ad content together, they should be distinct.\n\n"
            "For example:\n"
            "Ad: 'Win big with our product and enjoy amazing results!' #Ad #Product #Amazing\n\n"
            "Here are the trends:\n"
            "Generate a min and max of 5 ads, one for each trend"
        )
        for i, (topic, summary) in enumerate(trends, 1):
            prompt += f"{i}. Trend: {topic}\n   Summary: {summary}\n   Ad:\n"
        prompt += "\nGenerate all ads now."

        try:
            # Try ChatCompletion first
            resp = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Produce short, trend-based ad copy."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            raw = resp.choices[0].message.content
        except AttributeError:
            # Fallback to Completion
            resp = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            raw = resp.choices[0].text

        ads = []
        for line in raw.splitlines():
            txt = line.strip()
            if not txt:
                continue
            txt = re.sub(r"^\s*\d+[\.)]\s*", "", txt)
            if include_tags:
                txt += "  " + self._generate_hashtags(txt)
            ads.append(txt)
        return ads


def main():
    """Command-line interface"""
    if len(sys.argv) < 5:
        # print("Usage: python ad_generator.py <product> <description> <tone> <yes|no>")
        sys.exit(1)

    generator = AdGenerator()
    product, desc, tone_arg, flag = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    include_tags = flag.lower() in {"yes", "true", "1", "y"}

    # print(f"[ad_generator] args → product={product!r}, desc={desc!r}, tone={tone_arg!r}, tags={include_tags}")
    trends = generator.fetch_trends()
    # print(f"[ad_generator] fetched trends = {trends!r}")

    try:
        for ad in generator.generate(product, desc, trends, tone_arg, include_tags):
            print(ad)
        sys.exit(0)
    except Exception:
        logger.exception("Failed to generate ads")
        sys.exit(1)


if __name__ == "__main__":
    main()