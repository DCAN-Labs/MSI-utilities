import csv
import re

"""
Author: rae McCollum
Created: 5 Dec 2023
Purpose: Filter fasttrack to only include certain subject IDs, lines without a specific word, or lines that have bad data (ftq_usable==0). Can also produce a list of subject IDs present in a fasttrack.
Last Modified: 26 Feb 2024
"""


def grab_subject_ids(file_path, output_file):
    """Create list of all subject IDs (removing _ from subject row)"""
    subjectkey_list = []

    with open(file_path, 'r') as in_file:
        reader = csv.reader(in_file, delimiter='\t')
        for row in reader:
            if len(row) >= 4:
                subjectkey = row[3].replace("_", "")
                subjectkey_list.append(subjectkey)
            else:
                print(f"Warning: Skipping row {row} as it doesn't have enough columns.")
    with open(output_file, 'w') as output_file:
        for sub in sub_list:
            output_file.write(f"{sub}\n")

def filter_by_subject(input_file, output_file, allowed_subjectkeys_file):
    try:
        # Read allowed subjectkeys from the file
        with open(allowed_subjectkeys_file, 'r') as allowed_file:
            allowed_subjectkeys = [line.strip() for line in allowed_file.readlines()]

        with open(input_file, 'r') as file:
            lines = file.readlines()

        # Process each line
        filtered_lines = []
        for line in lines:
            # Split the line by tabs and extract the subjectkey
            columns = line.strip().split('\t')
            if len(columns) > 4:
                subjectkey = columns[3].replace("_", "")
                subjectkey = subjectkey.replace('"', "")  # Assuming "subjectkey" is in the second column (index 1)
                
                # Check if the subjectkey is in the allowed_subjectkeys list
                if subjectkey in allowed_subjectkeys:
                    filtered_lines.append(line)

        with open(output_file, 'w') as output_file:
            output_file.writelines(filtered_lines)

        print(f"Filtered content written to '{output_file}'.")
    except FileNotFoundError:
        print(f"Error: File not found at '{input_file}' or '{allowed_subjectkeys_file}'")

def remove_lines_with_word(input_file, output_file, word_to_remove):
    with open(input_file, 'r') as file:
        lines = file.readlines()

    # Filter out lines containing the specified word
    filtered_lines = [line for line in lines if word_to_remove not in line]

    with open(output_file, 'w') as file:
        file.writelines(filtered_lines)
        
def grab_bad_data(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            # Split the line into columns using tabs
            columns = line.strip().split('\t')
            
            # Check if the 19th column (index 18) has a value of "0"
            ftp_usable = columns[18]
            if len(columns) >= 19 and columns[18] == '"0"':
                # If yes, write the line to the output file
                outfile.write(line)

if __name__ == "__main__":
    fasttrack_path = "/path/to/abcd_fasttrack.txt"
    subject_file = "/path/to/subject_list.txt"  # Needs to be a file that only has the subjectID without the "sub-" prefix
    output_file_path = "/path/to/output_file.txt"
    # Specify the word to remove
    word_to_remove = 'Replaced'
    
    # Call the desired function 
    # grab_subject_ids(fasttrack_path, output_file_path)
    # filter_by_subject(fasttrack_path, output_file_path, subject_file)
    # remove_lines_with_word(fasttrack_path, output_file_path, word_to_remove)
    # grab_bad_data(fasttrack_path, output_file_path)

