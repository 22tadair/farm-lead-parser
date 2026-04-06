from duckduckgo_search import DDGS
import pandas as pd

def find_website(organization_company):
    """
    Finds the company website using DDGS.
    """
    if not organization_company or pd.isna(organization_company) or organization_company == "N/A":
        return ""

    query = f"{organization_company} official website"

    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)
            for res in results:
                href = res.get('href', '')
                if any(x in href for x in ['facebook.com', 'linkedin.com', 'twitter.com', 'instagram.com']):
                    continue
                return href
    except Exception as e:
        print(f"Error searching for {organization_company}: {e}")

    return ""
