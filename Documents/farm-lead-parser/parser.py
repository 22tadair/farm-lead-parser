import pandas as pd

file = "CM Leads (1).xlsx"

df = pd.read_excel(file)

print(df.head())