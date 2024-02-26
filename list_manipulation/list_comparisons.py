import pandas as pd
import argparse
import os

# TODO: Take into account sessions (currently assumes that we are just comparing subjects from the same year)
# TODO: Account for files that have headings 
#       TODO: Ask for heading input/smartly figure out which column/assume first column is subject 
#       TODO: Add heading consideration
# TODO: Can add a function to grab a subject list from a s3 bucket/directory path
#       TODO: Can steal s3 functionality from abcd-hcp-pipeline audit script

def _cli():
    """
    :return: Dictionary with all validated command-line arguments from the user
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input-1', dest="file1", type = valid_path, 
        help='Path to a subject list (.tsv/.csv/.txt)'
    )
    parser.add_argument(
        '--input-2', dest="file2", type = valid_path,
        help=('Path to a different subject list (.tsv/.csv/.txt)' 
        'File extension should be that same for both input files')
    )
    parser.add_argument(
        '--output-file', default = os.path.join(os.getcwd(), "comparison.txt"), dest="output",
        help='Path to an output file. Default is cwd/comparison.txt'
    )
    parser.add_argument(
        '--function', type = valid_operation, dest="func",
        help=('What function to run. Can print out number of unique subjects, write out values that are in both files, remove doubles,',
        'print subjects that only exist in the first list, or remove subjects in the first file from the second file. Input must be one of the following:',
        'count-unique, write-overlap, remove-doubles, write-unique, remove-subjects')
    )
    # parser.add_argument(
    #     '--header', dest="head", 
    #     help='Name of column that contains subject IDs (for files with headers)'
    # )
    # parser.add_argument(
    #     '--path', dest="dir", type = valid_path,
    #     help='Path to a BIDS/derivatives directory or s3 bucket to get a subject list of contents (will pull subject IDs from top level directories)' 
    # )
    return vars(parser.parse_args())

def valid_operation(choice):
    functions = ["count-unique", "write-overlap", "remove-doubles", "write-unique", "remove-subjects"]
    return choice in functions

def valid_path(path):
    return os.path.exists(path) and os.access(path, os.R_OK)

def count_unique_subjects(input_file):
    """
    Takes in a subject ID file
    Prints out the number of unique lines that start with a subject ID
    """
    sub_lines = []
    # Looks for lines that start with "sub-" or "NDARIN" to find subject IDs
    with open(input_file, "r") as input_file:
        for line in input_file:
            if line.startswith("sub-") or line.startswith("NDARIN"):
                sub_lines.append(line.strip()) 

    df = pd.DataFrame({"Subjects": sub_lines})
    unique_count = df["Subjects"].nunique()

    print("Unique subjects:", unique_count)

def compare_files(file1, file2, output_file):
    """
    Takes in two input subject ID files of the same format and an output file
    Writes file of subject IDs that exist in both files 
    """
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        lines1 = set(f1.readlines())
        lines2 = set(f2.readlines())
        common_lines = lines1.intersection(lines2) 
    print("Overlapping values:",len(common_lines))

    with open(output_file, 'w') as output:
        output.write("\n".join(common_lines))

    print(f'Data written to {output_file}')

def lines_not_overlapping(file1_path, file2_path, output_path):
    """
    Writes out lines that are only in file1_path
    """
    with open(file1_path, 'r') as f1, open(file2_path, 'r') as f2:
        lines1 = set(f1.readlines())
        lines2 = set(f2.readlines())

    lines_unique_to_file1 = lines1 - lines2

    print("Subjects only in first list:",len(lines_unique_to_file1))
    with open(output_path, 'w') as output:
        output.writelines(lines_unique_to_file1)
    print(f'Data written to {output_path}')

def remove_subjects(subject_file, input_file, output_file):
    """
    Removes lines from input_file that are also in subject_file
    """
    with open(subject_file, 'r') as sub_file:
        subjects = set(sub_file.read().splitlines())

    good_lines = []
    with open(input_file, 'r') as in_file:
        for line in in_file:
            line = line.strip()
            if not any(sub in line for sub in subjects):
                good_lines.append(line)
    print("Remaining subjects:",len(good_lines))
   
    with open(output_file, 'w') as output:
        output.write("\n".join(good_lines))
    print(f'Data written to {output_file}')

def remove_duplicates(input_file, output_file):
    """
    Force list of subjects into set to remove duplicate entries
    """
    singles = set()
    with open(input_file, 'r') as in_file:
        for line in in_file:
            singles.add(line.strip())

    print("Number of subjects w/o duplicates:",len(singles))
    with open(output_file, 'w') as output:
        output.write("\n".join(singles))
    print(f'Data written to {output_file}')

def make_func_dict():
    operations = {"count-unique":count_unique_subjects, "write-overlap":compare_files, "remove-doubles":remove_duplicates, "write-unique":lines_not_overlapping, "remove-subjects":remove_subjects}
    return operations

def main():
    cli_args = _cli()
    input1 = cli_args.file1
    input2 = cli_args.file2
    output = cli_args.output
    operation = cli_args.func
    choices = make_func_dict()
    if "count" in operation:
        choices[operation](input1)
    elif "doubles" in operation:
        choices[operation](input1, output)
    else:
        choices[operation](input1, input2, output)

if __name__ == '__main__':
    main()


		







