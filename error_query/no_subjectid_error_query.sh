#!/bin/bash

error_directory=$1
output_path=$2
no_subjectids_file=no_subjectid_errors_runs.csv
echo "Path to their output logs:" >> ${output_path}/${no_subjectids_file}
#list of run numbers
uniq_run_numbers=$( ls $error_directory | awk 'BEGIN { FS = "[_.]" } ; {print $(NF-1)}' | sort | uniq )

#filter list of .err for most recent .err file for each run number
no_subjectid_runs=( )
for run in $uniq_run_numbers; do
most_recent_file_info=$( ls -lt $error_directory*_$run.err | head -n1 )
most_recent=$( echo $most_recent_file_info | awk '{print $NF}' )
echo $most_recent
nosubject=$( grep -L "sub-" $most_recent | cut -d_ -f5 | cut -d. -f1) 

if [[ ! -z "$nosubject" ]]; then
no_subjectid_runs+=$( echo $nosubject, )
echo $most_recent >> ${output_path}/${no_subjectids_file}
fi

echo "Run numbers that have no subject ID in the logs:" $no_subjectid_runs
done

echo "Run numbers that have no subject ID in the logs:" $no_subjectid_runs | sed 's/,$//' | cat - ${output_path}/${no_subjectids_file} >> temp && mv temp ${output_path}/${no_subjectids_file}

#create comma separated list of each type of fail

# /home/rando149/shared/projects/ABCC_year2_derivatives_reprocessing/slurm_abcd-hcp-pipeline_rerun/output_logs/
