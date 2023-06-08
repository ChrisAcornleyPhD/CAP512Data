import pandas as pd
import os




# List all csvs
list_of_files = [x for x in os.listdir('..\\') if x.endswith('.csv')]

# open Grade export for each year
for file in list_of_files:
    df = pd.read_csv('..\\'+file)
    sub_df = df[df.filter(regex='^(?!Unnamed)').columns]        # Removed any unnamed columns (these are not needed)
    sub_df = sub_df[sub_df.filter(regex='^((?!IGNORE).)*$').columns]  # Remove anu IGNORE columns

    # extract column names (exclude USERNAME, GRADE, SYMBOL, ATTENDANCE TOTAL, ATTENDANCE PERCENT)
    sub_df = sub_df[sub_df.filter(regex='^(?!USERNAME)').columns]
    sub_df = sub_df[sub_df.filter(regex='^(?!GRADE)').columns]
    sub_df = sub_df[sub_df.filter(regex='^(?!SYMBOL)').columns]
    sub_df = sub_df[sub_df.filter(regex='^(?!ATTENDANCE)').columns]

    # If no columns left, skip to next file
    if not len(sub_df.columns) > 0:
        continue

    # Extract dataframes - Group A, Group B, Lecture
    a_sub_df = sub_df[sub_df.filter(regex='Practical - Group A').columns]
    b_sub_df = sub_df[sub_df.filter(regex='Practical - Group B').columns]
    l_sub_df = sub_df[sub_df.filter(regex='Lecture').columns]