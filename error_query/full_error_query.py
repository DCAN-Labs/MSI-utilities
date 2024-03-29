# Brief outline of the scripts steps:
#   1. set the variables: 
#       a. output_logs_dir is a path to the output_logs directory
#       b. run_files_dir is a path to the run_files directory, used to find the associated sub/ses information for each unique run file (if necessary)
#       c. output_path will be a path to a directory where the csvs will go
#       d. sub_ids_csv is a path to a list of subject ids
#       e. add_error_log_path is a boolean that will add a path to the most recent error log for each subject in the output
#       f. error_strings allow for new strings to be added to a default dictionary of strings
#   2. parse through the output_logs_dir and create a unique list of all the run numbers
#   3. find the most recent .err file associated with each unique run number
#   4. read each error file and find certain error strings, then match information with run number (or sub_id, if using csv input) identifier 
#   5. using identifier, find subject_id and session_id for each associated error file;
#      if subject_id and session_id not found within the .err file, extract info from the associated run file in the run_files directory
#   6. return csvs for each error that contain the associated subject_id and session_id, and the path to the error log that contains the error, if desired

# TODO:
#   - provide a catch for error logs that are missing subject and session information
#   - add no_sub_id_err_files to its own csv
#   - test out ability to add in other error strings
#   - test on a subset of BIDS conversion error logs
#   - need to consolidate find_subject_session_ids function 
#   - further edit exception in match_error_data function
#   - make sure either run files dir or subject list is a required input 


# import necessary modules
import os
from glob import glob
import pandas as pd
import pdb
import re
import csv
import argparse
from argparse import RawTextHelpFormatter

