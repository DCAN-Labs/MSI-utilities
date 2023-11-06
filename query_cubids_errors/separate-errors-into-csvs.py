"""
Author: rae McCollum
Created: 10 Oct 23
Purpose: Given a list of errors, search through a cubids (or other error file) file and copy each type of error found to their own csv
"""

import csv

# Define the list of errors 
errors = [
    "EMPTY_FILE",
    "BOLD_NOT_4D",
    "NIFTI_PIXDIM4",
    "INTENDED_FOR",
    "PHASE_ENCODING_DIRECTION_MUST_DEFINE",
    "VOLUME_COUNT_MISMATCH",
    "REPETITION_TIME_MUST_DEFINE",
    "SESSION_LABEL_IN_FILENAME_DOESNOT_MATCH_DIRECTORY",
    "TOTAL_READOUT_TIME_MUST_DEFINE",
    "SLICE_TIMING_NOT_DEFINED",
    "NIFTI_TOO_SMALL",
    "DWI_MISSING_BVEC",
    "DWI_MISSING_BVAL",
    "QUICK_VALIDATION_FAILED",
    "INVALID JSON ENCODING"
]

# Create a dictionary to hold lines for each error
error_lines = {error: [] for error in errors}

# Define the input file path
input_tsv = '/home/rando149/shared/projects/rae_testing/cubids-ngdr/parsed-out-errors.tsv'

# Read the TSV file
with open(input_tsv, 'r', newline='') as tsvfile:
    reader = csv.reader(tsvfile, delimiter='\t')
    next(reader)
    for row in reader:
        error = row[1]  # Assuming error is in the second column, adjust if necessary
        error_lines[error].append('\t'.join(row))

# Write lines to separate files
for error, lines in error_lines.items():
    output_file = f"{error.lower()}-errors.txt"
    with open(output_file, 'w') as f:
        f.write('\n'.join(lines))

print("Files created successfully.")
