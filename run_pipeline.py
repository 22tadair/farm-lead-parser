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

    # 2. Clean leads (Basic normalization to identify the organization/messy cell)
    df = clean_leads(df)

    if df.empty:
        print(f"  File {filepath} resulted in empty dataframe after cleaning.")
        return

    # Results lists for all 13 categories
    orgs, first_names, last_names, phones, emails = [], [], [], [], []
    states, countries, cities, zips, addresses = [], [], [], [], []
    categories, scores, crops = [], [], []
    websites, linkedin_pages = [], []

    for index, row in df.iterrows():
        raw_text = str(row['organization'])
        # Also include any existing info from other columns to help the AI
        other_info = " ".join([str(row[c]) for c in df.columns if c != 'organization' and pd.notna(row[c])])
        full_raw_text = f"{raw_text} {other_info}".strip()

        print(f"  Analyzing: {full_raw_text}")

        # 3. AI Decomposition (First pass)
        ai_result = classify_company(full_raw_text)
        parts = [p.strip() for p in ai_result.split('|')]
        while len(parts) < 13:
            parts.append("")

        company = parts[0]

        # 4. Find website
        website = find_website(company)

        # 5. Scrape and RE-CLASSIFY (Second pass)
        if website:
            scraped_text = scrape_website(website)
            ai_result = classify_company(full_raw_text, scraped_text)
            parts = [p.strip() for p in ai_result.split('|')]
            while len(parts) < 13:
                parts.append("")

        # 6. Find LinkedIn
        linkedin = find_linkedin(parts[0])

        # Store all parts
        orgs.append(parts[0])
        first_names.append(parts[1])
        last_names.append(parts[2])
        phones.append(parts[3])
        emails.append(parts[4])
        states.append(parts[5])
        countries.append(parts[6])
        cities.append(parts[7])
        zips.append(parts[8])
        addresses.append(parts[9])
        categories.append(parts[10])
        scores.append(parts[11])
        crops.append(parts[12])
        websites.append(website)
        linkedin_pages.append(linkedin)

    # Reconstruct final dataframe with requested columns
    enriched_df = pd.DataFrame({
        'Organization/Company': orgs,
        'first name': first_names,
        'last name': last_names,
        'phone number': phones,
        'email': emails,
        'state/region': states,
        'country': countries,
        'city': cities,
        'zip code': zips,
        'address': addresses,
        'grower or supplier': categories,
        'confidence score': scores,
        'type of crop': crops,
        'website': websites,
        'linkedin': linkedin_pages
    })

    # 7. Export
    filename = os.path.basename(filepath)
    output_filename = os.path.splitext(filename)[0] + "_enriched.xlsx"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    export_to_excel(enriched_df, output_path)

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
