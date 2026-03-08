from duckduckgo_search import DDGS
import pandas as pd

def find_website(company_name):
    """
    Finds the company website using DuckDuckGo search library.
    """
    if not company_name or pd.isna(company_name):
        return ""

    query = f"{company_name} official website"

    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)
            for res in results:
                href = res.get('href', '')
                # Basic heuristic: avoid social media if possible for the official website
                if any(x in href for x in ['facebook.com', 'linkedin.com', 'twitter.com', 'instagram.com']):
                    continue
                return href
    except Exception as e:
        print(f"Error searching for {company_name}: {e}")

    return ""
