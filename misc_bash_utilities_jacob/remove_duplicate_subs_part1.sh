#!/bin/bash

# Replace 'bucket_name' with your actual S3 bucket name
bucket_name="s3://ABCC_year2_derivatives/processed/abcd-hcp-pipeline-v0.1.3"

# Output file to save sub-IDs without 'executivesummary' directory
output_file="sub_ids_without_processed_files_dir_have_been_removed_part2.csv"

# Get a list of all sub-IDs in the S3 bucket
sub_ids=$(cat /home/rando149/shared/projects/ABCC_year2_derivatives_reprocessing/slurm_abcd-hcp-pipeline_rerun/sub_ids_without_processed_files_dir_both_buckets.csv)

# Loop through each sub-ID and check if 'executivesummary' directory exists
for sub_id in ${sub_ids[@]}; do
    # Remove the trailing slash from sub_id
    sub_id=${sub_id%,2YearFollowUpYArm1}
    echo $sub_id
    
    # Check if the 'executivesummary' directory exists for the current sub-ID
    if [ $(s3cmd ls ${bucket_name}/sub-${sub_id}/ses-2YearFollowUpYArm1/files/ | wc -l) == 0 ]; then
        echo "files directory not found for sub-ID: ${sub_id}"
        echo "=======================removing processed outputs for sub-ID: ${sub_id}============================="
        s3cmd rm ${bucket_name}/sub-${sub_id} --recursive -v 
        echo "=======================removed processed outputs for sub-ID: ${sub_id}=============================="
        echo "=======================removing derivatives outputs for sub-ID: ${sub_id}==========================="
        s3cmd rm s3://ABCC_year2_derivatives/derivatives/abcd-hcp-pipeline-v0.1.3/sub-${sub_id} --recursive -v
        echo "=======================removed derivatives outputs for sub-ID: ${sub_id}============================"
        echo "${sub_id}" >> "${output_file}"
    else
        echo "files directory exists for sub-ID: ${sub_id}"
    fi
done

