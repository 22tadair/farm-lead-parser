import pandas as pd

def normalize_columns(df):
    """
    Normalizes column names to standard fields.
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
        found = False
        for standard_name, aliases in mapping.items():
            if clean_col == standard_name.replace('_', ' ') or clean_col in aliases:
                new_cols[col] = standard_name
                found = True
                break
        if not found:
            # Try partial matching if exact match not found
            for standard_name, aliases in mapping.items():
                if any(alias in clean_col for alias in aliases):
                     new_cols[col] = standard_name
                     found = True
                     break

    return df.rename(columns=new_cols)

def clean_leads(df):
    """
    Cleans and extracts specific fields from the dataframe.
    """
    df = normalize_columns(df)

    required_fields = [
        'first_name', 'last_name', 'organization', 'email', 'phone',
        'street', 'city', 'state', 'postal_code', 'country', 'designation'
    ]

    # Ensure all required fields exist
    for field in required_fields:
        if field not in df.columns:
            df[field] = ""

    return df[required_fields]
