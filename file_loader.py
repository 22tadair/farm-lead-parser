import pandas as pd
import os

def load_file(filepath):
    """
    Loads a CSV or Excel file into a pandas DataFrame.
    """
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.csv':
        return pd.read_csv(filepath)
    elif ext == '.xlsx':
        return pd.read_excel(filepath, engine='openpyxl')
    elif ext == '.xls':
        # Requires xlrd package
        return pd.read_excel(filepath)
    else:
        raise ValueError(f"Unsupported file format: {ext}")
