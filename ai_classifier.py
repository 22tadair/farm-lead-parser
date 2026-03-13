import google.generativeai as genai
import os

def classify_company(raw_text, scraped_text=""):
    """
    Decomposes messy lead info and classifies it into 13 specific fields using Gemini.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return f"{raw_text} | | | | | | | | | | Unknown | 0 | N/A"

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    prompt = f"""
    Analyze this messy farm lead and any scraped website text.
    Your goal is to extract and separate ALL available information into the specified fields.

    Lead Text: {raw_text}
    Scraped Text: {scraped_text}

    Fields to extract:
    1. Organization/Company
    2. First Name
    3. Last Name
    4. Phone Number
    5. Email
    6. State/Region
    7. Country
    8. City
    9. Zip Code
    10. Address (Street address)
    11. Category: Grower, Supplier, or Other
    12. Confidence Score: (0-100)
    13. Type of Crop: (List crops if Grower, otherwise 'N/A'. Use 'General Agriculture' if Grower but crops not specified).

    Return ONLY in this format, separated by pipes:
    Organization | First Name | Last Name | Phone Number | Email | State/Region | Country | City | Zip Code | Address | Category | Confidence Score | Type of Crop
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error in classify_company: {e}")
        # Return fallback with empty fields
        return f"{raw_text} | | | | | | | | | | Other | 0 | N/A"
