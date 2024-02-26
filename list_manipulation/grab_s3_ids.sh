#!/bin/bash

# Specify your S3 bucket name
S3_BUCKET="ABCC_year1"

# Specify output file
output="s3_year1_directories.txt"

# Run s3cmd ls command, filter directories starting with "sub-", and write to a file
s3cmd ls s3://$S3_BUCKET/ | grep -oP "s3://$S3_BUCKET/sub-\K[^/]+" > $output

echo "Directories starting with 'sub-' have been written to " $output
