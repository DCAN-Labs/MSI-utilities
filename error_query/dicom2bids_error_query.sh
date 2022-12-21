#!/bin/bash

error_directory=$1
output_path=$2
all_subjects_file=subjects.txt

for file in $( ls ${error_directory}/*.out ); do 
subject=$( cat $file | grep "Downloading S3 links from text file" | cut -d/ -f5 ) ;
echo $subject >> ${output_path}/${all_subjects_file} ;
done

uniq_subjects=$( cat ${output_path}/${all_subjects_file} | sort | uniq )

time_limit_subjects=( )
oom_subjects=( )

for subject in ${uniq_subjects}; do
subject_files=$( grep -m 1 $subject ${error_directory}/*.err | cut -d: -f 1 ) ;
most_recent_file_info=$( ls -lrt $subject_files | head -n 1 ) ;
most_recent=$( basename $( echo $most_recent_file_info | awk '{print $NF}' ))
echo $most_recent
time_limit_subjects=$( grep -l "DUE TO TIME LIMIT" ${error_directory}/${most_recent} | cut -d_ -f2 | cut -d. -f1); #make if statement to grab run number if "DUE TO TIME LIMIT" is outputted
oom_subjects=$( grep -l "oom-kill" ${error_directory}/${most_recent} | cut -d_ -f2 | cut -d. -f1 );
done

rm ${output_path}/${all_subjects_file}

for sub in ${time_limit_subjects}; do
echo $sub >> ${output_path}/resubmit_due_to_timelimit.txt
done

for sub in ${oom_subjects}; do
echo $sub >> ${output_path}/resubmit_due_to_oom.txt
done


#print list of subjects to resubmit for each - save as .txt or .csv 
