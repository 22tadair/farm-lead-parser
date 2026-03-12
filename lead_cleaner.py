import pandas as pd

def normalize_columns(df):
    """
    Normalizes column names to standard fields.
    """
    mapping = {
        'organization': ['organization', 'company', 'org', 'business name', 'company name', 'unnamed: 0'],
        'designation': ['designation', 'title', 'job title', 'role', 'position']
    }

    new_cols = {}
    for col in df.columns:
        clean_col = str(col).lower().strip()
        for standard_name, aliases in mapping.items():
            if clean_col == standard_name or clean_col in aliases:
                new_cols[col] = standard_name
                break

    df = df.rename(columns=new_cols)

    # EMERGENCY FALLBACK: If no organization column was found,
    # assume the VERY FIRST column is the organization/messy cell.
    if 'organization' not in df.columns:
        df = df.rename(columns={df.columns[0]: 'organization'})

    # Deduplicate in case multiple columns mapped to 'organization'
    df = df.loc[:, ~df.columns.duplicated()]
    return df

def clean_leads(df):
    """
    Cleans and standardizes lead columns.
    """
    df = normalize_columns(df)

    # We only care about having 'organization' for the AI to work with
    if 'organization' not in df.columns:
        return pd.DataFrame() # Still empty? Skip.

    # Make sure other columns exist so the script doesn't crash
    required_fields = ['first_name', 'last_name', 'email', 'phone', 'state', 'designation', 'street', 'city', 'postal_code', 'country']
    for field in required_fields:
        if field not in df.columns:
            df[field] = ""

    return df
