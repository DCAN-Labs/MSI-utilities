#!/bin/bash

# Specify your BIDS directory
tier1_dir="/path/to/dir/with/subject/dirs/"

# Specify output file
output="sub_directories.txt"

# Run ls command, filter directories starting with "sub-", and write to a file
ls $tier1_dir | grep -oP "sub-\K[^/]+" > $output

echo "Directories starting with 'sub-' have been written to " $output
