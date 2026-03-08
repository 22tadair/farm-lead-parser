import google.generativeai as genai
import os

_model = None

def get_model():
    """
    Initializes and returns the Gemini model (singleton).
    """
    global _model
    if _model is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return None
        genai.configure(api_key=api_key)
        _model = genai.GenerativeModel('gemini-1.5-flash')
    return _model

def classify_company(company_name, scraped_text):
    """
    Classifies a company using the Gemini API.
    """
    model = get_model()
    if not model:
        print("GEMINI_API_KEY not found in environment variables.")
        return "Unknown (API key missing)"

    prompt = f"""
    Based on the following company name and scraped website text, classify the company into one of these categories:
    - Farm Equipment Dealer
    - Farm Equipment Manufacturer
    - Farm Equipment Supplier
    - Agriculture Service Provider
    - Other

    Company Name: {company_name}
    Scraped Text: {scraped_text}

    Return ONLY the category name from the list above.
    """

    try:
        response = model.generate_content(prompt)
        classification = response.text.strip()

        valid_categories = [
            "Farm Equipment Dealer",
            "Farm Equipment Manufacturer",
            "Farm Equipment Supplier",
            "Agriculture Service Provider",
            "Other"
        ]

        for category in valid_categories:
            if category.lower() in classification.lower():
                return category

        return "Other"
    except Exception as e:
        print(f"Error classifying {company_name}: {e}")
        return "Other"
