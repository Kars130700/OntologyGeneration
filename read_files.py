import pandas as pd

# Define the file path
file_path = r"C:\Users\karst\Documents\University\SP\Software Production - Ontology Generation\SnomedCT_InternationalRF2_PRODUCTION_20210131T120000Z\SnomedCT_InternationalRF2_PRODUCTION_20210131T120000Z\Full\Terminology\sct2_Concept_Full_INT_20210131.txt"

# Read the file into a DataFrame
df = pd.read_csv(file_path, sep='\t', header=0, encoding='utf-8')

# Display the first 5 rows
print(df.head())

# Display the column names
print("Columns:", df.columns.tolist())
