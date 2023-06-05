#!/bin/bash

# Function to verify the existence of a file in S3
verify_s3_file() {
    local s3_path=$1
    s3cmd info "$s3_path" >/dev/null 2>&1
    return $?
}

# Function to verify the existence of a file on the local disk
verify_local_file() {
    local local_path=$1
    [ -e "$local_path" ]
    return $?
}

# Function to verify the existence of a directory in S3
verify_s3_directory() {
    local s3_path=$1
    s3cmd ls "$s3_path" >/dev/null 2>&1
    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        s3cmd ls "$s3_path"/* >/dev/null 2>&1
        exit_code=$?
    fi
    return $exit_code
}

# Function to verify the sync status of a file or directory
verify_sync_status() {
    local source_path=$1
    local dest_path=$2
    local use_checksum=$3

    # Verify if the source and destination paths exist
    if [[ ! -e $source_path ]]; then
        echo "Failed to sync: Source path does not exist"
        return
    fi

    if [[ $dest_path == s3://* ]]; then
        if ! verify_s3_directory "$dest_path"; then
            echo "Failed to sync: Destination bucket does not exist"
            return
        else
            echo "Destination bucket exists: $dest_path"
        fi
    else
        if [[ ! -e $dest_path ]]; then
            echo "Failed to sync: Destination path does not exist"
            return
        fi

        # Use rsync to compare the source and destination directories or files
        local rsync_command=("rsync" "-a" "--dry-run" "--itemize-changes")
        if [[ $use_checksum == true ]]; then
            rsync_command+=("--checksum")
        fi
        rsync_command+=("$source_path/" "$dest_path/")

        if "${rsync_command[@]}" | grep -q "^[^d]"; then
            echo "Failed to sync: $source_path -> $dest_path"
            return
        fi

        echo "Synced: $source_path -> $dest_path"

        # Compare file contents if checksum is specified
        if [[ $use_checksum == true ]]; then
            find "$source_path" -type f -exec shasum {} + | while read -r source_file_sum source_file; do
                local dest_file="${source_file/$source_path/$dest_path}"
                if verify_s3_file "$dest_file" && verify_local_file "$source_file"; then
                    local source_file_sum_new=$(shasum "$source_file" | awk '{ print $1 }')
                    local dest_file_sum=$(s3cmd info "$dest_file" | grep "ETag:" | awk '{ print $2 }')
                    if [[ $source_file_sum_new != $dest_file_sum ]]; then
                        echo "File differs: $source_file -> $dest_file"
                    fi
                fi
            done
        fi
    fi
}

# Function to verify sync status for multiple directories or files listed in a text file
verify_multiple_sync_status() {
    local list_file=$1
    local dest_path=$2

    if [[ -z $list_file ]]; then
        verify_sync_status "$source_path" "$dest_path" "$use_checksum"
    else
        while IFS= read -r path; do
            verify_sync_status "$path" "$dest_path" "$use_checksum"
        done < "$list_file"
    fi
}

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    key="$1"

    case $key in
    --source-path)
        source_path="$2"
        shift
        shift
        ;;
    --dest-path)
        dest_path="$2"
        shift
        shift
        ;;
    --dry-run)
        dry_run=true
        shift
        ;;
    --verify-list)
        verify_list_file="$2"
        shift
        shift
        ;;
    --checksum)
        use_checksum=true
        shift
        ;;
    *)
        echo "Unknown option: $1"
        exit 1
        ;;
    esac
done

# Check if required arguments are provided
if [[ -z $source_path || -z $dest_path ]]; then
    echo "Missing required arguments. Usage: $0 --source-path <source_path> --dest-path <dest_path> [--dry-run] [--verify-list <list_file>] [--checksum]"
    exit 1
fi

# Run 'rsync' command with the user-provided source and destination
if [ "$dry_run" = true ]; then
    echo "Performing a dry run without syncing..."
elif [ -n "$verify_list_file" ]; then
    verify_multiple_sync_status "$verify_list_file" "$dest_path"
else
    verify_sync_status "$source_path" "$dest_path" "$use_checksum"
fi
