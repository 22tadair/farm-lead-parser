import os
import pandas as pd
import time
from file_loader import load_file
from lead_cleaner import clean_leads
from website_finder import find_website
from web_scraper import scrape_website
from ai_classifier import parse_leads_batch, classify_enrichment
from linkedin_finder import find_linkedin
from exporter import export_to_excel

INPUT_FOLDER = 'input'
OUTPUT_FOLDER = 'output'
BATCH_SIZE = 5

def process_file(filepath):
    print(f"Processing {filepath}...")

    # 1. Load file
    df = load_file(filepath)

    # 2. Clean leads (Identify columns)
    df = clean_leads(df)

    if df.empty:
        print(f"  File {filepath} resulted in empty dataframe after cleaning.")
        return

    # Filter out empty leads and collect non-empty blobs
    blobs = []
    for _, row in df.iterrows():
        blob = " ".join([str(v) for v in row.values if pd.notna(v)]).strip()
        blobs.append(blob)

    all_processed_data = []

    # Process in batches of 5
    for i in range(0, len(blobs), BATCH_SIZE):
        batch = [b for b in blobs[i:i + BATCH_SIZE] if b]
        if not batch:
            continue

        print(f"  Processing batch {i//BATCH_SIZE + 1} ({len(batch)} leads)...")

        # 3. AI Decomposition (Batch "Puzzle" surgery)
        parsed_batch = parse_leads_batch(batch)

        # Throttling: brief pause between batches
        time.sleep(2)

        for parsed_row in parsed_batch:
            # FIX: Safety check for NoneType and structure
            if parsed_row and len(parsed_row) > 2 and parsed_row[2] is not None:
                # Clean company name: text before semi-colon
                company_name = str(parsed_row[2]).split(';')[0].strip()
                parsed_row[2] = company_name
            else:
                company_name = "Unknown"
                print(f"Warning: AI returned invalid or empty data for a lead in this batch.")
                # Ensure parsed_row is a list if it was None
                if parsed_row is None:
                    parsed_row = ["N/A"] * 12

            # 4. Find website using the cleaned company name
            website = ""
            if company_name != "Unknown":
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
                # Throttling: brief pause between enrichment calls
                time.sleep(1)

            # 6. Find LinkedIn
            linkedin = ""
            if company_name != "Unknown":
                linkedin = find_linkedin(company_name)

            # Assemble full data row
            full_row = parsed_row + [website, linkedin, confidence_score, crop_type]
            all_processed_data.append(full_row)

    output_columns = [
        'first name', 'last name', 'Organization/Company', 'phone number', 'email',
        'state/region', 'country', 'city', 'zip code', 'address',
        'grower or supplier', 'Notes', 'website', 'linkedin',
        'confidence score', 'type of crop'
    ]

    final_df = pd.DataFrame(all_processed_data, columns=output_columns)

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
