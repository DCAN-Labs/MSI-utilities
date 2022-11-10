
declare -A error_files

for file in $( ls *.out ); do 
subject=$( cat $file | grep "Downloading S3 links from text file" | cut -d/ -f5 )
error_files+=$( ["$file"]="$subject" )
declare -p error_files
done

#make it skip empty subjects
#choose most recent file for each subject
#search for time out
#search for oom-kill
#print list of subjects to resubmit for each - save as .txt or .csv 