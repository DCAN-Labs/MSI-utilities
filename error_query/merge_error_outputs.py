import os
import pandas as pd
import sys
from collections import defaultdict
#from datetime import datetime

# Check if the directories path is provided as an argument
if len(sys.argv) < 2:
    print("Usage: python merge_error_outputs.py /path/to/error/query/results/directory /path/to/merged/errors/output_file.csv")
    sys.exit(1)

# Get the directories path from the command-line argument
error_directories = sys.argv[1:len(sys.argv)-1]
output_file = sys.argv[len(sys.argv)]
output_data = []

# Initialize a dictionary to store DataFrames for each error type
total_errors_dfs = defaultdict(pd.DataFrame)

# Loop through all files in the directory
for dir in error_directories:
    for filename in os.listdir(dir):
        filepath = os.path.join(dir, filename)
        df = pd.read_csv(filepath)
        #looks for "Errors" column in error query output files to distinguish which file is the combined file
        if "Errors" in df.columns:
            timestamp = os.path.getctime(filepath)
            df["Timestamp"] = timestamp
            df = df[['Subject_IDs', 'Session_IDs', 'Dataset_ID', 'Errors', 'Timestamp']]
            # Append the DataFrame to the dictionary
            total_errors_dfs[timestamp] = total_errors_dfs[timestamp].append(df, ignore_index=True)



# Merge the DataFrames based on 'Subject_IDs' and 'Session_IDs'
merged_df = pd.DataFrame()
for error_df, df in total_errors_dfs.items():
    merged_df = merged_df.append(df, ignore_index=True)

# Add a 'rerun_type' column with a default value
merged_df['rerun_type'] = 'default_value'

# Reset the index and write the merged DataFrame
merged_df = merged_df.reset_index(drop=True)
merged_df.to_csv(output_file, index=False)