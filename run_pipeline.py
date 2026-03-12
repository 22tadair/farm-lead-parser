import os
import pandas as pd
from file_loader import load_file
from lead_cleaner import clean_leads
from website_finder import find_website
from web_scraper import scrape_website
from ai_classifier import classify_company
from linkedin_finder import find_linkedin
from exporter import export_to_excel

INPUT_FOLDER = 'input'
OUTPUT_FOLDER = 'output'

def process_file(filepath):
    print(f"Processing {filepath}...")

    # 1. Load file
    df = load_file(filepath)

    # 2. Clean leads
    df = clean_leads(df)

    if df.empty:
        print(f"  File {filepath} resulted in empty dataframe after cleaning.")
        return

    # Enrich data
    extracted_companies = []
    extracted_states = []
    extracted_titles = []
    classifications = []
    confidence_scores = []
    crop_types = []
    websites = []
    linkedin_pages = []

    for index, row in df.iterrows():
        # Using the potentially messy organization cell
        raw_text = str(row['organization'])
        print(f"  Analyzing: {raw_text}")

        # 3. AI Decomposition and Initial Classification
        # We call it twice or handle it better?
        # Better to do it once if possible.
        # But we need the company name for website search.

        ai_result = classify_company(raw_text)
        parts = [p.strip() for p in ai_result.split('|')]

        # Ensure we have 6 parts
        while len(parts) < 6:
            parts.append("Unknown")

        company = parts[0]
        state = parts[1]
        title = parts[2]
        category = parts[3]
        score = parts[4]
        crop = parts[5]

        # 4. Find website using extracted company name
        website = find_website(company)

        # 5. Scrape and RE-CLASSIFY with website info for better accuracy
        if website:
            scraped_text = scrape_website(website)
            # Second pass with scraped data
            ai_result = classify_company(raw_text, scraped_text)
            parts = [p.strip() for p in ai_result.split('|')]
            while len(parts) < 6:
                parts.append("Unknown")
            company = parts[0]
            state = parts[1]
            title = parts[2]
            category = parts[3]
            score = parts[4]
            crop = parts[5]

        # 6. Find LinkedIn
        linkedin = find_linkedin(company)

        extracted_companies.append(company)
        extracted_states.append(state)
        extracted_titles.append(title)
        classifications.append(category)
        confidence_scores.append(score)
        crop_types.append(crop)
        websites.append(website)
        linkedin_pages.append(linkedin)

    df['organization'] = extracted_companies
    df['state'] = extracted_states
    df['designation'] = extracted_titles
    df['classification'] = classifications
    df['confidence_score'] = confidence_scores
    df['crop_type'] = crop_types
    df['website'] = websites
    df['linkedin'] = linkedin_pages

    # 7. Export
    filename = os.path.basename(filepath)
    output_filename = os.path.splitext(filename)[0] + "_enriched.xlsx"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    export_to_excel(df, output_path)

def main():
    if not os.path.exists(INPUT_FOLDER):
        print(f"Input folder '{INPUT_FOLDER}' not found.")
        return

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(('.csv', '.xlsx', '.xls'))]

    if not files:
        print("No lead files found in the input folder.")
        return

    for file in files:
        process_file(os.path.join(INPUT_FOLDER, file))

if __name__ == "__main__":
    main()
