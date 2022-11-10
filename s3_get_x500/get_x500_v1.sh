#!/bin/bash

#insert your s3 bucket with full path (ex: s3://your_bucket/)
bucket=$1

x500=$( for uid in $(s3cmd info ${bucket} | grep -oE '([0-9]{5})'); do s3info -u $uid | grep '@umn.edu' | awk '{print $3}' | cut -d @ -f 1; done )

all_x500s=$(echo $x500 | sed 's| |,|g')


if ( s3cmd info  $bucket | grep -qo "24503" ); then all_x500s=(${all_x500s[@]}",hendr522"); echo $all_x500s; else echo $all_x500s; fi
