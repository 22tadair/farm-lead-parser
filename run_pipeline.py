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

    # Enrich data
    websites = []
    scraped_texts = []
    classifications = []
    linkedin_pages = []

    for index, row in df.iterrows():
        company = row['organization']
        print(f"  Enriching: {company}")

        # 3. Find website
        website = find_website(company)
        websites.append(website)

        # 4. Scrape website
        scraped_text = ""
        if website:
            scraped_text = scrape_website(website)
        scraped_texts.append(scraped_text)

        # 5. AI Classification
        classification = classify_company(company, scraped_text)
        classifications.append(classification)

        # 6. Find LinkedIn
        linkedin = find_linkedin(company)
        linkedin_pages.append(linkedin)

    df['website'] = websites
    df['classification'] = classifications
    df['linkedin'] = linkedin_pages
    # We don't necessarily want to export the raw scraped text, but we could
    # df['scraped_text'] = scraped_texts

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
