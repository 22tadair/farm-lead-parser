import google.generativeai as genai
import os

def parse_messy_lead(raw_blob):
    """
    Takes a massive string of text and breaks it into 12 structured categories.
    Handles semi-colons specifically by treating text before it as the company name.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return ["N/A"] * 12

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    prompt = f"""
    You are a data entry expert. Parse the following messy lead text into structured fields.

    SPECIAL RULE: If you see a semi-colon (;), the text BEFORE it is likely the Company Name.
    The text AFTER it is likely Location, Brand (e.g. Case IH), or other notes.

    TEXT: "{raw_blob}"

    EXTRACT THESE FIELDS:
    1. First Name
    2. Last Name
    3. Company Name (Keep it clean: e.g. 'Hood Equipment Company' instead of 'Hood Equipment Company; Mississippi')
    4. Phone Number
    5. Email
    6. State/Region
    7. Country
    8. City
    9. Zip Code
    10. Address (Street address)
    11. Category (Grower, Supplier, or Manufacturer)
    12. Notes (Any extra info, including text found after a semi-colon if it doesn't fit elsewhere)

    RETURN ONLY ONE LINE in this exact format, separated by pipes (|):
    First | Last | Company | Phone | Email | State | Country | City | Zip | Address | Category | Notes

    If a field is missing, write 'N/A'.
    """

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"): text = text[4:].strip()
            elif text.startswith("|"): text = text.strip()

        data = [item.strip() for item in text.split('|')]
        while len(data) < 12:
            data.append("N/A")
        return data[:12]
    except Exception as e:
        print(f"AI Error: {e}")
        return ["Error"] * 12

def classify_enrichment(company_name, scraped_text):
    """
    Secondary classification based on scraped text.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key: return "0 | N/A"

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    prompt = f"""
    Based on the following company name and scraped website text, provide:
    1. Confidence Score (0-100)
    2. Type of Crop (List crops if Grower, else 'N/A')

    Company: {company_name}
    Text: {scraped_text}

    Format: Score | Crop Type
    """

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if "Score |" in text: text = text.split("\n")[-1]
        return text
    except:
        return "0 | N/A"
