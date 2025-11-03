import argparse
import json
import os
from datetime import datetime
from pathlib import Path

from helpers.connectionHandler import ConnectionHandler
from helpers.mattermostHandler import MattermostHandler
from helpers.common import getProperty,flaky_testcase_data

parse = argparse.ArgumentParser("CircleCI Flaky Testcase Insights (OpenNMS Project)")
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

# Save a copy of the overall status
if not os.path.exists("workarea"):
    os.mkdir("workarea")


fields = ["test_name", "classname", "job_name", "times_flaked", "workflow_created_at"]

# Note: Flaky tests are branch agnostic. A flaky test is a test that passed and failed in the same commit.
PROJECT_FLAKY_TESTS=handler.get(f"/insights/{PROJECT_SLUG}/opennms/flaky-tests")

# Save the result to a file
with open(f"workarea/flaky-tests_{TODAYS_DATE_TIME}.json","w") as fp:
    json.dump(PROJECT_FLAKY_TESTS,fp,indent=4)

print(f"Saved the result into workarea/flaky-tests_{TODAYS_DATE_TIME}.json")

# Post a message to Mattermost
if MATTERMOST and MATTERMOST_WEBHOOK_URL:
    mattermost_handler=MattermostHandler(
        webhook_url=MATTERMOST_WEBHOOK_URL
    )
    chunks = flaky_testcase_data(PROJECT_FLAKY_TESTS["flaky_tests"])
    if len(chunks) > 1:
        for i, chunk in enumerate(chunks):
            chunks[i]=chunk.replace("Flaky Tests",f"Flaky Tests (Part {i+1} of {len(chunks)})")

    for i, chunk in enumerate(chunks):
        print(" ",mattermost_handler.post(message=chunk,footer=f"Part {i+1} of {len(chunks)}"))

# print to screen
if PRINT_TO_CONSOLE:
    print("OpenNMS CircleCI Flaky Tests Insights:")
    chunks = flaky_testcase_data(PROJECT_FLAKY_TESTS["flaky_tests"])
    for chunk in chunks:
        print(chunk)
