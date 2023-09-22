# Steps:
#   1. set the variables: 
#       a. input_1 needs to be a path to the output_logs directory
#       b. input_2 will be a path to the run_files directory, to find the associated sub/ses information for each unique run file
#       c. output will be a path to a directory where the csvs will go
#   2. parse through the output_logs directory and create a unique list of all the run numbers
#   3. find the most recent .err file associated with each unique run number
#   4. read each error file and look to match certain strings that are associated with certain errors
#   5. create a list of all the run numbers that have a certain error string associated with it
#   6. using each list of run numbers, find subject_id and session_id for each run number within the associated error file.
#      If subject_id and session_id not found within the .err file, extract info from the associated run file in the run_files directory
#   7. return csvs for each error that contain the path to the error log that contains the error, 
#      and the associated subject_id and session_id for that error log (found using run number)

# TODO:
#   - test on directories 
#   - test out ability to add in other error strings
#   - need to add in a catch for .err files that dont have an error string in them/or a completed processing string
#   - add in comments

import os
import glob
import re
import csv
import argparse

error_strings = {
    "time_limit": "DUE TO TIME LIMIT",
    "oom": "oom-kill",
    "assertion_error": "AssertionError",
    "key_error": "KeyError",
    "index_error": "IndexError",
    "s3_credentials": "An error occurred fetching S3 credentials",
    "s3_quota": "ERROR: S3 error: 403 (QuotaExceeded)",
    "no_response_status": "ERROR: Cannot retrieve any response status before encountering an EPIPE or ECONNRESET exception",
    "upload_failed": "WARNING: Upload failed:",
    "unable_to_copy": "WARNING: Unable to remote copy files",
    "ssl_verification": "ERROR: SSL certificate verification failure:",
    "connection_reset": "error: [Errno 104] Connection reset by peer"
}

def main():
    parser = argparse.ArgumentParser(description="Review error logs and extract relevant error information from each .err file.")
    parser.add_argument("-l", "--output_logs_dir", dest="output_logs_dir", 
                        help="Required. Path to the output_logs directory."
                        )
    parser.add_argument("-r", "--run_files_dir", dest="run_files_dir", action="store_true", default="", 
                        help="Optional. Path to the run_files directory."
                            "Recommended to use if there could be missing subject information in the .err file."
                            "IMPORTANT: if run files in this directory have been remade since running the processing jobs,"
                            "this could result in the incorrect subject information being matched to the .err log."
                            "Suggestion is to only use this flag after first round of processing."
                        )
    parser.add_argument("-o", "--output_dir", dest="output_dir", 
                        help="Required. Path to the directory where the CSVs will be saved."
                        )
    parser.add_argument("-p", "--add_error_log_path", dest="add_error_log_path", action="store_true", default = False,
                        help="Include the 'Error_Log_Path' in the CSVs for each .err file."
                        )
    parser.add_argument("-e", "--error_strings", dest="error_strings", nargs="+", default=error_strings,
                        help="Optional arg to add in different error strings to dictionary of strings to search for. Current default dictionary:"
                            "'time_limit': 'DUE TO TIME LIMIT',"
                            "'oom': 'oom-kill',"
                            "'assertion_error': 'AssertionError',"
                            "'key_error': 'KeyError',"
                            "'index_error': 'IndexError',"
                            "'s3_credentials': 'An error occurred fetching S3 credentials',"
                            "'s3_quota': 'ERROR: S3 error: 403 (QuotaExceeded)',"
                            "'no_response_status': 'ERROR: Cannot retrieve any response status before encountering an EPIPE or ECONNRESET exception',"
                            "'upload_failed': 'WARNING: Upload failed:',"
                            "'unable_to_copy': 'WARNING: Unable to remote copy files',"
                            "'ssl_verification': 'ERROR: SSL certificate verification failure:',"
                            "'connection_reset': 'error: [Errno 104] Connection reset by peer'"
                            
                            "In order to add a new error string to search for, use this format:"
                            "'csv_title': 'string to search for'"
                        )
    args = parser.parse_args()

    run_numbers = get_run_numbers(args.output_logs_dir)
    most_recent_err_files = get_most_recent_err_files(args.output_logs_dir, run_numbers)
    errors_by_string, run_numbers_with_error = find_errors(args.error_strings, most_recent_err_files)

    error_data = find_subject_session_ids(args.run_files_dir, run_numbers_with_error, most_recent_err_files)
    matched_error_data = match_error_data(error_data, errors_by_string)

    match_and_print_errors(matched_error_data, error_strings, args.output_dir, args.add_error_log_path)

# Create a unique list of run numbers from output_logs directory
def get_run_numbers(output_logs_dir):
    run_numbers = set()
    for root, _, files in os.walk(output_logs_dir):
        for file in files:
            if file.endswith(".err"):
                run_number = re.search(r"_(\d+)\.err", file)
                if run_number:
                    run_numbers.add(run_number.group(1))
    return run_numbers

# Find the most recent .err file for each unique run number
def get_most_recent_err_files(output_logs_dir, run_numbers):
    most_recent_err_files = {}
    for run_number in run_numbers:
        err_files = glob.glob(os.path.join(output_logs_dir, f"*_{run_number}.err"))
        if err_files:
            most_recent_err_files[run_number] = max(err_files, key=os.path.getctime)
    return most_recent_err_files

