"""
Author: rae McCollum
Created: 13 Nov 23
Last Modified: 4 Dec 23 by rae
Purpose: Searches through a BIDS dir (originally used on the ngdr) to look for an empty/non-existent folder. 
"""
import os
import boto3
import argparse

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
    parser.add_argument(
        '--access_key', default= "None",
        help='s3 access key, needed to access s3 bucket. If using MSI, run s3info to find'
    )
    parser.add_argument(
        '--secret_key', default = "None",
        help='s3 secret key, needed to access s3 bucket. If using MSI, run s3info to find'
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        '--folder', action="store_true",
        help='Specify if searching for a empty/non-existent folder'
    )
    group.add_argument(
        '--file', action="store_true",
        help='Specify if searching for missing files'
    )

    return vars(parser.parse_args())


def search_empty_tier1_folders(input_dir, output_file, search_term):
    with open(output_file, 'w') as output:
        # Iterate through top-level "sub-" directories
        for sub_dir in os.listdir(input_dir):
            if sub_dir.startswith("sub-") and os.path.isdir(os.path.join(input_dir, sub_dir)):
                # Iterate through each session subdirectory
                for session_dir in os.listdir(os.path.join(input_dir, sub_dir)):
                    session_path = os.path.join(input_dir, sub_dir, session_dir)

                    # Check if it's a directory and has the searched for subdirectory
                    if os.path.isdir(session_path):
                        func_path = os.path.join(session_path, search_term) 

                        if not os.path.exists(func_path) or not os.listdir(func_path):
                            output.write(f"Subject: {sub_dir}, Session: {session_dir}\n")

def search_tier1_files(input_dir, output_file, search_file):
    with open(output_file, 'w') as output:
        # Iterate through top-level "sub-" directories
        for sub_dir in os.listdir(input_dir):
            if sub_dir.startswith("sub-") and os.path.isdir(os.path.join(input_dir, sub_dir)):
                # Iterate through session subdirectories
                for session_dir in os.listdir(os.path.join(input_dir, sub_dir)):
                    # Check if it's a directory and has a "func" subdirectory
                    if os.path.isdir(session_dir) and os.path.isdir(os.path.join(session_dir,"fmap")):
                        print("Search for file")## SPECIFY HERE WHAT EMPTY FOLDER YOU'RE LOOKING FOR
                        func_path = [1,2,3]
                        func_path2 = [1,2,3]

                        if len(func_path)==0 and len(func_path2) == 0:
                            output.write(f"Subject: {sub_dir}, Session: {session_dir}\n")

def search_empty_s3_folders(input_directory, output_file, search_term, s3):
    print("Search for s3 dir")
    with open(output_file, 'w') as output:
        bucket = s3.Bucket(input_directory)
        objects = bucket.objects.filter(Prefix=search_term)

        if len(list(objects)) > 0:
            print("dir exists")
        else:
            print("dir doesn't exist")

def search_s3_files(input_directory, output_file, search_term, s3):
    print("Search for s3 files")
    with open(output_file, 'w') as output:
        try:
            s3.head_object(Bucket=input_directory, Key=search_term)
            print("This file is not missing")
        except:
            print("This file is missing")

def create_s3_client(host, access_key, secret_key):
    session = boto3.Session()
    client = session.client('s3', endpoint_url=host, aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    return client

def create_s3_bucket(host, access_key, secret_key):
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
                search_s3_files(input_directory, output_txt_file, search_term, s3)
    else:
        if cli_args["folder"]:
            search_empty_tier1_folders(input_directory, output_txt_file, search_term)
        elif cli_args["file"]:
            search_tier1_files(input_directory, output_txt_file, search_term)
