import pandas as pd
from ai_classifier import analyze_leads_structure, parse_messy_row

def smart_clean_leads(df):
    """
    Smarter cleaning that uses AI to handle merged columns and obscure headers.
    """
    # 1. Analyze structure using first few rows
    sample = df.head(3).to_json(orient='records')
    mapping = analyze_leads_structure(sample)

    required_fields = [
        'first_name', 'last_name', 'organization', 'email', 'phone',
        'street', 'city', 'state', 'postal_code', 'country', 'designation'
    ]

    cleaned_rows = []

    if mapping:
        print(f"  Detected mapping: {mapping}")
        # Process each row
        for _, row in df.iterrows():
            new_row = {field: "" for field in required_fields}

            # First, handle non-merged columns
            for col, standard in mapping.items():
                if standard in required_fields and col in df.columns:
                    new_row[standard] = row[col]

            # Then, handle merged columns or missing data using AI parsing if needed
            merged_content = []
            for col, standard in mapping.items():
                if standard == 'merged' and col in df.columns:
                    merged_content.append(str(row[col]))

            # If we have merged content, or if key fields like organization are still empty,
            # try to parse the entire row as a string.
            if merged_content or not new_row['organization']:
                full_row_text = " ".join([str(v) for v in row.values if pd.notna(v)])
                parsed = parse_messy_row(full_row_text)
                for k, v in parsed.items():
                    if k in required_fields and not new_row[k]:
                        new_row[k] = v

            cleaned_rows.append(new_row)
    else:
        # Fallback to basic cleaning if AI mapping fails
        print("  AI mapping failed, falling back to basic normalization.")
        return fallback_clean_leads(df)

    return pd.DataFrame(cleaned_rows)

def fallback_clean_leads(df):
    """
    Basic normalization logic as a fallback.
    """
    mapping = {
        'first_name': ['first name', 'fname', 'first', 'given name'],
        'last_name': ['last name', 'lname', 'last', 'surname', 'family name'],
        'organization': ['organization', 'company', 'org', 'business name', 'company name'],
        'email': ['email', 'e-mail', 'email address'],
        'phone': ['phone', 'telephone', 'mobile', 'tel', 'phone number'],
        'street': ['street', 'address', 'address 1', 'street address'],
        'city': ['city'],
        'state': ['state', 'province', 'region'],
        'postal_code': ['postal code', 'zip code', 'zip', 'postcode'],
        'country': ['country'],
        'designation': ['designation', 'title', 'job title', 'role', 'position']
    }

    new_cols = {}
    for col in df.columns:
        clean_col = str(col).lower().strip().replace('_', ' ')
        for standard_name, aliases in mapping.items():
            if clean_col == standard_name.replace('_', ' ') or clean_col in aliases:
                new_cols[col] = standard_name
                break

    df = df.rename(columns=new_cols)
    required_fields = [
        'first_name', 'last_name', 'organization', 'email', 'phone',
        'street', 'city', 'state', 'postal_code', 'country', 'designation'
    ]
    for field in required_fields:
        if field not in df.columns:
            df[field] = ""
    return df[required_fields]
