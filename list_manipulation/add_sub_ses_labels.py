import argparse
import csv
import os

"""
Author: rae McCollum
Created: 26 Oct 23
Last Modified: 22 Feb 24
Purpose: Add or remove "sub-"/"ses-" labels 
"""

def _cli():
    """
    :return: Dictionary with all validated command-line arguments from the user
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input', dest="file", type = valid_path, 
        help='Path to a subject list (.tsv/.csv/.txt)'
    )
    parser.add_argument(
        '--output-file', default = os.path.join(os.getcwd(), "labeled_subjects.txt"), dest="output",
        help='Path to an output file. Default is cwd/labeled_subjects.txt'
    )
    parser.add_argument(
        '--function', type = valid_operation, dest="func",
        help=('What function to run. Can add sub- and ses- prefixes, add/remove sub- prefix, or add/remove session. ' 
        'Input must be one of the following: [add-both-labels, add-sub, remove-sub, add-ses, remove-ses] '
        'If removing/adding a session, specify which session label with the --session flag')
    )
    parser.add_argument(
        '--session', dest="ses",
        help='Session label to add/remove. Can either be with or without ses- label.'
    )
    return vars(parser.parse_args())

def valid_operation(choice):
    functions = ["add-both-labels", "add-sub", "remove-sub", "add-ses", "remove-ses"]
    return choice in functions

def valid_path(path):
    return os.path.exists(path) and os.access(path, os.R_OK)

def add_sub_ses_labels(input_file,output_file):
    """
    Takes in a csv of the format subjectID,sessionID and adds the "sub-" and "ses-" prefixed
    """
    with open(input_file, 'r') as file:
        reader = csv.reader(file)
        data = list(reader)

    modified_data = []

    for line in data:
        subject_id, session_id = line
        modified_line = f'sub-{subject_id},ses-{session_id}'
        modified_data.append([modified_line])

    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_NONE, escapechar=' ')
        writer.writerows(modified_data)

    print(f'Data written to {output_file}')

def add_sub_labels(input_file,output_file):
    """
    Takes in a csv/txt/tsv of the format subjectID (can have something following but subjectID needs to be start of line) and adds the "sub-" prefixes
    """
    labeled_data = []
    
    # Add "sub-" to beginning of each ling
    with open(input_file, 'r') as in_file:
        for line in in_file:
            subject_id = line.strip()
            modified_line = f'sub-{subject_id}'
            labeled_data.append(modified_line)

    with open(output_file, 'w') as output:
        output.write("\n".join(labeled_data))
    print(f'Data written to {output_file}')

def remove_sub_labels(input_file, output_file):
    """
    Takes in a csv/txt/tsv file of the format sub-subjectID and removes the "sub-" prefix
    """
    with open(input_file, 'r') as infile:
        lines = infile.readlines()

    # Remove "sub-" from the beginning of each line
    modified_lines = [line.lstrip('sub-') for line in lines]

    with open(output_file, 'w') as outfile:
        outfile.writelines(modified_lines)
    print(f'Data written to {output_file}')

def add_session_id(input_file, output_file, session_id):
    """
    Takes in a txt file of subjectIDs (with or without the "sub-" prefix) and adds the session
    """
    with open(input_file, 'r') as infile:
        lines = infile.readlines()

    # Add session ID to each line
    modified_lines = [f"{line.strip()},{session_id}\n" for line in lines]

    with open(output_file, 'w') as outfile:
        outfile.writelines(modified_lines)
    print(f'Data written to {output_file}')

def remove_session_id(input_file, output_file, session_id):
    """
    Takes in a txt file of subjectIDs (with or without the "sub-" prefix) and removes the session
    """
    with open(input_file, 'r') as infile:
        lines = infile.readlines()

    # Remove session ID from each line
    modified_lines = [line.strip().replace(f",{session_id}", '\n') for line in lines]

    with open(output_file, 'w') as outfile:
        outfile.writelines(modified_lines)
    print(f'Data written to {output_file}')

def make_func_dict():
    operations = {"add-both-labels":add_sub_ses_labels, "add-sub":add_sub_labels, "remove-sub":remove_sub_labels, "add-ses":add_session_id, "remove-ses":remove_session_id}
    return operations

def main():
    cli_args = _cli()
    input_file = cli_args["file"]
    output_file = cli_args["output"]
    option = cli_args["func"]
    session = cli_args["ses"]
    choices = make_func_dict()
    if "ses" in option:
        choices[option](input_file, output_file, session)
    else:
        choices[option](input_file, output_file)

if __name__ == '__main__':
    main()
