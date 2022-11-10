
error_directory=$1
#list of run numbers
uniq_run_numbers=$( ls $error_directory | awk 'BEGIN { FS = "[_.]" } ; {print $(NF-1)}' | uniq | sort )

#filter list of .err for most recent .err file for each run number
timelimit_runs=( )
memorylimit_runs=( )
for run in $uniq_run_numbers; do
most_recent_file_info=$( ls -lt $error_directory*_$run.err | head -n1 )
most_recent=$( basename $( echo $most_recent_file_info | awk '{print $NF}' ))
#echo $most_recent
timelimit=$( grep -l "DUE TO TIME LIMIT" $most_recent | cut -d_ -f2 | cut -d. -f1) #make if statement to grab run number if "DUE TO TIME LIMIT" is outputted
memory=$( grep -l "oom-kill" $most_recent | cut -d_ -f2 | cut -d. -f1 )

if [[ ! -z "$memory" ]]; then
memorylimit_runs+=$( echo $memory, )
fi

if [[ ! -z "$timelimit" ]]; then
timelimit_runs+=$( echo $timelimit, )
fi

done

echo "Run numbers to resubmit with more memory:" $memorylimit_runs
echo "Run numbers to resubmit with more time:" $timelimit_runs
#create comma separated list of each type of fail

