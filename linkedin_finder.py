from duckduckgo_search import DDGS
import pandas as pd

def find_linkedin(organization_company):
    """
    Finds the company LinkedIn page using DDGS.
    """
    if not organization_company or pd.isna(organization_company) or organization_company == "N/A":
        return ""

    query = f"{organization_company} LinkedIn company page"

    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)
            for res in results:
                href = res.get('href', '')
                if 'linkedin.com/company/' in href:
                    return href
    except Exception as e:
        print(f"Error searching LinkedIn for {organization_company}: {e}")

    return ""
