"""
Author: rae McCollum
Created: 25 Nov 23 
Purpose: Creates subject lists of cubids errors from the error text files created by separate-errors-into-csvs.py
Last Modified: 
"""
import os

def extract_subject_from_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith('-errors.txt'):
            input_filepath = os.path.join(directory, filename)
            error_name = filename.split('-')[0]

            # Read the first column of each line in the file
            with open(input_filepath, 'r') as infile:
                lines = infile.readlines()

            subjects_and_sessions = set()
            for line in lines:
                # Extract subject and session from the first column
                parts = line.split('/')
                subject = parts[1]
                session = parts[2]
                subjects_and_sessions.add(f'{subject},{session}')

            # Write subjects to a new file
            output_filepath = os.path.join(directory, f'{error_name}-subjects.txt')
            with open(output_filepath, 'w') as outfile:
                outfile.write('\n'.join(subjects_and_sessions))

            print(f"Processed {filename}. Extracted subjects written to {output_filepath}")

# Example usage:
input_directory_path = '/home/rando149/shared/projects/rae_testing/abcc_s3_cubids/cubids_errors/year2_errors/'  # Replace with your input directory path
output_directory_path = '/path/to/your/output/directory'  # Replace with your output directory path

extract_subject_from_files(input_directory_path)
