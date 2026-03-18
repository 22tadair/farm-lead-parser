from duckduckgo_search import DDGS
import pandas as pd

def find_website(company_name):
    """
    Finds the company website using DDGS.
    """
    if not company_name or pd.isna(company_name) or company_name == "N/A":
        return ""

    query = f"{company_name} official website"

    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)
            for res in results:
                href = res.get('href', '')
                if any(x in href for x in ['facebook.com', 'linkedin.com', 'twitter.com', 'instagram.com']):
                    continue
                return href
    except Exception as e:
        print(f"Error searching for {company_name}: {e}")

    return ""
