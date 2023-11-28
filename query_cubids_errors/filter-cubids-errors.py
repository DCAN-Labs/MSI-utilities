"""
Author: rae McCollum
Date: 13 Oct 2023
Purpose: Takes in a cubids csv and either filters out lines containing a specificed value
or grabs lines that have a specific value.
"""

import csv

def remove_lines(tsv_input, tsv_output):
    """Filters out lines containing unwanted error strings"""
    with open(tsv_input, 'r', newline='') as input_file:
        reader = csv.reader(input_file, delimiter='\t')
        errors = ["NOT_INCLUDED", "INCONSISTENT_PARAMETERS", "EVENTS_TSV_MISSING", "TASK_NAME_CONTAIN_ILLEGAL_CHARACTER", "SLICE_TIMING_NOT_DEFINED", "TASK_NAME_MUST_DEFINE"] ## Enter errors that need to be removed here 
        data = [row for row in reader if not any(val in row for val in errors)]

    with open(tsv_output, 'w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter='\t')
        writer.writerows(data)

def filter_csv(input_csv, output_csv):
    """Pulls out any lines containing the desired error string"""
    with open(input_csv, 'r', newline='') as input_file, open(output_csv, 'w', newline='') as output_file:
        reader = csv.reader(input_file)
        writer = csv.writer(output_file)
        
        for row in reader:
            if 'INTENDED_FOR' in ','.join(row): ## Enter error that you want to grab here
                writer.writerow(row)

def remove_duplicates(input_file):
    # Read lines from the input file
    with open(input_file, 'r') as file:
        lines = file.readlines()

    # Remove duplicates while preserving order
    unique_lines = list(dict.fromkeys(lines))

    # Write back to the same file
    with open(input_file, 'w') as file:
        file.writelines(unique_lines)

if __name__ == "__main__":
    input_csv = input("Enter the csv you want to filter (then press enter): ")
    output_csv = input("Enter the path where the output csv should go (then press enter): ")

    print("Choose an option for which function you want. 1 is for removing lines with unwanted error strings. 2 is for grabbing lines with a specified error")

    choice = input("Enter 1 or 2: ")

    if choice == "1":
        remove_lines(input_csv, output_csv)
        remove_duplicates(output_csv)
    elif choice == "2":
        filter_csv(input_csv, output_csv)
        remove_duplicates(output_csv)
    else:
        print("Invalid Choice")

    #remove_lines(input_csv, output_csv)
											## Select which function you need here
    # filter_csv(input_csv, output_csv)
