from tools.jira import jira
from tools.adoc import adoc

from library.markdown import MARKDOWN

import json

from pathlib import Path

import argparse


WORK_AREA=Path("workarea")
CONFIGURATION_FOLDER=Path("configurations")
CONFIGURATION_FOLDER=Path("configurations")


parse = argparse.ArgumentParser("Release Day 1 Automation")
parse.add_argument("--version","-v",default="",help="Release version(For example, 30.0.2 or Meridian-2019.0.1)")
parse.add_argument("--changelog","-c",default="",help="Changelog to modify")

ARGS=parse.parse_args()
VERSION=ARGS.version
CHANGE_LOG=ARGS.changelog

WORK_AREA=WORK_AREA / VERSION

Path(WORK_AREA).mkdir(exist_ok=True)

# We got the Version
JIRA=jira.JIRA(WORK_AREA=WORK_AREA,CONFIGURATION_FILE=CONFIGURATION_FOLDER/"jira.conf",CREDENTIAL_CONFIGURATION_FILE=CONFIGURATION_FOLDER/"credential.conf")   
MARKDOWN_HANDLER = MARKDOWN()

releases=JIRA.getReleases()
if VERSION not in releases:
    print(f"Unable to find {VERSION} Release")
else:
    # This is Day 1 -- Generating Changlog
    FIXED_ISSUES=JIRA.getFixedIssues(VERSION)
    with open(f"{WORK_AREA}/{VERSION}.json","w") as fp:
        json.dump(FIXED_ISSUES,fp,indent=4)

    # create release notes
    MARKDOWN_HANDLER.print_issues(input_filename=f"{WORK_AREA}/{VERSION}.json",
                           release_version=VERSION,
                           output_filename=f"{WORK_AREA}/{VERSION}.adoc")
    
    # Should we download the source code? or assume the source code is there

    if CHANGE_LOG:
        MAIN_ADOC = adoc.AsciiDoc(CHANGE_LOG)

        changelog_section=MAIN_ADOC.find_section("Changelog")

        FIXED_ISSUES_BREAKDOWN=MARKDOWN_HANDLER.get_json()

        MAIN_ADOC.add_release(
            changelog_section,
            version=FIXED_ISSUES_BREAKDOWN["release_version"],
            description=FIXED_ISSUES_BREAKDOWN["description"],
            categories=FIXED_ISSUES_BREAKDOWN["categories"],
            prepend=True
        )

        MAIN_ADOC.write_adoc(CHANGE_LOG)


    