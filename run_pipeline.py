import os
import pandas as pd
from file_loader import load_file
from lead_cleaner import clean_leads
from website_finder import find_website
from web_scraper import scrape_website
from ai_classifier import parse_messy_lead, classify_enrichment
from linkedin_finder import find_linkedin
from exporter import export_to_excel

INPUT_FOLDER = 'input'
OUTPUT_FOLDER = 'output'

def process_file(filepath):
    print(f"Processing {filepath}...")

    # 1. Load file
    df = load_file(filepath)

    # 2. Clean leads (Identify organization/messy cell)
    df = clean_leads(df)

    if df.empty:
        print(f"  File {filepath} resulted in empty dataframe after cleaning.")
        return

    all_parsed_data = []

    for index, row in df.iterrows():
        messy_text = str(row['organization'])
        print(f"  Surgery in progress on: {messy_text[:40]}...")

        # 3. AI Decomposition (The "Puzzle" surgery)
        # parsed_row: [First, Last, Company, Phone, Email, State, Country, City, Zip, Address, Category, Notes]
        parsed_row = parse_messy_lead(messy_text)

        company_name = parsed_row[2]

        # 4. Find website
        website = find_website(company_name)

        # 5. Scrape and Enrichment
        confidence_score = "0"
        crop_type = "N/A"
        if website:
            scraped_text = scrape_website(website)
            enrich_result = classify_enrichment(company_name, scraped_text)
            enrich_parts = [p.strip() for p in enrich_result.split('|')]
            if len(enrich_parts) >= 2:
                confidence_score = enrich_parts[0]
                crop_type = enrich_parts[1]

        # 6. Find LinkedIn
        linkedin = find_linkedin(company_name)

        # Assemble full data row
        full_row = parsed_row + [website, linkedin, confidence_score, crop_type]
        all_parsed_data.append(full_row)

    output_columns = [
        'first name', 'last name', 'Organization/Company', 'phone number', 'email',
        'state/region', 'country', 'city', 'zip code', 'address',
        'grower or supplier', 'Notes', 'website', 'linkedin',
        'confidence score', 'type of crop'
    ]

    final_df = pd.DataFrame(all_parsed_data, columns=output_columns)

    # 7. Export
    filename = os.path.basename(filepath)
    output_filename = os.path.splitext(filename)[0] + "_Clean_Leads.xlsx"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    export_to_excel(final_df, output_path)

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
