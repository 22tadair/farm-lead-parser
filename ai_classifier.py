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
    Classifies a company using the Gemini API and returns (Category, Score, Crop Type).
    """
    model = get_model()
    if not model:
        print("GEMINI_API_KEY not found in environment variables.")
        return "Unknown (API key missing)", 0, "N/A"

    prompt = f"""
    Based on the following company name and scraped website text, analyze the company.

    1. Classify the company into one of these categories:
       - Farm Equipment Dealer
       - Farm Equipment Manufacturer
       - Farm Equipment Supplier
       - Agriculture Service Provider
       - Other

    2. Provide a confidence score (0-100) based on how much evidence (keywords) you found in the scraped text for this classification.

    3. Identify Crop Types for Growers. If they grow crops, list them (e.g., Corn, Soybeans, Almonds, Citrus, Wheat, Cotton).
       - If the category is 'Farm Equipment Dealer', 'Farm Equipment Manufacturer', or 'Farm Equipment Supplier', return 'N/A'.
       - If no specific crops are found for a Grower, return 'General Agriculture'.

    Company Name: {company_name}
    Scraped Text: {scraped_text}

    Return the result in EXACTLY this format: Category | Score | Crop Type
    Example: Farm Equipment Dealer | 95 | N/A
    Example: Agriculture Service Provider | 80 | Corn, Soybeans
    Example: Other | 60 | General Agriculture
    """

    try:
        response = model.generate_content(prompt)
        result = response.text.strip()

        parts = [p.strip() for p in result.split('|')]

        category = "Other"
        score = 0
        crop_type = "N/A"

        if len(parts) >= 1:
            category = parts[0]
        if len(parts) >= 2:
            try:
                score = int(parts[1])
            except ValueError:
                score = 0
        if len(parts) >= 3:
            crop_type = parts[2]

        return category, score, crop_type

    except Exception as e:
        print(f"Error classifying {company_name}: {e}")
        return "Other", 0, "N/A"
