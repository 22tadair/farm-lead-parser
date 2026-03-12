import pandas as pd
import os

def export_to_excel(df, output_path):
    """
    Exports the DataFrame to an Excel file.
    """
    try:
        df.to_excel(output_path, index=False, engine='openpyxl')
        print(f"Successfully exported to {output_path}")
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
