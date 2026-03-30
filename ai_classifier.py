import os
import time
import json
from google import genai
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

def get_client():
    """
    Initializes and returns the Gemini client using the latest SDK.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("CRITICAL: No API Key found in .env")
        return None
    return genai.Client(api_key=api_key)

def parse_leads_batch(leads_blob_list):
    """
    Takes a list of messy lead strings and parses them as a batch using gemini-3-flash-preview.
    Returns a list of 12-field lists.
    """
    client = get_client()
    if not client:
        return [["N/A"] * 12] * len(leads_blob_list)

    # Format the batch for the prompt
    leads_text = "\n".join([f"LEAD {i+1}: {lead}" for i, lead in enumerate(leads_blob_list)])

    prompt = f"""
    Act as a data parser. You will be given a batch of {len(leads_blob_list)} messy farm leads.
    Parse each lead into exactly 12 fields.

    CRITICAL RULE: The 'Company' field MUST contain ONLY the name of the business.
    You MUST strip out any City, State, Zip, Address, or extra notes from the 'Company' field.

    If you see a semi-colon (;), the text BEFORE it is the Company Name.
    The text AFTER it is likely Location, Brand, or other notes.

    Fields for each lead: First Name, Last Name, Company Name, Phone, Email, State, Country, City, Zip, Address, Role, Notes.

    DATA BATCH:
    {leads_text}

    RETURN the result as a JSON list of objects, each with these keys:
    "first", "last", "company", "phone", "email", "state", "country", "city", "zip", "address", "role", "notes"
    """

    for i in range(3): # Max 3 retries
        try:
            response = client.models.generate_content(
                model='gemini-3-flash-preview',
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )

            # Use parsed JSON response
            results = json.loads(response.text)

            # Map JSON objects back to lists
            parsed_batch = []
            for item in results:
                row = [
                    item.get("first", "N/A"),
                    item.get("last", "N/A"),
                    item.get("company", "N/A"),
                    item.get("phone", "N/A"),
                    item.get("email", "N/A"),
                    item.get("state", "N/A"),
                    item.get("country", "N/A"),
                    item.get("city", "N/A"),
                    item.get("zip", "N/A"),
                    item.get("address", "N/A"),
                    item.get("role", "N/A"),
                    item.get("notes", "N/A")
                ]
                parsed_batch.append(row)

            return parsed_batch

        except Exception as e:
            if "429" in str(e) or "503" in str(e):
                wait_time = (i + 1) * 20
                print(f"Rate limit hit in batch parsing. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"AI Error in parse_leads_batch: {e}")
                break

    return [["Error"] * 12] * len(leads_blob_list)

def classify_enrichment(company_name, scraped_text):
    """
    Secondary classification based on scraped text with retry mechanism.
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

    Format ONLY: Score | Crop Type
    """

    for i in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-3-flash-preview',
                contents=prompt
            )
            text = response.text.strip()
            if "Score |" in text:
                text = text.split("\n")[-1]
            return text
        except Exception as e:
            if "429" in str(e) or "503" in str(e):
                wait_time = (i + 1) * 10
                print(f"Rate limit hit in enrichment. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"AI Error in classify_enrichment: {e}")
                break

    return "0 | N/A"
