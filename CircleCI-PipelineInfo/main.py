from libCCI import circleci
from common import common

import configparser

import argparse

import json

import sys

import datetime

import os, shutil

parse = argparse.ArgumentParser("CircleCI")
parse.add_argument(
    "--branch",
    "-b",
    default="develop",
    help="The branch we want to get pipeline information for.",
    required=False,
)
parse.add_argument(
    "--all_branches",
    "-ab",
    action="store_true",
    help="Retrieve and save pipeline data for all branches we can find",
)

parse.add_argument(
    "--items", "-i", default="", help="Number of pipelines are returned. Defaults to 5"
)
parse.add_argument(
    "--branch_list",
    "-bl",
    action="store_true",
    help="Retrieve and save branch lists to workspace/branches.json",
)
parse.add_argument("--save", "-s", default="", help="File name")
# Do we want to display items that only belongs to a certain user?
#

args = parse.parse_args()

branch = args.branch
retrieve_branches = args.branch_list
all_branches = args.all_branches
items = args.items
outputFile = args.save
AllItems = False

if not items:
    maxitems = 5
elif items and items not in "all":
    maxitems = int(items)
elif items in "all":
    maxitems = ""
    AllItems = True


_cfg = configparser.ConfigParser()
_cfg.read("configurations/circleci.conf")
_project_slug = "github/OpenNMS/" + _cfg.get("Common", "Project")
cci_handler = circleci.circleci(_cfg.get("Tokens", "CircleCI"))


if retrieve_branches:
    _branches = cci_handler.retrieveBranches(project_slug=_project_slug)
    _branches["datetime"] = str(datetime.datetime.now())

    common.backup_save("branches.json", _branches)

    sys.exit(0)


if all_branches:
    if not os.path.exists("workspace/branches.json"):
        print("<<", "all_branches", ">>", "Gathering branch list")
        _branches = cci_handler.retrieveBranches(project_slug=_project_slug)
        _branches["datetime"] = str(datetime.datetime.now())
        common.backup_save("branches.json", _branches)

    with open("workspace/branches.json", "r") as f:
        branche_list = json.load(f)
    for ib in branche_list["items"]:
        print("<<", ib["name"], ">>")
        _pipelines = cci_handler.retrievePipelines_new(
            _project_slug, branch=ib["name"], allpages=AllItems, trackPipelinesID=True
        )
        _pipelines["datetime"] = str(datetime.datetime.now())
        common.backup_save(
            ib["name"].replace(" ", "__").replace("/", "_") + ".json",
            _pipelines,
            folder="pipelines",
        )

    sys.exit(0)


_pipelines = cci_handler.retrievePipelines_new(
    _project_slug, branch=branch, allpages=AllItems, trackPipelinesID=True
)

if outputFile:
    with open(outputFile, "w") as f:
        json.dump(_pipelines, f, indent=4)

    _pipelines["datetime"] = str(datetime.datetime.now())

    if outputFile:
        common.backup_save(outputFile, _pipelines)
    else:
        common.backup_save("pipelines.json", _pipelines)

    sys.exit(0)
