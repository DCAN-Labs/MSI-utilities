#!/bin/bash
# author: Thomas Madison (tmadison)
# description: Of the shares in (feczk001, miran045, faird, rando149, smnelson) of which the user is a member, echo the share with the greatest fairshare value. Optionally, use -l or --list to specify a (comma-separated) list of shares to search instead of the default.

shares="feczk001,miran045,faird,rando149,smnelson"

while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -l|--list)
        shares="$2"
        shift
        shift
        ;;
        *)
        echo "Unknown option: $1"
        exit 1
        ;;
    esac
done

# Echo the share with the greatest fairshare value
max_share=$(for n in $(groups); do
    for share in $(echo $shares | tr ',' ' '); do
        if [[ "$n" == "$share" ]]; then
            echo -n ${n},
        fi
    done
done | sshare -A $(cat) | sort -k 7 -nr | awk 'NR==1{print $1}')

echo $max_share
