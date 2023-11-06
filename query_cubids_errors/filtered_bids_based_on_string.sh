#!/bin/bash

# Prompt the user for the input CSV file path
read -p "Enter the path to the input CSV file: " input_file

# Check if the input file exists
if [ ! -f "$input_file" ]; then
  echo "Input file does not exist."
  exit 1
fi

# Prompt the user for the strings to filter out (space-separated)
read -p "Enter the strings to filter out (space-separated): " filter_strings

# Convert the space-separated filter strings into an array
read -ra filters <<< "$filter_strings"

# Prompt the user for the output CSV file path
read -p "Enter the path to the output CSV file: " output_file

# Create a temporary file for storing the filtered data
temp_file=$(mktemp)

# Read the input file line by line, filter out lines containing the specified strings, and save the filtered data to the temporary file
while IFS= read -r line; do
  skip_line=0

  # Check if the line contains any of the filter strings
  for filter in "${filters[@]}"; do
    if [[ $line == *"$filter"* ]]; then
      skip_line=1
      break
    fi
  done

  # Save the line to the temporary file if it does not match any filter string
  if [ "$skip_line" -eq 0 ]; then
    echo "$line" >> "$temp_file"
  fi
done < "$input_file"

# Move the temporary file to the output file path
mv "$temp_file" "$output_file"

echo "Filtered data saved to $output_file."
