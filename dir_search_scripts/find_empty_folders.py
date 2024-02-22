"""
Author: rae McCollum
Created: 13 Nov 23
Last Modified: 13 Dec 23 by rae
Purpose: Searches through a BIDS dir (originally used on the ngdr) to look for an empty/non-existent folder or files. 
"""
import os
import csv
import boto3
import argparse
from glob import glob

def _cli():
    """
    :return: Dictionary with all validated command-line arguments from the user
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input_dir', required=True, 
        help='Path to a BIDS valid subject directory, either a tier1 path or an s3 bucket'
    )
    parser.add_argument(
        '--output_file', required=True, 
        help='Path to the file which will contain the subjects and sessions that are missing'
    )
    parser.add_argument(
        '--search', required=True,
        help='The file or folder that you are searching for. You will also need to specify if it is a folder or a file'
    )
    parser.add_argument(
        '--host', default= 'https://s3.msi.umn.edu', type=str,
        help='s3 host url, defaults to s3.msi.umn.edu for MSI users'
    )
    ## TODO: Parse a config file for secret and access keys instead of providing via command line 
    parser.add_argument(
        '--access_key', default= "None",
        help='s3 access key, needed to access s3 bucket. If using MSI, run s3info to find'
    )
    parser.add_argument(
        '--secret_key', default = "None",
        help='s3 secret key, needed to access s3 bucket. If using MSI, run s3info to find'
    )
    parser.add_argument(
        '--sub_list',
        help='Path to a file with the list of subjects in the s3 bucket with an expected format of "sub-ID" with one subject per line. Must be a txt or csv file'
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        '--folder', action="store_true",
        help='Specify if searching for a empty/non-existent folder'
    )
    group.add_argument(
        '--file', action="store_true",
        help='Specify if searching for missing files' ## relative path inside session folder (anat/fmap/func/dwi, or derivatives, etc)
    )

    return vars(parser.parse_args())

def grab_sub_dirs(input_dir):
    # Returns list of top level subject directories in input_dir
    sub_dirs = []
    for dir in os.listdir(input_dir): ## change to be scandir (can check below checks quicker)
        if dir.startswith("sub-") and os.path.isdir(os.path.join(input_dir, dir)):
            sub_dirs.append(dir)
    return dir

def check_for_ses(sub_dir):
    # Returns true if there are session folders in a subject directory 
    return bool(glob(os.path.join(sub_dir, "ses-*")))

def search_tier1(input_dir, output_file, search_file):
    sub_dirs = grab_sub_dirs(input_dir)
    missing_info = [] 
    # Iterate through top-level "sub-" directories
    for sub in sub_dirs:
        sub_dir = os.path.join(input_dir, sub)
        ses_exist = check_for_ses(sub_dir)
        if ses_exist:
            for session_dir in os.listdir(sub_dir):
                file_path = os.path.join(input_dir, sub, session_dir, search_file)
                if not os.path.exists(file_path):
                    missing_info.append(f"{sub},{session_dir}")
        elif not ses_exist:
            file_path = os.path.join(input_dir, sub, search_file)
            if not os.path.exists(file_path):
                missing_info.append(sub)
    with open(output_file, 'w') as output: 
        output.write("\n".join(missing_info))

def search_empty_s3_folders(input_directory, output_file, search_term, s3): ## Hasn't been tested, unsure of functionality
    print("Search for s3 dir")
    with open(output_file, 'w') as output:
        bucket = s3.Bucket(input_directory)
        objects = bucket.objects.filter(Prefix=search_term)

        if len(list(objects)) > 0:
            print("dir exists")
        else:
            print("dir doesn't exist")

def search_s3_files(input_directory, search_term, s3, subject): ## Still developing, works when given a subject list
    print(f"Search s3 for the file for subject: {subject}")

    raw_bucket_name = input_directory.split('/')[2] ## Maybe figure out a better way to do this
    objects = s3.list_objects(Bucket=raw_bucket_name, Prefix=subject)
    contents = objects["Contents"]
    found_term = False
    for obj in contents:
        key = obj["Key"]
        if search_term in key:
            found_term = True
            break
    return found_term

def output_missing_subjects(output_file, subject):
    # Write subject with missing term to file 
    with open(output_file, 'a+') as output:
        output.write(subject)

def get_subjects(subject_list_file):
    # Extract subject IDs from text file
    if subject_list_file[-3:] == "txt":
        with open(subject_list_file, 'r') as file:
            subject_ids = [line.strip() for line in file.readlines()]
    # Extract subject IDs from csv  
    elif subject_list_file[-3:] == "csv":
        with open(subject_list_file, 'r') as file:
            reader = csv.reader(file)
            subject_ids = [row[0].strip() for row in reader]

    return subject_ids

def create_s3_client(host, access_key, secret_key):
    # Create s3 client to access bucket 
    session = boto3.Session()
    client = session.client('s3', endpoint_url=host, aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    return client

def create_s3_bucket(host, access_key, secret_key): ## Same as above, I think this will need to be different for bucket searching function
    session = boto3.Session()
    client = session.client('s3', endpoint_url=host, aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    return client

if __name__ == '__main__':
    cli_args = _cli()
    input_directory = cli_args["input_dir"]
    output_txt_file = cli_args["output_file"]
    search_term = cli_args["search"]
    host = cli_args["host"]
    access_key = cli_args["access_key"]
    secret_key = cli_args["secret_key"]
    sub_list = cli_args["sub_list"]

    if not cli_args["folder"] and not cli_args["file"]:
        raise ValueError("You need to specify if you're searching for a folder or file with the --folder or --file flag")
    
    if "s3://" in input_directory:
        if access_key == "None" or secret_key == "None":
            raise ValueError("You are trying to search a s3 bucket but have not provided your access or secret key. Please specify these values. See the help message for more info.")
        else:
            s3 = create_s3_client(host, access_key, secret_key)
            if cli_args["folder"]:
                search_empty_s3_folders(input_directory, output_txt_file, search_term, s3)
            elif cli_args["file"]:
                subjects = get_subjects(sub_list)
                for sub in subjects:
                    found_term = search_s3_files(input_directory, search_term, s3, sub)
                    if not found_term:
                        output_missing_subjects(output_txt_file, sub)
    else:
        search_tier1(input_directory, output_txt_file, search_term)
