import os
import pandas as pd
import sys
from collections import defaultdict

# Check if the directories path is provided as an argument
if len(sys.argv) < 3:
    print("Usage: python merge_error_outputs.py /path/to/error/query/results/directory /path/to/merged/errors/output_file.csv")
    sys.exit(1)

# Get the directories path from the command-line argument
error_directory = sys.argv[1]
output_file = sys.argv[2]
output_data = []

# Initialize a dictionary to store DataFrames for each error type
error_type_dfs = defaultdict(pd.DataFrame)

# Loop through all files in the directory
for filename in os.listdir(error_directory):
    if filename.endswith('.csv'):
        # Construct the full file path
        filepath = os.path.join(error_directory, filename)

        # Read the CSV file into a Pandas DataFrame
        df = pd.read_csv(filepath)
        df = df[['Subject_IDs', 'Session_IDs']]

        # Extract the error type from the filename
        error_type = filename.split('.csv')[0]

        # Add an 'error_type' column to the DataFrame
        df['error_type'] = error_type

        # Append the DataFrame to the dictionary
        error_type_dfs[error_type] = error_type_dfs[error_type].append(df, ignore_index=True)

# Merge the DataFrames based on 'Subject_IDs' and 'Session_IDs'
merged_df = pd.DataFrame()
for error_type, df in error_type_dfs.items():
    merged_df = merged_df.append(df, ignore_index=True)

# Add a 'rerun_type' column with a default value
merged_df['rerun_type'] = 'default_value'

# Reset the index and write the merged DataFrame
merged_df = merged_df.reset_index(drop=True)
merged_df.to_csv(output_file, index=False)