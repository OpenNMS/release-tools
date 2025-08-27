import hashlib
import os
import json
import glob
from datetime import datetime
import re

def file_checksum(path, algorithm='sha256', block_size=65536):
    """Return the hex digest of the file."""
    h = hashlib.new(algorithm)
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(block_size), b''):
            h.update(chunk)
    return h.hexdigest()

def checksum_folder(folder_path, output_file='checksums.json',logger=None):
    """Walk through a folder, calculate checksums, and store in a JSON file."""
    checksums = {}
    for root, _, files in os.walk(folder_path):
        for name in files:
            file_path = os.path.join(root, name)
            try:
                checksums[file_path] = file_checksum(file_path)
            except Exception as e:
                if logger:
                    logger.error(f"Skipping {file_path}: {e}")
                else:
                    print(f"Skipping {file_path}: {e}")

    with open(output_file, 'w') as f:
        json.dump(checksums, f, indent=4)
    if logger:
        logger.info(f"Checksums saved to {output_file}")
    else:
        print(f"Checksums saved to {output_file}")

def get_latest_branch_file(branch_name, directory="reports/hashes"):
    # Build the pattern to match files for the specific branch
    pattern = os.path.join(directory, f"{branch_name}_*.json")
    files = glob.glob(pattern)

    # Function to extract timestamp from filename
    def extract_timestamp(filename):
        match = re.search(rf"{re.escape(branch_name)}_(\d{{4}}-\d{{2}}-\d{{2}})_(\d{{2}}-\d{{2}}-\d{{2}})\.json$", filename)
        if match:
            date_str = match.group(1)
            time_str = match.group(2)
            return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H-%M-%S")
        return datetime.min

    # Sort files by extracted timestamp
    files.sort(key=extract_timestamp, reverse=True)

    return files[0] if files else None

def compare_checksum_files(file1, file2,logger=None):
    """Compare two checksums.json files and report differences."""
    with open(file1, 'r') as f:
        checksums1 = json.load(f)
    with open(file2, 'r') as f:
        checksums2 = json.load(f)

    set1 = set(checksums1.keys())
    set2 = set(checksums2.keys())

    added_files = set2 - set1
    deleted_files = set1 - set2
    modified_files = [f for f in (set1 & set2) if checksums1[f] != checksums2[f]]

    if added_files:
        if logger:
            logger.info("🆕 Files present in second file but not in first:")
        else:
            print("🆕 Files present in second file but not in first:")
        for f in added_files:
            if logger:
                logger.info(f" + {f}")
            else:
                print(f" + {f}")
            

    if deleted_files:
        if logger:
            logger.info("❌ Files present in first file but missing in second:")
        else:
            print("❌ Files present in first file but missing in second:")

        for f in deleted_files:
            if logger:
                logger.info(f" - {f}")
            else:
                print(f" - {f}")


    if modified_files:
        if logger:
            logger.info("✏️ Files changed between snapshots:")
        else:
            print("✏️ Files changed between snapshots:")
        for f in modified_files:
            if logger:
                logger.info(f" * {f}")
            else:
                print(f" * {f}")

    if not (added_files or deleted_files or modified_files):
        if logger:
            logger.info("✅ No differences found.")
        else:
            print("✅ No differences found.")

# Example usage
# branch = "feature-login"
# latest_file = get_latest_branch_file(branch)
# print("Latest file for branch:", latest_file)

# Example:
# compare_checksum_files('checksums_old.json', 'checksums_new.json')