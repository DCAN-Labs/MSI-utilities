import os
import pandas as pd
import sys
#from collections import defaultdict
#from datetime import datetime

# Check if the directories path is provided as an argument
if len(sys.argv) < 3:
    print("Usage: python merge_error_outputs.py /path/to/error/query/results/directory1/ /path/to/error/query/results/directory2/ /path/to/merge/output/dir/")
    sys.exit(1)

# Get the directories path from the command-line argument
error_directories = sys.argv[1:len(sys.argv)-1]
output_dir = sys.argv[len(sys.argv)-1]
#output_data = []

# Initialize a dictionary to store DataFrames for each error type
total_errors_dfs = []

# Loop through all files in the directory
for dir in error_directories:
    if dir[len(dir)-1] == "/":
        dir = dir[:-1] 
        dir_basename = os.path.basename(dir)
    #total_errors_dfs[dir_basename] = pd.DataFrame()
        for filename in os.listdir(dir):
            if filename == "all_err_types.csv":
                filepath = os.path.join(dir, filename)
                df = pd.read_csv(filepath)
                df["Dataset_ID"] = dir_basename
                df = df[['Subject_IDs', 'Session_IDs', 'Errors', 'Dataset_ID']]
                df = df.rename(columns={'Errors': 'Error_Type'})
                total_errors_dfs.append(df)

# Concatenate the DataFrames in the list
if total_errors_dfs:
    combined_df = pd.concat(total_errors_dfs, ignore_index=True)
    # Create the new DataFrame with the desired columns
    counts_df = combined_df.groupby(['Dataset_ID', 'Error_Type'])['Subject_IDs'].nunique().reset_index()
    counts_df.rename(columns={'Subject_IDs': 'Counts'}, inplace=True)

    # Save the combined DataFrame to a file
    output_csv = os.path.join(output_dir, "combined_error_types_for_dataset.csv")
    counts_csv = os.path.join(output_dir, "combined_error_counts_for_dataset.csv")
    combined_df.to_csv(output_csv, index=False)
    counts_df.to_csv(counts_csv, index=False)
else:
    print("No data found in the provided directories.")


        
"""         df = pd.read_csv(filepath)
        #looks for "Errors" column in error query output files to distinguish which file is the combined file
        if "Errors" in df.columns:
            timestamp = os.path.getctime(filepath)
            df["Timestamp"] = timestamp
            df = df[['Subject_IDs', 'Session_IDs', 'Dataset_ID', 'Errors', 'Timestamp']]
            # Append the DataFrame to the dictionary
            total_errors_dfs[timestamp] = total_errors_dfs[timestamp].append(df, ignore_index=True) """

""" 

# Merge the DataFrames based on 'Subject_IDs' and 'Session_IDs'
merged_df = pd.DataFrame()
for error_df, df in total_errors_dfs.items():
    merged_df = merged_df.append(df, ignore_index=True)

# Add a 'rerun_type' column with a default value
merged_df['rerun_type'] = 'default_value'

# Reset the index and write the merged DataFrame
merged_df = merged_df.reset_index(drop=True)
merged_df.to_csv(output_file, index=False) """