# default dictionary of error strings to search for
error_strings = {
    "undetermined_or_no": " ",
    "prefreesurfer":"Exception: error caught during stage: PreFreeSurfer",
    "freesurfer": "Exception: error caught during stage: FreeSurfer",
    "postfreesurfer": "Exception: error caught during stage: PostFreeSurfer",
    "fmrivolume": "Exception: error caught during stage: FMRIVolume",
    "fmrisurface": "Exception: error caught during stage: FMRISurface",
    "dcanboldprocessing": "Exception: error caught during stage: DCANBOLDProcessing",
    "executivesummary": "Exception: error caught during stage: ExecutiveSummary",
    "customclean": "Exception: error caught during stage: CustomClean",  
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
    # set the input variables using argument parser
    # change arguments to dashes from underscores
    # store true means default will always be False 
    parser = argparse.ArgumentParser(description="Review error logs and extract relevant error information from each .err file.", formatter_class=RawTextHelpFormatter)
    parser.add_argument("-l", "--output_logs_dir", dest="output_logs_dir", required=True,
                        help="Required. Path to the output_logs directory."
                        )
    parser.add_argument("-r", "--run_files_dir", dest="run_files_dir", default="", required=False,
                        help="Optional. Path to the run_files directory.\n"
                            "Recommended to use if there could be missing subject information in the .err file.\n"
                            "IMPORTANT: if run files in this directory have been remade since running the processing jobs,\n"
                            "this could result in the incorrect subject information being matched to the .err log.\n"
                            "Suggestion is to only use this flag after first round of processing."
                        )
    parser.add_argument("-o", "--output_dir", dest="output_dir", required=True,
                        help="Required. Path to the directory where the CSVs will be saved."
                        )
    parser.add_argument("-s", "--sub_ids_csv", dest="sub_ids_csv", default="", required=False,
                         help="Optional. Path to a csv containing specific subject_id,session_id pair to search for in each log file."
                        )
    parser.add_argument("-p", "--add_error_log_path", dest="add_error_log_path", action="store_true", default = False, required=False,
                        help="Optional. Include the 'Error_Log_Path' in the CSVs for each .err file."
                        )
    #parser.add_argument("-remove", "--remove_old_log_files", dest="remove_old_log_files", action="store_true", default = False, required=False,
    #                    help="Optional. Remove old log files that may no longer be necessary.")
    parser.add_argument("-e", "--error_strings", dest="error_strings", nargs="+", default=error_strings, required=False,
                        help="Optional arg to add in different error strings to dictionary of strings to search for. Current default dictionary:\n"
                            "'undetermined_or_no': ' ',\n"
                            "'prefreesurfer':'Exception: error caught during stage: PreFreeSurfer',\n"
                            "'freesurfer': 'Exception: error caught during stage: FreeSurfer',\n"
                            "'postfreesurfer': 'Exception: error caught during stage: PostFreeSurfer',\n"
                            "'fmrivolume': 'Exception: error caught during stage: FMRIVolume',\n"
                            "'fmrisurface': 'Exception: error caught during stage: FMRISurface',\n"
                            "'dcanboldprocessing': 'Exception: error caught during stage: DCANBOLDProcessing',\n"
                            "'executivesummary': 'Exception: error caught during stage: ExecutiveSummary',\n"
                            "'customclean': 'Exception: error caught during stage: CustomClean',\n"  
                            "'time_limit': 'DUE TO TIME LIMIT',\n"
                            "'oom': 'oom-kill',\n"
                            "'assertion_error': 'AssertionError',\n"
                            "'key_error': 'KeyError',\n"
                            "'index_error': 'IndexError',\n"
                            "'s3_credentials': 'An error occurred fetching S3 credentials',\n"
                            "'s3_quota': 'ERROR: S3 error: 403 (QuotaExceeded)',\n"
                            "'no_response_status': 'ERROR: Cannot retrieve any response status before encountering an EPIPE or ECONNRESET exception',\n"
                            "'upload_failed': 'WARNING: Upload failed:',\n"
                            "'unable_to_copy': 'WARNING: Unable to remote copy files',\n"
                            "'ssl_verification': 'ERROR: SSL certificate verification failure:',\n"
                            "'connection_reset': 'error: [Errno 104] Connection reset by peer'\n"
                            "\n"
                            "In order to add a new error string to search for, use this format:\n"
                            "'csv_title': 'string to search for'\n"
                        )
    args = parser.parse_args()

    # parse through the output_logs_dir and create a unique list of all the run numbers
    run_numbers = get_run_numbers(args.output_logs_dir)
    # find the most recent .err file associated with each unique run number
    if args.sub_ids_csv == "":
        most_recent_err_files,no_sub_id_err_files = get_most_recent_err_files(args.output_logs_dir, run_numbers)
    else: 
        most_recent_err_files,no_sub_id_err_files = get_most_recent_err_files_from_id(args.output_logs_dir, args.sub_ids_csv)
    # read each error file and find certain error strings, then match information with run number identifier
    errors_by_string, run_numbers_with_error, run_numbers_without_error = find_errors(args.error_strings, most_recent_err_files)
    # using run number identifier, find subject_id and session_id for each associated error file
    error_data = find_subject_session_ids(args.run_files_dir, run_numbers_with_error, run_numbers_without_error, most_recent_err_files)
    # match the error data for each error string
    matched_error_data = match_error_data(error_data, errors_by_string)
    # print the identified information in a csv for each error
    match_and_print_errors(no_sub_id_err_files,matched_error_data, error_strings, args.output_dir, args.add_error_log_path)

# create a unique list of run numbers from output_logs directory
def get_run_numbers(output_logs_dir):
    run_numbers = set()
    for root, _, files in os.walk(output_logs_dir):
        for file in files:
            if file.endswith(".err"):
                run_number = re.search(r"_(\d+)\.err", file)
                if run_number:
                    run_numbers.add(run_number.group(1))
    return run_numbers

# find the most recent .err file for each unique run number
def get_most_recent_err_files(output_logs_dir, run_numbers):
    most_recent_err_files = {}
    for run_number in run_numbers:
        err_files = glob(os.path.join(output_logs_dir, f"*_{run_number}.err"))
        if err_files:
            most_recent_err_files[run_number] = max(err_files, key=os.path.getctime)
    return most_recent_err_files


# if using subject id list, find most recent err file
def get_most_recent_err_files_from_id(output_logs_dir, sub_ids_csv):
    # Get all error file paths
    err_files_df = pd.DataFrame({
        "err_file_path": glob(os.path.join(output_logs_dir, f"*.err"))
    })

    # Patterns to find subject and session IDs
    find_subj = re.compile(r"(sub-NDARINV.{8})")
    find_ses = re.compile(r"(ses-.*Arm[0-9]{1})")

    # Get each error file's subject and session ID
    COLS_ID = ["subject", "session"]
    err_files_df[COLS_ID] = err_files_df["err_file_path"].apply(
        lambda fpath: get_sub_and_ses_IDs(fpath, find_subj, find_ses)
    ).values.tolist()

    # Check how recently each error file was [created? updated?]
    err_files_df["recency"] = err_files_df["err_file_path"].apply(os.path.getctime)

    most_recent_err_files = remove_err_files_and_get_most_recent_v1(
        sub_ids_csv, err_files_df, COLS_ID
    )
    # most_recent_err_files = remove_err_files_and_get_most_recent_v2(sub_ids_csv, err_files_df)

    # Get all error files that don't include a subject ID
    no_sub_id_err_files = err_files_df[err_files_df[COLS_ID[0]].isna()
                                       ]["err_file_path"].values.tolist()
    
    return most_recent_err_files, no_sub_id_err_files


def remove_err_files_and_get_most_recent_v1(sub_ids_csv, err_files_df, COLS_ID):
    most_recent_err_files = dict()
    col_sub, col_ses = COLS_ID
    with open(sub_ids_csv, 'r') as csv_file:
        for line in csv_file: 
            # Get subject and session from .csv file
            sub_id, ses_id = line.strip().split(",")

            # Get all error files for that subject and session
            sub_ses_df = err_files_df[(err_files_df[col_sub] == f"sub-{sub_id}") &
                                      (err_files_df[col_ses] == f"ses-{ses_id}")]
            
            if not sub_ses_df.empty:  # Get the most recent error file and delete the rest
                is_most_recent = (sub_ses_df["recency"] == sub_ses_df["recency"].max())
                most_recent_row = sub_ses_df[is_most_recent].iloc[0]
                most_recent_err_files[most_recent_row.get(col_sub)
                                      ] = most_recent_row.get("err_file_path")
                sub_ses_df[~is_most_recent]["err_file_path"].apply(remove_err_and_log_files)
    return most_recent_err_files


def remove_err_files_and_get_most_recent_v2(sub_ids_csv, err_files_df, COLS_ID=None):
    csv_df = pd.read_csv(sub_ids_csv)
    if not COLS_ID:
        COLS_ID = csv_df.columns.values.tolist()
    for col_name in COLS_ID:
        csv_df[col_name] = f"{col_name[:3]}-" + csv_df[col_name]
    intersection = err_files_df.merge(csv_df, how="inner", on=COLS_ID)
    return intersection.groupby(COLS_ID).apply(
        get_most_recent_err_file_and_remove_others
    ).values.tolist()


def get_most_recent_err_file_and_remove_others(sub_ses_df: pd.DataFrame) -> str:
    # Get the most recent error file and delete the rest
    most_recent_err_file = None
    if not sub_ses_df.empty:  
        is_most_recent = (sub_ses_df["recency"] == sub_ses_df["recency"].max())
        most_recent_row = sub_ses_df[is_most_recent].iloc[0]
        sub_ses_df[~is_most_recent]["err_file_path"].apply(remove_err_and_log_files)
        most_recent_err_file = most_recent_row.get("err_file_path")
    return most_recent_err_file


def get_sub_and_ses_IDs(err_file_path: str, find_subj, find_ses):
    # Get subject and session IDs from the content of an error file, and if
    # one is missing, return that one as None instead
    with open(err_file_path, 'r') as file:
        file_content = file.read()
    return [get_sub_or_ses_ID_in(find_subj, file_content),
            get_sub_or_ses_ID_in(find_ses, file_content)]


def get_sub_or_ses_ID_in(pattern, str_to_find_ID_in):
    # Get the subject- or session-ID from a string by using the Regex pattern
    matched_ID = re.search(pattern, str_to_find_ID_in)
    if matched_ID:
        matched_ID = matched_ID.group()
    return matched_ID


def remove_err_and_log_files(err_file_path):
    for each_log_file in (err_file_path, err_file_path.replace(".err", ".out")):
        print(each_log_file)
        if os.path.exists(each_log_file):
            os.remove(each_log_file)


# if using subject id list, find most recent err file
def get_most_recent_err_files_from_id_old(output_logs_dir, sub_ids_csv):
    most_recent_err_files = {}
    no_sub_id_err_files = [] 
    err_files = glob(os.path.join(output_logs_dir, f"*.err"))
    for err_file in err_files:
        with open(err_file, 'r') as file:
            file_content = file.read()
        with open(sub_ids_csv, 'r') as csv_file:
            sub_id_found=False
            for line in csv_file:
                sub_id,ses_id = line.strip().split(",")
                sub_match = re.search(sub_id, file_content)
                ses_match = re.search(ses_id, file_content)
                if sub_match and ses_match:
                    sub_id_found=True
                    if sub_id not in most_recent_err_files or os.path.getctime(err_file) > os.path.getctime(most_recent_err_files[sub_id]):
                        most_recent_err_files[sub_id] = err_file
                        #err_files is all of the err_files instead of subject specific
                        err_files.remove(most_recent_err_files[sub_id]) 
                        for to_delete in err_files:
                            if to_delete:
                                for each_log_file in (to_delete, to_delete.replace(".err", ".out")):
                                    print(each_log_file)
                                    if os.path.exists(each_log_file):
                                        os.remove(each_log_file)
                        break
            if not sub_id_found:
                no_sub_id_err_files.append(err_file)

    
    return most_recent_err_files, no_sub_id_err_files

# read error files and look for specific error strings
def find_errors(error_strings, most_recent_err_files):
    error_strings_list = list(error_strings.values())
    
    errors_by_string = {error_string: [] for error_string in error_strings_list} 
    run_numbers_with_error = set()
    run_numbers_without_error = set()
    
    for run_number, err_file in most_recent_err_files.items():
        with open(err_file, 'r') as err_file:
            content = err_file.read()
            # hard coded to catch for undetermined errors 
            # TODO: separate non error list and error string list
            for error_string in error_strings_list[1:]:
                if error_string in content:
                    errors_by_string[error_string].append(run_number)
                    run_numbers_with_error.add(run_number)
                    break
            for error_string in error_strings_list[:1]:
                if run_number not in run_numbers_with_error:
                    errors_by_string[error_string].append(run_number)
                    run_numbers_without_error.add(run_number)
    
    return errors_by_string, run_numbers_with_error, run_numbers_without_error

# find subject_id and session_id for each run number within the associated error file
# TODO: for loop in code is being repeated, need to consolidate 
# STEPS: make code within for loops its own function, call that new function within find_subject_session_ids
def find_subject_session_ids(run_files_dir, run_numbers_with_error, run_numbers_without_error, most_recent_err_files):
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
                # if subject_id and session_id not found, extract info from the associated run file in the run_files directory 
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

    for run_number in run_numbers_without_error:
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
                # if subject_id and session_id not found, extract info from the associated run file in the run_files directory 
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

# match error_data info with errors_by_string info
def match_error_data(error_data, errors_by_string):
    matched_error_data = {}

    for string, run_numbers in errors_by_string.items():
        for run_number in run_numbers:
            try:
                if run_number in error_data['Run_Number'] and string not in matched_error_data:
                    run_index = error_data['Run_Number'].index(run_number)
                    error_data_dict = {
                        'Error_Log_Path': error_data['Error_Log_Paths'][run_index],
                        'Subject_ID': error_data['Subject_IDs'][run_index],
                        'Session_ID': error_data['Session_IDs'][run_index]
                    }
                    matched_error_data[string] = [error_data_dict]
                else:   
                    run_index = error_data['Run_Number'].index(run_number)
                    error_data_dict = {
                        'Error_Log_Path': error_data['Error_Log_Paths'][run_index],
                        'Subject_ID': error_data['Subject_IDs'][run_index],
                        'Session_ID': error_data['Session_IDs'][run_index]
                    } 
                    matched_error_data[string].append(error_data_dict)
            # TODO: further edit this exception
            except ValueError as e:
                if "is not in list" in str(e):
                    print("Unmatchable error logs! run file may be missing from the run_files dir")
                    pass
                #elif e:
                #    pass
                else:
                    raise

    return matched_error_data


# write csvs for each error
def match_and_print_errors(no_sub_id_err_files,matched_error_data, error_strings, output_dir, add_error_log_path):
    matched_errors = {}

    for error_key in matched_error_data.keys():
        for error_name, error_value in error_strings.items():
            if error_value in error_key:
                if error_name not in matched_errors.keys():
                    matched_errors[error_name] = matched_error_data[error_key]

    for error_name, error_data_list in matched_errors.items():
        csv_filename = os.path.join(output_dir, f"{error_name}_errors.csv")

        if not add_error_log_path:
                error_data_list = [{key: value for key, value in error_data.items() if key != "Error_Log_Path"} for error_data in error_data_list]

        with open(csv_filename, 'w', newline='') as csvfile:
            fieldnames = error_data_list[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for error_data in error_data_list:
                writer.writerow(error_data)            
        print(f"CSV file '{csv_filename}' created with {len(error_data_list)} entries.")

    no_sub_id_csv = os.path.join(output_dir, f"no_sub_id_errors.csv")
    with open (no_sub_id_csv, 'w', newline='') as csvfile:
        fieldnames = ['paths']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for line in no_sub_id_err_files:
            writer.writerow({'paths': line})
    print(f"CSV file '{no_sub_id_csv}' created with {len(no_sub_id_err_files)} entries.")

if __name__ == "__main__":
    main()
