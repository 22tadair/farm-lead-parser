import pandas as pd

def normalize_columns(df):
    """
    Normalizes column names to standard fields based on common aliases.
    """
    mapping = {
        'first_name': ['first name', 'firstname', 'given name'],
        'last_name': ['last name', 'lastname', 'surname'],
        'email': ['email', 'e-mail', 'e-mail 1 - value', 'email address'],
        'phone': ['phone', 'phone number', 'phone 1 - value', 'telephone', 'mobile', 'tel'],
        'organization': ['organization', 'company', 'org', 'business name', 'company name', 'organization name', 'unnamed: 0'],
        'street': ['street', 'address', 'address 1 - formatted', 'street address'],
        'city': ['city'],
        'state': ['state', 'region', 'province'],
        'postal_code': ['postal code', 'zip', 'zip code', 'postcode'],
        'country': ['country'],
        'designation': ['designation', 'title', 'job title', 'role', 'position']
    }

    new_cols = {}
    for col in df.columns:
        clean_col = str(col).lower().strip()
        found = False
        for standard_name, aliases in mapping.items():
            if clean_col == standard_name or clean_col in aliases:
                new_cols[col] = standard_name
                found = True
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

    required_fields = [
        'first_name', 'last_name', 'organization', 'email', 'phone',
        'state', 'country', 'city', 'postal_code', 'street', 'designation'
    ]

    for field in required_fields:
        if field not in df.columns:
            df[field] = ""

    return df
