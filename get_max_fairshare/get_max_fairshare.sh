#!/bin/bash

# of the shares in (feczk001, miran045, faird, rando149, smnelson) of which the user is a member, echo the share with the greatest fairshare value

max_share=$(for n in $(groups); do case "$n" in (feczk001 | miran045 | faird | rando149 | smnelson) echo -n ${n},; esac; done |  sshare -A $(cat) | sort -k 7 -nr | awk 'NR==1{print $1'})

echo $max_share