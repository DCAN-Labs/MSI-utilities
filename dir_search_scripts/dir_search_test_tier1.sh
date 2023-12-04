#!/bin/bash

path="/spaces/ngdr/ref-data/abcd/nda-3165-2020-09"

# Output file to save sub-IDs without 'executivesummary' directory
output_file="sub_ids_with_ses_year2.csv"

# Get a list of all sub-IDs in the S3 bucket
sub_ids=$(cat /home/rando149/shared/projects/ABCC_year2_derivatives_reprocessing/error_query/year2_subjects.csv)

# Loop through each sub-ID and check if 'executivesummary' directory exists
for sub_id in ${sub_ids[@]}; do
    # Remove the trailing slash from sub_id
    sub_id=${sub_id%,2YearFollowUpYArm1}
    echo $sub_id
    
    # Check if the 'ses-baselineYear1Arm1' directory exists for the current sub-ID
    if [ $(ls ${path}/sub-${sub_id}/ses-2YearFollowUpYArm1 | wc -l) == 0 ]; then
        echo "baselineYear1Arm1 directory not found for sub-ID: ${sub_id}"
    else
        echo "baselineYear1Arm1 directory exists for sub-ID: ${sub_id}"
        echo "${sub_id}" >> "${output_file}"
    fi
done

