import google.generativeai as genai
import os

def classify_company(raw_text, scraped_text=""):
    """
    Splits messy lead info and classifies it using the latest Gemini model.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return f"{raw_text} | Unknown | Unknown | Unknown | 0 | N/A"

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    prompt = f"""
    Analyze this messy farm lead and any scraped website text.

    Lead Text: {raw_text}
    Scraped Text: {scraped_text}

    1. Extract/Split: Company Name, State, and Job Title.
    2. Classify: Dealer, Grower, or Other.
    3. Score: Confidence (0-100).
    4. Crop Type: If Grower, list crops (e.g. Corn, Soybeans). If not, return 'N/A'. If Grower but no crops found, return 'General Agriculture'.

    Return ONLY in this format:
    Company Name | State | Job Title | Category | Confidence Score | Crop Type
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error in classify_company: {e}")
        return f"{raw_text} | Unknown | Unknown | Other | 0 | N/A"
