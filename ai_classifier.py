import os
from google import genai
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

def get_client():
    """
    Initializes and returns the Gemini client with a forced stable API version.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("CRITICAL: No API Key found in .env")
        return None
    # Force 'v1' to avoid 404 NOT_FOUND errors from beta endpoints
    return genai.Client(api_key=api_key, http_options={'api_version': 'v1'})

def parse_messy_lead(raw_blob):
    """
    Takes a massive string of text and breaks it into 12 structured categories using models/gemini-1.5-flash.
    """
    client = get_client()
    if not client:
        return ["N/A"] * 12

    prompt = f"""
    Act as a data parser. Split this lead into exactly 12 fields separated by |
    Stop looking at this as a single name. Treat it as a puzzle and extract the pieces.

    CRITICAL RULE: The 'Company' field MUST contain ONLY the name of the business.
    You MUST strip out any City, State, Zip, Address, or extra notes from the 'Company' field.

    If you see a semi-colon (;), the text BEFORE it is the Company Name.
    The text AFTER it is likely Location, Brand, or other notes.

    Fields: First, Last, Company, Phone, Email, State, Country, City, Zip, Address, Role, Notes
    Data: {raw_blob}
    """

    try:
        # Use full model path 'models/gemini-1.5-flash'
        response = client.models.generate_content(
            model='models/gemini-1.5-flash',
            contents=prompt
        )
        text = response.text.strip()
        # Handle markdown blocks if present
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"): text = text[4:].strip()
            elif text.startswith("|"): text = text.strip()

        # Robust parsing: remove empty strings from leading/trailing pipes
        parts = [p.strip() for p in text.split('|') if p.strip()]

        while len(parts) < 12:
            parts.append("N/A")

        return parts[:12]
    except Exception as e:
        print(f"AI Error in parse_messy_lead: {e}")
        return ["Error"] * 12

def classify_enrichment(company_name, scraped_text):
    """
    Secondary classification based on scraped text using models/gemini-1.5-flash.
    """
    client = get_client()
    if not client:
        return "0 | N/A"

    prompt = f"""
    Based on the following company name and scraped website text, provide:
    1. Confidence Score (0-100)
    2. Type of Crop (List crops if Grower, else 'N/A'. If Grower but no specific crops found, return 'General Agriculture')

    Company: {company_name}
    Text: {scraped_text}

    Format: Score | Crop Type
    """

    try:
        # Use full model path 'models/gemini-1.5-flash'
        response = client.models.generate_content(
            model='models/gemini-1.5-flash',
            contents=prompt
        )
        text = response.text.strip()
        if "Score |" in text:
            text = text.split("\n")[-1]
        return text
    except Exception as e:
        print(f"AI Error in classify_enrichment: {e}")
        return "0 | N/A"
