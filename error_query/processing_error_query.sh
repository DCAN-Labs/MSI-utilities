#!/bin/bash
#SBATCH -J error_query
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=10
#SBATCH --cpus-per-task=1
#SBATCH --mem=100gb
#SBATCH --tmp=100gb
#SBATCH -t 3:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=lundq163@umn.edu
#SBATCH -p msismall

#set variables
error_directory=$1
output_path=$2
all_subjects_file=subjects.txt

#create a list that contains the subject ID for each .out log file. Now works for both ABCC and eLABE
for file in $( ls ${error_directory}*.out ); do 
subject=$(cat $file | grep "download: 's3://*/" | awk -F'sub-' '{print $2}' | awk -F'/' '{print $1}' | head -n 1) ;
echo $subject >> ${output_path}/${all_subjects_file} ;
done

#find the unique subject IDs from the previously created .txt file
uniq_subjects=$( cat ${output_path}/${all_subjects_file} | sort | uniq )

#declare empty csv files
time_limit_ids=time_limit_ids.csv
oom_ids=oom_ids.csv
s3_error_ids=s3_error_ids.csv
json_error_ids=json_error_ids.csv
undetermined_error_ids=undetermined_error_ids.csv

#loop through each subject in unique subjects 
for subject in ${uniq_subjects}; do
subject_files=$( grep -m 1 $subject ${error_directory}*.err | cut -d: -f 1 ) #find all the .err files for the current subject
most_recent_file_info=$( ls -lrt $subject_files | tail -n 1 | awk '{print $NF}' ) #determine the most recent .err file
echo $most_recent_file_info #print the most recent .err file in the output log
if grep -l "DUE TO TIME LIMIT" ${most_recent_file_info}; then #determine if error message in quotes is in most recent .err file
	time_limit_errors=$( grep -l "DUE TO TIME LIMIT" ${most_recent_file_info} ) #set the .err file as a variable 
	sub_id_time_limit=$( cat $time_limit_errors | grep "s3://*/" | cut -d/ -f4 | head -n 1 | sed 's/sub-//' ) #grab subject id info from the .err file
	ses_id_time_limit=$( cat $time_limit_errors | grep "s3://*/" | cut -d/ -f5 | head -n 1 | sed 's/ses-//' | sed 's/ ...//' ) #grab session id info from the .err file
	sub_ses_id_time_limit="${sub_id_time_limit},${ses_id_time_limit}" #store sub-id and ses-id info into a comma separated string
	echo $sub_ses_id_time_limit >> ${output_path}/${time_limit_ids} #print subject info string into new line of .csv 
elif grep -l "oom-kill" ${most_recent_file_info}; then #repeat previously outlined steps for a different error message
	oom_errors=$( grep -l "oom-kill" ${most_recent_file_info} )
	sub_id_oom=$( cat $oom_errors | grep "s3://*/" | cut -d/ -f4 | head -n 1 | sed 's/sub-//' )
	ses_id_oom=$( cat $oom_errors | grep "s3://*/" | cut -d/ -f5 | head -n 1 | sed 's/ses-//' | sed 's/ ...//' )
	sub_ses_id_oom="${sub_id_oom},${ses_id_oom}"
	echo $sub_ses_id_oom >> ${output_path}/${oom_ids}
elif grep -l "ERROR: S3 error: 403 (QuotaExceeded)" ${most_recent_file_info}; then #repeat previously outlined steps for a different error message
	s3_errors=$( grep -l "ERROR: S3 error: 403 (QuotaExceeded)" ${most_recent_file_info} )
	sub_id_s3_error=$( cat $s3_errors | grep "s3://*/" | cut -d/ -f4 | head -n 1 | sed 's/sub-//' )
	ses_id_s3_error=$( cat $s3_errors | grep "s3://*/" | cut -d/ -f5 | head -n 1 | sed 's/ses-//' | sed 's/ ...//' )
	sub_ses_id_s3_error="${sub_id_s3_error},${ses_id_s3_error}"
	echo $sub_ses_id_s3_error >> ${output_path}/${s3_error_ids}
elif grep -l "JSONDecodeError" ${most_recent_file_info}; then #repeat previously outlined steps for a different error message
	json_errors=$( grep -l "JSONDecodeError" ${most_recent_file_info} )
	sub_id_json_error=$( cat $json_errors | grep "s3://*/" | cut -d/ -f4 | head -n 1 | sed 's/sub-//' )
	ses_id_json_error=$( cat $json_errors | grep "s3://*/" | cut -d/ -f5 | head -n 1 | sed 's/ses-//' | sed 's/ ...//' )
	sub_ses_id_json_error="${sub_id_json_error},${ses_id_json_error}"
	echo $sub_ses_id_json_error >> ${output_path}/${json_error_ids}
else
	echo "error undetermined for this .err file" #print this message and repeat previously outlined steps if error is still undetermined
	undetermined_errors=${most_recent_file_info}
	sub_id_undetermined_error=$( cat $undetermined_errors | grep "s3://*/" | cut -d/ -f4 | head -n 1 | sed 's/sub-//' )
	ses_id_undetermined_error=$( cat $undetermined_errors | grep "s3://*/" | cut -d/ -f5 | head -n 1 | sed 's/ses-//' | sed 's/ ...//' )
	sub_ses_id_undetermined_error="${sub_id_undetermined_error},${ses_id_undetermined_error}"
	echo $sub_ses_id_undetermined_error >> ${output_path}/${undetermined_error_ids}
fi
done

#remove subject.txt file 
rm ${output_path}/${all_subjects_file}

# may need to fix the counts
time_count=$(wc -w < time_limit_ids.csv)
echo "Total number of time limit errors: $time_count"

oom_count=$(wc -w < oom_ids.csv)
echo "Total number of oom errors: $oom_count"

s3_count=$(wc -w < s3_error_ids.csv)
echo "Total number of s3 sync errors: $s3_count"

json_count=$(wc -w < json_error_ids.csv)
echo "Total number of json decode errors: $json_count"

undetermined_count=$(wc -w < undetermined_error_ids.csv)
echo "Total number of undetermined errors: $undetermined_count"
