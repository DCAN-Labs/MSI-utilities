import os
import sys
import pandas as pd

# Check if the directories path is provided as an argument
if len(sys.argv) < 3:
    print("Usage: python count_error_outputs.py /path/to/error/query/results/directory /path/to/error/counts/output_file.csv")
    sys.exit(1)

# Get the directories path from the command-line argument
error_directory = sys.argv[1]
output_file = sys.argv[2]
output_data = []

# Loop through all the csv files in the error directory
for filename in os.listdir(error_directory):
    if filename.endswith('.csv'):
        # Construct the full file path
        filepath = os.path.join(error_directory, filename)

        # Read the CSV file into a Pandas DataFrame
        df = pd.read_csv(filepath)

        # Get the count of unique subject IDs
        subject_count = df['Subject_IDs'].nunique()

        # Append the file name and subject count to the output data list
        output_data.append({'Error_File': filename, 'Unique_Subject_Count': subject_count})

# Create a Pandas DataFrame from the output data
output_df = pd.DataFrame(output_data)

# Write the output DataFrame to a CSV file
output_df.to_csv(output_file, index=False)