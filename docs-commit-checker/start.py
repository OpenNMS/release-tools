#!/usr/bin/env python3
import datetime
import os
import json
import logging
from pathlib import Path
from git import Repo
import json

from helpers.helpers import compare_checksum_files,checksum_folder,get_latest_branch_file


with open(os.path.join("configurations","general.json"),"r") as fp:
    CONFIGURATION=json.load(fp)

if not os.path.exists("reports"):
    os.mkdir("reports")

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set the minimum log level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("reports/app.log",mode="w"),      # Log to a file
        logging.StreamHandler()                               # Log to console
    ],
)

logger = logging.getLogger(__name__)

# ==== Configuration ====

REPO_URL = CONFIGURATION["repository_url"] # "https://github.com/OpenNMS/opennms.git"
BRANCHES = CONFIGURATION["branches"] # ["foundation-2021","foundation-2022","foundation-2023","foundation-2024","release-34.x", "develop"]  # List of branches to check
HISTORY_FILE = os.path.join("reports","history.json")
LOCAL_REPO_DIR = "./repo"  # Where to clone/fetch the repo

TODAY=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
TODAY_DATE=TODAY.split("_")[0]
TODAY_TIME=TODAY.split("_")[1]

# ==== Load history ====
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)
else:
    history = {}

# ==== Clone or update repo ====
if not os.path.exists(LOCAL_REPO_DIR):
    logger.info(f"Cloning {REPO_URL}...")
    repo = Repo.clone_from(REPO_URL, LOCAL_REPO_DIR)
else:
    logger.info(f"Fetching updates for {REPO_URL}...")
    repo = Repo(LOCAL_REPO_DIR)
    repo.remotes.origin.fetch()

# ==== Process each branch ====
new_commits_report = {}

for branch in BRANCHES:
    logger.info(f"Checking branch: {branch}")
    repo.git.checkout(branch)
    repo.remotes.origin.pull(branch)

    last_seen = history.get(branch)
    if last_seen:
        commit_range = f"{last_seen}..origin/{branch}"
    else:
        commit_range = f"origin/{branch}"
    commits = list(repo.iter_commits(commit_range, paths="docs/"))

    new_commits = []
    for commit in commits:
        if commit == last_seen:
            break
        # Look at the commit diff for files in docs/
        for diff in commit.stats.files.keys():
            if diff.startswith("docs/"):
                new_commits.append({
                    "hash": commit.hexsha,
                    "author": commit.author.name,
                    "date": commit.committed_datetime.isoformat(),
                    "message": commit.message.strip()
                })
                break

    # Reverse to chronological order (oldest first)
    new_commits.reverse()

    if new_commits:
        new_commits_report[branch] = new_commits
        # Update last_seen to the newest commit we processed
        history[branch] = new_commits[-1]["hash"]
    


    # ==== Check to see if we have a history ====
    if not os.path.exists(f"reports/checksums"):
        os.makedirs(f"reports/checksums")
    
    if not os.path.exists(f"reports/checksums/{branch}"):
        os.makedirs(f"reports/checksums/{branch}")
    latest_file = get_latest_branch_file(branch)
    current_file=os.path.join(f"reports/checksums/{branch}/{branch}_{TODAY_DATE}_{TODAY_TIME}.json")
    checksum_folder('repo/docs',output_file=current_file,logger=logger)
    if latest_file:
        # ==== Compare files ====
        logger.info(f"Comparing {latest_file} vs {current_file}")
        compare_checksum_files(latest_file,current_file,logger)
  

# ==== Save history ====
with open(HISTORY_FILE, "w") as f:
    json.dump(history, f, indent=2)

# ==== Output report ====
if new_commits_report:
    for a in new_commits_report:
        report_file=f"reports/{a}/{TODAY_DATE}_{TODAY_TIME}.json"
        logger.info(f"{a} docs folder contains a new change, see {report_file} for more details")

        if not os.path.exists(f"reports/{a}"):
            os.mkdir(f"reports/{a}")

        with open(f"{report_file}","w") as fp:
            json.dump(new_commits_report[a],fp,indent=4)
