import google.generativeai as genai
import os
import json

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

def parse_messy_row(row_text):
    """
    Uses Gemini to extract structured fields from a messy string or row.
    """
    model = get_model()
    if not model:
        return {}

    prompt = f"""
    Extract lead information from the following text.
    The text might contain a name, organization, and location all in one string.

    Text: {row_text}

    Return a JSON object with the following keys:
    first_name, last_name, organization, street, city, state, postal_code, country, designation, phone, email

    If a field is missing, use an empty string.
    Return ONLY the JSON.
    """

    try:
        response = model.generate_content(prompt)
        json_str = response.text.strip()
        # Clean up markdown code blocks if present
        if json_str.startswith('```json'):
            json_str = json_str[7:-3].strip()
        elif json_str.startswith('```'):
            json_str = json_str[3:-3].strip()
        return json.loads(json_str)
    except Exception as e:
        print(f"Error parsing messy row: {e}")
        return {}

def analyze_leads_structure(sample_rows_json):
    """
    Analyzes sample rows to determine how to map columns to standard fields.
    """
    model = get_model()
    if not model:
        return None

    prompt = f"""
    Given the following sample rows from a spreadsheet (as JSON),
    determine which column names map to our standard fields:
    first_name, last_name, organization, email, phone, street, city, state, postal_code, country, designation

    Sample Data:
    {sample_rows_json}

    Return a JSON object where keys are the original column names and values are the standard field names.
    If a column contains multiple pieces of information (like Name and Org), map it to 'merged'.
    Return ONLY the JSON.
    """

    try:
        response = model.generate_content(prompt)
        json_str = response.text.strip()
        if json_str.startswith('```json'):
            json_str = json_str[7:-3].strip()
        elif json_str.startswith('```'):
            json_str = json_str[3:-3].strip()
        return json.loads(json_str)
    except Exception as e:
        print(f"Error analyzing structure: {e}")
        return None
