from library import jira 
from library import markup
import os

import argparse


parse = argparse.ArgumentParser("Jira-tools")
parse.add_argument("--version","-v",default="",help="Release version(For example, 30.0.2 or Meridian-2019.0.1)")
parse.add_argument("--releases","-r",action='store_true',help="Retrieve and update the release file")
parse.add_argument("--releasesWithInfo","-ri",action='store_true',help="Retrieve and show releases info")
parse.add_argument("--projects","-p",action='store_true',help="Retrieve and update the projects file")
parse.add_argument("--checkInvalidVersion","-ivv",action='store_true',help="Check for issue(s) that contain value Next in their fixed version")
parse.add_argument("--myitems","-me",action='store_true',help="Get Items assigned to me that are not resolved")
parse.add_argument("--epic","-e",default="",help="Epic key to fetch child issues")

args=parse.parse_args()
epicKey=args.epic

checkInvalidVersion=args.checkInvalidVersion
Version=args.version
getReleasesWithInfo=args.releasesWithInfo
getReleases=args.releases
getProjects=args.projects
getMyItems=args.myitems


Working_dir="workspace/"+Version

if not os.path.exists("workspace"):
    os.mkdir("workspace")

jira_handler= jira.jira(working_dir=Working_dir)   
markup_library=markup.markup_helper()

if checkInvalidVersion:
    number_of_issues_without_correct_version=jira_handler.getFixedIssuesWithMissingVersion()

    if number_of_issues_without_correct_version>0:
        print("We have",str(number_of_issues_without_correct_version),"issues that don't have proper version:")
        print()
        markup_library.print(filename=os.path.join(Working_dir,"issues_withNextInFixedVersion.json"),prefix="*")

if getReleases and not getReleasesWithInfo:
    jira_handler.getReleases()

if getReleasesWithInfo:
    jira_handler.getReleases(print_info=True)

if getProjects:
    jira_handler.getProjects()

if Version:
    jira_handler.getFixedIssues(Version,project_name="OpenNMS",filename="fixedIssues-"+Version+".json")
    markup_library.print_issues(filename=os.path.join(Working_dir,"fixedIssues-"+Version+".json"),release=Version,output_filename=os.path.join(Working_dir,"releasenote-"+Version+".txt"))

if getMyItems:
    jira_handler.getMyItems()
    markup_library.print(filename=os.path.join(Working_dir,"myItems.json"),prefix="*")

if epicKey:
    children = jira_handler.get_issues_under_epic(epicKey)
    print(f"Child issues under Epic {epicKey}:")
    for c in children:
        print(f"{c['key']} - {c['fields']['summary']}")
