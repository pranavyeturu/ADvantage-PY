#!/usr/bin/env python
# AD_gen/trend_summarizer_agent.py

import os
import openai
from dotenv import load_dotenv
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class TrendSummarizer:
    def __init__(self):
        """Initialize with configurable parameters"""
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("SUMMARY_MODEL", "gpt-3.5-turbo")
        self.max_tokens = int(os.getenv("SUMMARY_MAX_TOKENS", 300))
        self.temperature = float(os.getenv("SUMMARY_TEMP", 0.7))
        
        if not openai.api_key:
            logger.error("OPENAI_API_KEY not found in environment variables")
            raise ValueError("API key not configured")

    def summarize(self, trend_name: str, search_results: str) -> str:
        """
        Summarize a trending topic based on search results
        
        Args:
            trend_name: The trending topic name
            search_results: Raw search results to summarize
            
        Returns:
            Summary text or error message
        """
        if not search_results.strip():
            logger.warning(f"Empty search results for trend: {trend_name}")
            return "No summary available (empty search results)"
            
        try:
            logger.info(f"Summarizing trend: {trend_name}")
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert analyst summarizing Google Trends data. "
                            "Provide concise, informative summaries highlighting:\n"
                            "1. What the trend is about\n"
                            "2. Why it's trending\n"
                            "3. Key context or details\n"
                            "Keep it under 3 sentences."
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Trend Name: {trend_name}\n\n"
                            f"Search Results:\n{search_results}\n\n"
                            "Please provide a concise summary:"
                        )
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            summary = response['choices'][0]['message']['content'].strip()
            logger.debug(f"Generated summary for {trend_name}: {summary[:50]}...")
            return summary
            
        except openai.error.APIError as e:
            logger.error(f"API error for {trend_name}: {str(e)}")
            return "Summary unavailable (API error)"
        except openai.error.RateLimitError as e:
            logger.error(f"Rate limit exceeded for {trend_name}")
            return "Summary unavailable (rate limit exceeded)"
        except Exception as e:
            logger.error(f"Unexpected error summarizing {trend_name}: {str(e)}")
            return f"Summary unavailable ({str(e)})"


# Singleton instance
summarizer = TrendSummarizer()

def summarize_trend(trend_name: str, search_results: str) -> str:
    """Public interface function"""
    return summarizer.summarize(trend_name, search_results)

if __name__ == "__main__":
    # Test functionality
    test_trend = "PBKS vs LSG IPL Match"
    test_content = """• Punjab Kings defeated Lucknow Super Giants by 5 wickets
                    • Match played at Ekana Stadium
                    • Shikhar Dhawan scored 70 runs"""
    
    print("Testing Trend Summarizer...")
    print(f"Trend: {test_trend}")
    print("Generated Summary:")
    print(summarize_trend(test_trend, test_content))