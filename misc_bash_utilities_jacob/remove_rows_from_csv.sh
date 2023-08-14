#!/bin/bash

# Check if the correct number of arguments is provided
if [ $# -ne 2 ]; then
  echo "Usage: $0 <subject_ids_file> <data_file>"
  exit 1
fi

# Assign input arguments to variables
subject_ids_file=$1
data_file=$2

# Check if the input files exist
if [ ! -f "$subject_ids_file" ]; then
  echo "Error: Subject IDs file '$subject_ids_file' not found."
  exit 1
fi

if [ ! -f "$data_file" ]; then
  echo "Error: Data file '$data_file' not found."
  exit 1
fi

# Loop through the subject IDs and create a grep pattern to match them
grep_pattern=""
while IFS= read -r subject_id || [ -n "$subject_id" ]; do
  grep_pattern+="\b${subject_id}\b|"
done < "$subject_ids_file"

# Remove the trailing "|" from the grep_pattern
grep_pattern=${grep_pattern%|}

# Filter out the rows matching subject IDs and create a new data file
grep -vE "$grep_pattern" "$data_file" > "${data_file}.new"

# Replace the original data file with the new one
mv "${data_file}.new" "$data_file"

echo "Rows with matching subject IDs removed from '$data_file'."
