import os
import zipfile


def display_zip_tree(zip_path):
    # Open the zip file for reading
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        print("Internal directory tree of the zip file:")
        for info in zip_file.infolist():
            print(info.filename)


def add_to_zip(file_or_dir, zip_path, target_dir=None, top_level_dir=None):
    # Get the absolute path of the file or dir
    abs_path = os.path.abspath(file_or_dir)

    # Create a ZipFile object with write permission
    with zipfile.ZipFile(zip_path, 'a') as zip_file:
        # Determine the target dir inside the zip file
        if target_dir is None:
            target_dir = ''

        # Determine the arcname (path inside the zip file)
        if top_level_dir:
            arcname = os.path.join(top_level_dir, os.path.basename(abs_path))
        else:
            arcname = os.path.basename(abs_path)

        # Add the file or dir to the zip file
        zip_file.write(abs_path, arcname=arcname)


def remove_from_zip(file_or_dir, zip_path):
    # Create a temporary zip file
    temp_zip = zip_path + ".temp"

    # Get the absolute path of the file or dir
    abs_path = os.path.abspath(file_or_dir)

    # Create a ZipFile object with write permission
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        # Open the temporary zip file for writing
        with zipfile.ZipFile(temp_zip, 'w') as temp_zip_file:
            # Iterate over the files in the original zip file
            for item in zip_file.infolist():
                # If the file or dir is not in the zip file, add it to the temporary zip file
                if item.filename != os.path.relpath(abs_path, os.path.dirname(zip_path)):
                    temp_zip_file.writestr(item, zip_file.read(item.filename))

    # Replace the original zip file with the temporary zip file
    os.replace(temp_zip, zip_path)


# Parse command line arguments
import argparse

parser = argparse.ArgumentParser(description='Add or remove a specified file or dir from a zip file.')
parser.add_argument('zip_path', type=str, help='Path of the zip file')
parser.add_argument('--add', type=str, default=None,
                    help='Path to the file or dir to be added to the zip file')
parser.add_argument('--remove', type=str, default=None,
                    help='Path to the file or dir to be removed from the zip file')
parser.add_argument('--target_dir', type=str, default=None,
                    help='Path inside the zip file where the file or dir will be placed')
parser.add_argument('--top_level_dir', type=str, default=None,
                    help='Top-level dir inside the zip file')

args = parser.parse_args()

zip_path = args.zip_path
file_or_dir = args.add
target_dir = args.target_dir
top_level_dir = args.top_level_dir

# Display the internal directory tree of the zip file
display_zip_tree(zip_path)

# Check if a file or dir is provided and add it to the zip file
if file_or_dir is not None:
    if target_dir is None and top_level_dir is None:
        parser.error('Either --target_dir or --top_level_dir must be provided when adding a file or dir.')
    add_to_zip(file_or_dir, zip_path, target_dir, top_level_dir)
    print("File/dir added to the zip file.")

# Check if a file or dir is provided and remove it from the zip file
if args.remove is not None:
    remove_from_zip(args.remove, zip_path)
    print("File/dir removed from the zip file.")