# Read error files and look for specific error strings
def find_errors(error_strings, most_recent_err_files):
    errors_by_string = {error_string: [] for error_string in error_strings.values()} 
    run_numbers_with_error = set()
    
    for run_number, err_file in most_recent_err_files.items():
        with open(err_file, 'r') as err_file:
            content = err_file.read()
            for error_string in error_strings.values():
                if error_string in content:
                    errors_by_string[error_string].append(run_number)
                    run_numbers_with_error.add(run_number)
    
    return errors_by_string, run_numbers_with_error

# Find subject_id and session_id for each run number within the associated error file
def find_subject_session_ids(run_files_dir, run_numbers_with_error, most_recent_err_files):
    error_data = {
        "Run_Number": [],
        "Error_Log_Paths": [],
        "Subject_IDs": [],
        "Session_IDs": []
    }

    for run_number in run_numbers_with_error:
        with open(most_recent_err_files[run_number], 'r') as err_file:
            err_content = err_file.read()
            sub_match = re.search(r"sub-([a-zA-Z0-9_]+)", err_content)
            ses_match = re.search(r"ses-([a-zA-Z0-9_]+)", err_content)
            if sub_match and ses_match:
                subject_id = sub_match.group(1)
                session_id = ses_match.group(1)
                inputs = [run_number, most_recent_err_files[run_number], subject_id, session_id]
                for key, value in zip(error_data.keys(), inputs):
                    error_data[key].append(value)
            elif not run_files_dir == "": 
                # If subject_id and session_id not found, extract info from the associated run file in the run_files directory 
                run_file = os.path.join(run_files_dir, f"run{run_number}")
                if os.path.exists(run_file):
                    with open(run_file, 'r') as run_file:
                        lines = run_file.readlines()
                        subject_id = None
                        session_id = None
                        for line in lines:
                            if "subject_id" in line:
                                subject_id = re.search(r"subject_id=(\w+)", line)
                                if subject_id:
                                    subject_id = subject_id.group(1)
                            elif "ses_id" in line:
                                session_id = re.search(r"ses_id=(\w+)", line)
                                if session_id:
                                    session_id = session_id.group(1)
                            if subject_id and session_id:
                                break
                        if subject_id and session_id:
                            inputs = [run_number, most_recent_err_files[run_number], subject_id, session_id]
                            for key, value in zip(error_data.keys(), inputs):
                                error_data[key].append(value)
            else:
                subject_id = None
                session_id = None
                inputs = [run_number, most_recent_err_files[run_number], subject_id, session_id]
                for key, value in zip(error_data.keys(), inputs):
                    error_data[key].append(value)

    
    return error_data

# Match error_data infor with errors_by_string info
def match_error_data(error_data, errors_by_string):
    matched_error_data = {}

    for string, run_numbers in errors_by_string.items():
        for run_number in run_numbers:
            if run_number in error_data['Run_Number']:
                run_index = error_data['Run_Number'].index(run_number)
                error_data_dict = {
                    'Error_Log_Path': error_data['Error_Log_Paths'][run_index],
                    'Subject_ID': error_data['Subject_IDs'][run_index],
                    'Session_ID': error_data['Session_IDs'][run_index]
                }
            if string not in matched_error_data:
                matched_error_data[string] = [error_data_dict]
            else:    
                matched_error_data[string].append(error_data_dict)
    
    return matched_error_data


# Write CSVs for each error !! this is the last part i need to troubleshoot !!
def match_and_print_errors(matched_error_data, error_strings, output_dir, add_error_log_path):
    # Initialize an empty dictionary to store the matched errors.
    matched_errors = {}

    # Iterate through the keys in matched_error_data.
    for error_key in matched_error_data:
        # Iterate through the error_strings dictionary to find a match.
        for error_name, error_value in error_strings.items():
            if error_value in error_key:
                # Append the error data to the matched_errors dictionary.
                if error_name in matched_errors:
                    matched_errors[error_name].extend(matched_error_data[error_key])
                else:
                    matched_errors[error_name] = matched_error_data[error_key]

    # Iterate through the matched_errors and write to CSV files.
    for error_name, error_data_list in matched_errors.items():
        # Define the CSV file name using the associated error name.
        csv_filename = os.path.join(output_dir, f"{error_name}_errors.csv")

        if not add_error_log_path:
                error_data_list = [{key: value for key, value in error_data.items() if key != "Error_Log_Path"} for error_data in error_data_list]

        # Write the data to the CSV file.
        with open(csv_filename, 'w', newline='') as csvfile:
            fieldnames = error_data_list[0].keys()
            #fieldnames = list(fieldnames) + ["Number of subjects:"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write the header row.
            writer.writeheader()

            # Write the error data.
            for error_data in error_data_list:
                writer.writerow(error_data)

            #writer.writerow({"Number of subjects:": len(error_data_list)})    
            
        print(f"CSV file '{csv_filename}' created with {len(error_data_list)} entries.")

if __name__ == "__main__":
    main()

print("done")
