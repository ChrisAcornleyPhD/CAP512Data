import pandas as pd
import hashlib

# Load all csvs
df = pd.read_csv('2020-2021\\GradeExport.csv')
df2 = pd.read_csv('2021-2022\\GradeExport.csv')
df3 = pd.read_csv('2022-2023\\GradeExport.csv')

# Pass username through sha256 hash function
def formatUsername(x):
    return hashlib.sha256(str(x).encode('utf-8')).hexdigest()

# Map above function to each USERNAME entry in all three dataframes
df['USERNAME'] = df['USERNAME'].map(formatUsername)
df2['USERNAME'] = df2['USERNAME'].map(formatUsername)
df3['USERNAME'] = df3['USERNAME'].map(formatUsername)

# Save dataframes to new csv
df.to_csv('2020-2021\\GradeReport2020.2021.csv')
df2.to_csv('2021-2022\\GradeReport2021.2022.csv')
df3.to_csv('2022-2023\\GradeReport2022.2023.csv')