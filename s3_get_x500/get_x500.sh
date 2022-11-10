#!/bin/bash

#insert your s3 bucket with full path (ex: s3://your_bucket/)
bucket=$1

x500=$( for uid in $(s3cmd info ${bucket} | grep -oE '([0-9]{5})'); do s3info -u ${uid} | grep 'user ' | cut -d \' -f 2; done )

all_x500s=$(echo $x500 | sed 's| |,|g')

your_x500=$(whoami)

echo $all_x500s,$your_x500
