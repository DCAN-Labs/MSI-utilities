#!/usr/bin/env python3

"""
Created by Jacob Lundquist lundq163@umn.edu
Updated by Greg Conan gregmconan@gmail.com on 2024-03-20
"""
# Standard imports
import argparse
from argparse import RawTextHelpFormatter
import os
import pdb
import sys
                    
# Local custom imports
from DatasetErrFiles import DatasetErrFiles
from utilities import (valid_output_dir, valid_readable_dir,
                       valid_readable_file, valid_readable_json_content)


def main():
    cli_args = _cli()

    # parse through the output_logs_dir and get all error files' info
    err_files = DatasetErrFiles(**cli_args)

    # print the identified information in a csv for each error
    err_files.save_and_print_all_errs()


def _cli():
    # Get command-line input arguments
    # set the input variables using argument parser
    # change arguments to dashes from underscores (done automatically if 
    # there's only one argument with double dashes)
    # store true means default will always be False 
    DIR_SCRIPT = os.path.dirname(sys.argv[0])
    DEFAULT_ERR_STR_JSON = os.path.join(DIR_SCRIPT, "err_strings.json")
    DEFAULT_OUT_DIR = os.getcwd()
    parser = argparse.ArgumentParser(
        description="Review error logs and extract relevant error "
                    "information from each .err file.",
        formatter_class=RawTextHelpFormatter
    )

    # Required: Path to directory containing output logs files
    parser.add_argument("-l", "-logs", "--logs-dir", "--output-logs-dir",
                        dest="logs_dir", required=True,
                        type=valid_readable_dir,
                        help="Required. Path to the output_logs directory.")
    
    # Optional arguments
    parser.add_argument("-del", "--delete", "--delete-logs",
                        dest="delete", action="store_true",
                        help="Optional. Include this flag to remove old "
                             ".err and .out files found that may no longer "
                             "be necessary.")
    parser.add_argument("-e", "-err", "--err-strings",
                        dest="err_strings", type=valid_readable_json_content,
                        default=DEFAULT_ERR_STR_JSON,
                        help="Optional. Valid path to readable .JSON file "
                             "mapping error names to error strings (i.e. to "
                             "the strings that, when present in a log file, "
                             "indicate that an error by than name occurred)."
                             "By default, this script will try to read that "
                             f"from '{DEFAULT_ERR_STR_JSON}'. If no readable "
                             ".JSON file exists at that path, then you need "
                             "to include a different one as this argument.")
    parser.add_argument("-id", "-ID", "--dataset-id",
                        help="Identification naming the dataset that error " 
                             "querying is being run on.")
    parser.add_argument("-o", "-out", "--output", "--output-dir",
                        dest="output_dir", type=valid_output_dir,
                        default=DEFAULT_OUT_DIR,
                        help="Optional. Path to the directory where the .CSV "
                             "files created by this script will be saved. If "
                             "no directory exists at this path yet, then "
                             "this script will create one. By default, if "
                             "this argument is not included, the script will "
                             f"save .CSV files here: '{DEFAULT_OUT_DIR}'")
    parser.add_argument("-p", "-path", "--add-path", "--add-err-log-path",
                        dest="add_err_log_path", action="store_true",
                        help="Optional. Include this flag to include the "
                             ".err file path in the 'Error_Log_Path' column "
                             "of the .CSV files that this script creates.")
    parser.add_argument("-r", "-runs", "--run-dir", "--run-files-dir",
                        dest="run_dir", type=valid_readable_dir,
                        help="Optional. Path to the run_files directory.\n"
                             "Recommended to use if there could be missing "
                             "subject information in the .err file.\n"
                             "IMPORTANT: if run files in this directory were "
                             "remade since running the processing jobs,\n"
                             "this could result in the incorrect subject "
                             "information being matched to the .err log.\n"
                             "Suggested usage is to only use this flag after "
                             "the first round of processing.")
    parser.add_argument("-s", "-sub", "--subjects", "--sub-ids-csv",
                        dest="sub_IDs_CSV", type=valid_readable_file,
                        help="Optional. Path to existing .csv file which "
                             "contains specific subject_id,session_id pairs "
                             "to search for in each log file.")
    return vars(parser.parse_args())
    

if __name__ == "__main__":
    main()
