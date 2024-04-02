import os
import pandas as pd
import sys


#TODO: find a way to account for missing values


#check if more than one error_query output directory path is provided as an argument, along with an output dir for the merged scripts
#TODO: turn into argument parser with a help function
if len(sys.argv) < 3:
    print("Usage: python merge_error_outputs.py /path/to/error/query/results/directory1/ /path/to/error/query/results/directory2/ /path/to/merge/output/dir/")
    sys.exit(1)


#get the directories path from the command-line argument (see above comment)
error_directories = sys.argv[1:len(sys.argv)-1]
output_dir = sys.argv[len(sys.argv)-1]
total_errors_dfs = []


#loop through all files in each error_query output directory provided as an argument
for dir in error_directories:
    #remove backslash from dir path if it is there
    if dir[len(dir)-1] == "/":
        dir = dir[:-1]
        #set dir basename. to be used as dataset_id value
        dir_basename = os.path.basename(dir)
        for filename in os.listdir(dir):
            if filename == "all_err_types.csv":
                filepath = os.path.join(dir, filename)
                df = pd.read_csv(filepath)
                #append dataset_id info
                df["Dataset_ID"] = dir_basename
                #append file creation time info
                timestamp = os.path.getctime(filepath)
                df["Timestamp"] = timestamp
                df = df[['Subject_IDs', 'Session_IDs', 'Errors', 'Dataset_ID', 'Timestamp']]
                df = df.rename(columns={'Errors': 'Error_Type'})
                #append to a list
                total_errors_dfs.append(df)


#function that will take the most recent subject id if there are multiple in the combined dataframe
def duplicate_sub_correct(df):
    df = df.sort_values(['Subject_IDs', 'Timestamp'], ascending=[True,True])
    df = df.drop_duplicates('Subject_IDs', keep='first')
    df = df[['Subject_IDs', 'Session_IDs', 'Error_Type', 'Dataset_ID']]
    return df


#function that will calculate total counts for each error_type in the combined dataframe
def aggregate_counts(df):
    #group by error_type and get count of unique subject_ids
    counts_by_errortype = df.groupby(['Error_Type', 'Dataset_ID'])['Subject_IDs'].nunique().reset_index()
    #create a new dataframe that combined dataset_ids into a list for each error_type
    combined_dataset_ids = counts_by_errortype.groupby('Error_Type')['Dataset_ID'].apply(list).reset_index()
    #group by error_type and sum the subject_ids to get a total count
    total_counts = counts_by_errortype.groupby('Error_Type')['Subject_IDs'].sum().reset_index()
    #merge total count dataframe and the combined dataset ids dataframe
    result = combined_dataset_ids.merge(total_counts, on='Error_Type')
    result.columns = ['Error_Type', 'Dataset_IDs', 'Total_Count']
    return result


#concatenate the dataframes in the list
if total_errors_dfs:
    combined_df = pd.concat(total_errors_dfs, ignore_index=True)
    #run the functions outlined above
    combined_df = duplicate_sub_correct(combined_df)
    counts_df = aggregate_counts(combined_df)
    #save the new dataframes to separate csvs. print to specified output dir
    output_csv = os.path.join(output_dir, "combined_error_types_for_dataset.csv")
    counts_csv = os.path.join(output_dir, "combined_error_counts_for_dataset.csv")
    combined_df.to_csv(output_csv, index=False)
    counts_df.to_csv(counts_csv, index=False)
else:
    print("No data found in the provided directories.")