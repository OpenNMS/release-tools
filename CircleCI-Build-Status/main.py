import argparse
import json
import os
from datetime import datetime
from pathlib import Path

from helpers.connectionHandler import ConnectionHandler
from helpers.mattermostHandler import MattermostHandler
from helpers.common import display_icons,mattermost_text,getProperty

parse = argparse.ArgumentParser("CircleCI Build Status")
parse.add_argument(
    "--mattermost",
    "-m",
    action="store_true",
    help="Post status update to Mattermost (default: False)",
)
parse.add_argument(
    "--console",
    "-c",
    action="store_true",
    help="Print status update to the console (default: False)",
)

args = parse.parse_args()

TODAYS_DATE_TIME=datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
BRANCH_CONFIGURATION=Path("configurations/branches.json")

PROJECT_SLUG="github/OpenNMS"

OVERALL_STATUS={}

# CircleCI related
CIRCLECI_TOKEN=""
CIRCLECI_TOKEN=getProperty("CIRCLECI_TOKEN","CIRCLE_TOKEN")

# Console
PRINT_TO_CONSOLE=args.console

# Mattermost related
MATTERMOST=args.mattermost
MATTERMOST_WEBHOOK_URL=""
if MATTERMOST:
    MATTERMOST_WEBHOOK_URL=getProperty("MATTERMOST_WEBHOOK_URL")

# Initialize the handler with CircleCI API base URL
handler = ConnectionHandler(
    base_url="https://circleci.com/api/v2",
    auth_credentials=CIRCLECI_TOKEN
)

with open(BRANCH_CONFIGURATION,"r") as fp:
    BRANCHES=json.load(fp)

for category in BRANCHES:
    if category not in OVERALL_STATUS:
        OVERALL_STATUS[f"{category}"]={}
    for a in BRANCHES[category]:
        if a not in OVERALL_STATUS[f"{category}"]:
            OVERALL_STATUS[f"{category}"][f"{a}"]={}
        for b in BRANCHES[category][a]:
            OVERALL_STATUS[f"{category}"][f"{a}"][f"{b}"]={
                 "pipeline":"",
                 "workflow":""
            }
            pipelines = handler.get(f"/project/{PROJECT_SLUG}/{a}/pipeline",params={
                "branch":f"{b}"
            })

            # 1. Get pipeline
            PIPELINE_ID=""
            for entry in reversed(pipelines["items"]):
                PIPELINE_ID=entry["id"]
                OVERALL_STATUS[f"{category}"][f"{a}"][f"{b}"]["pipeline"]=entry["number"]
            if not PIPELINE_ID:
                continue

            # 2. Get workflow
            WORKFLOW_ID=""

            workflows = handler.get(f"/pipeline/{PIPELINE_ID}/workflow")

            for item in workflows["items"]:
                WORKFLOW_ID=item["id"]
                OVERALL_STATUS[f"{category}"][f"{a}"][f"{b}"]["workflow"]=item["status"]
                break # get the first entry
            

            if OVERALL_STATUS[f"{category}"][f"{a}"][f"{b}"]["workflow"] in ["failed","failing"]:
                if "jobs" not in OVERALL_STATUS[f"{category}"][f"{a}"][f"{b}"]:
                    OVERALL_STATUS[f"{category}"][f"{a}"][f"{b}"]["jobs"]=[]
                jobs=handler.get(f"/workflow/{WORKFLOW_ID}/job")
                for job in jobs["items"]:
                    if job["status"] in ["failed"]:
                        OVERALL_STATUS[f"{category}"][f"{a}"][f"{b}"]["jobs"].append(job["name"])

# Save a copy of the overall status
if not os.path.exists("workarea"):
    os.mkdir("workarea")

with open(f"workarea/{TODAYS_DATE_TIME}.json","w") as fp:
    json.dump(OVERALL_STATUS,fp,indent=4)

print(f"Saved the result into workarea/{TODAYS_DATE_TIME}.json")

# Post a message to Mattermost
if MATTERMOST and MATTERMOST_WEBHOOK_URL:
    print("Mattermost:")
    mattermost_handler=MattermostHandler(
        webhook_url=MATTERMOST_WEBHOOK_URL
    )
    message=mattermost_text(OVERALL_STATUS)
    print(" ",mattermost_handler.post(message=message))


# print to screen
if PRINT_TO_CONSOLE:
    print("CircleCI Build Status")
    display_icons(OVERALL_STATUS)


