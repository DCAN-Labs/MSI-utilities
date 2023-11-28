#!/bin/bash

# Author: rae McCollum
# Last Modified: 28 Nov 23
# Purpose: For every yaml in a specified directory, replace a string with a new one (originally used to update release date for uploads). If you are looking at a different file type, specifiy that in line 15. 

# Specify the folder path containing the .yaml files
folder_path="/home/rando149/shared/projects/ABCD/ABCC_Upload/working_directories/QSIprep_new_year1_submission/prepared_yamls/"

# Specify the string to be replaced
old_string='November 2023'

# Specify the replacement string
new_string='December 2023'

# Loop through each .yaml file in the folder OR SPECIFY OTHER FILE TYPE BELOW
for file in "$folder_path"/*.yaml; do
  # Check if the file exists
  if [ -e "$file" ]; then
    # Replace the string in the file using sed
    grep -l "old_string" $file 
    sed -i "s|$old_string|$new_string|" "$file"
    #echo "Replaced '$old_string' with '$new_string' in $file"
  fi
done
