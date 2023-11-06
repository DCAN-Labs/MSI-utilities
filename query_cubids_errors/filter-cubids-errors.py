"""
Author: rae McCollum
Date: 13 Oct 2023
Purpose: Takes in a cubids csv and either filters out lines containing a specificed value
or grabs lines that have a specific value.
"""

import csv

def remove_lines(tsv_input, tsv_output):
    with open(tsv_input, 'r', newline='') as input_file:
        reader = csv.reader(input_file, delimiter='\t')
        errors = ["NOT_INCLUDED", "INCONSISTENT_PARAMETERS", "EVENTS_TSV_MISSING", "TASK_NAME_CONTAIN_ILLEGAL_CHARACTER"] ## Enter errors that need to be removed here 
        data = [row for row in reader if not any(val in row for val in errors)]

    with open(tsv_output, 'w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter='\t')
        writer.writerows(data)

def filter_csv(input_csv, output_csv):
    with open(input_csv, 'r', newline='') as input_file, open(output_csv, 'w', newline='') as output_file:
        reader = csv.reader(input_file)
        writer = csv.writer(output_file)
        
        for row in reader:
            if 'INTENDED_FOR' in ','.join(row): ## Enter error that you want to grab here
                writer.writerow(row)

if __name__ == "__main__":
    input_csv = "/home/rando149/shared/projects/rae_testing/GE_issue_testing/GE-cubids/slurm_cubids_with_s3/GE-reprocessed-cubids.csv"
    output_csv = "/home/rando149/shared/projects/rae_testing/GE_issue_testing/GE-cubids/slurm_cubids_with_s3/new-part2-GE-issues.csv"

    #remove_lines(input_csv, output_csv)
											## Select which function you need here
    # filter_csv(input_csv, output_csv)
