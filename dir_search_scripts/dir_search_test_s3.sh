#!/bin/bash

# Replace 'bucket_name' with your actual S3 bucket name
bucket_name="s3://ABCC_year2_derivatives/derivatives/abcd-hcp-pipeline-v0.1.3"

# Output file to save sub-IDs without 'executivesummary' directory
output_file="sub_ids_without_executivesummary_dir_full_list_parse.csv"

# Get a list of all sub-IDs in the S3 bucket
sub_ids=$(cat /home/rando149/shared/projects/ABCC_year2_derivatives_reprocessing/slurm_abcd-hcp-pipeline_rerun/audit/part1_ok_subs_minus_GE_minus_missing_dirs_no_ws.csv)

# Loop through each sub-ID and check if 'executivesummary' directory exists
for sub_id in ${sub_ids[@]}; do
    # Remove the trailing slash from sub_id
    sub_id=${sub_id%,2YearFollowUpYArm1}
    echo $sub_id
    
    # Check if the 'executivesummary' directory exists for the current sub-ID
    if [ $(s3cmd ls ${bucket_name}/sub-${sub_id}/ses-2YearFollowUpYArm1/executivesummary/ | wc -l) == 0 ]; then
        echo "executivesummary directory not found for sub-ID: ${sub_id}"
        echo "${sub_id}" >> "${output_file}"
    else
        echo "executivesummary directory exists for sub-ID: ${sub_id}"
    fi
done

