import os
import requests
from dotenv import load_dotenv
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or "YOUR_GOOGLE_API_KEY"
GOOGLE_CX = os.getenv("GOOGLE_CX") or "YOUR_GOOGLE_CX"

def google_search(query, max_results=5):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX,
        "num": max_results
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return f"Google Search Error: {response.status_code}"

    data = response.json()
    results = []
    for item in data.get("items", []):
        title = item.get("title")
        snippet = item.get("snippet")
        link = item.get("link")
        results.append(f"Title: {title}\nLink: {link}\nSnippet: {snippet}")
    
    return "\n\n".join(results)

