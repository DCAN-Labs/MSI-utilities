#!/bin/bash


uids=`seq 10000 1 99999`


for uid in $uids; do
x500=$( s3info info -u $uid | grep "user" | cut -d\' -f2 );
echo $uid,$x500 >> uid_x500.csv; done
