# MSI-utilities

:exclamation: This repository is under construction. :exclamation:

## dir_search_scripts:

These scripts look through BIDS directories to find missing folders/files either on s3 or tier1

dir_search_test_s3.sh 

	Specifiy paths to s3 bucket to be searched and an output file that will output subjects with missing folders.
	Hardcoded, so need to change what year you're searching in and what empty folder you're looking for.

dir_search_test_tier1.sh

	Specifiy directory path and an output file that has the subjects that are missing the folders.
	Hardcoded, so need to change what year you're searching in and what empty folder you're looking for.

find_empty_folders.py

	Specifiy directory path, an output file with the subjects that are missing folders, and which folder
	Can input a tier1 or s3 path, will search based on if "s3://" exists in the directory path
	s3 search still under development
	
## error_query

## find_and_replace

This script locates strings and replaces them with a new string

update_yamls.sh
	
	Specify the directory you're looking in, the string you're replacing, the string you want to replace with, and the file type 
	Update line 15 if you're not looking at .yaml files 
	
## get_max_fairshare

Of the shares in (feczk001, miran045, faird, rando149, smnelson) of which the user is a member, echo the share with the greatest FairShare value. Submitting jobs using the share with highest FairShare minimizes job queueing times and helps balance fairshare usage across all shares. Optionally, use -l or --list to specify a (comma-separated) list of shares to search instead of the default.
	
get_max_fairshare.sh

	Command: ./get_max_fairshare.sh [ -l <list of shares> ]

 More FairShare info: https://dcan-labs-informational-guide.readthedocs.io/en/latest/fairshare
	
## misc_bash_utilities_jacob

remove_duplicate_subs_part1.sh

remove_rows_from_csv.sh

## modify zip

## query_cubids_errors

These scripts perform various filtering on cuBIDS output csvs

create_subject_lists.py

	After running separate-errors-into-csvs.py, run this to create subject lists for each error.
	Specify the directory where the <error_name>-errors.txt files live.
	Will create output txt files with the format <error_name>-subjects.txt

filter-cubids-errors.py 

	When you run this script, it will ask you for your input cuBIDS csv and an output filtered csv.
	You will choose if you want to remove irrelevant errors or only grab lines with a specified error.
	Specify which errors you want to filter by before running the script.
	
filtered_bids_based_on_string.sh

separate-errors-into-csvs.py

	Specify a list of cuBIDS errors that this script will divide out into separate csvs for each error.
	The output txt files will be named <error_name>-errors.txt
	

## s3_get_bucket_policy

Uses [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-example-bucket-policies.html) to get and print out a bucket's policy JSON.

Specifically configured to run with MSI's S3.

Have your aws key and secret ready! They are taken as arguments.


## s3_get_x500

## session_tsv_maker

## sync_verify
