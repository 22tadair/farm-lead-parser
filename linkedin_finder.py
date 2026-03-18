from duckduckgo_search import DDGS
import pandas as pd

def find_linkedin(company_name):
    """
    Finds the company LinkedIn page using DDGS.
    """
    if not company_name or pd.isna(company_name) or company_name == "N/A":
        return ""

    query = f"{company_name} LinkedIn company page"

    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)
            for res in results:
                href = res.get('href', '')
                if 'linkedin.com/company/' in href:
                    return href
    except Exception as e:
        print(f"Error searching LinkedIn for {company_name}: {e}")

    return ""
