from datetime import datetime
import os 
from libCCI import circleci
from library import libfile,liblog
import configparser
import pandas 

configparser_handler=configparser.ConfigParser()
circleci_handler=""
workspace="workspace"

def getWorkspace(path="generic"):
    workspace=os.path.join("workspace",path)
    if not os.path.exists(workspace):
        os.makedirs(workspace)
    return workspace


if __name__ == "__main__":
    libfile=libfile.libfile()
    liblog=liblog.liblog()
    configparser_handler=configparser.ConfigParser()
    configparser_handler.read("configurations/circleci.conf")
    project_slug="github/OpenNMS/"+configparser_handler.get("Common","Project")
    circleci_handler=circleci.circleci(configparser_handler.get("Tokens","CircleCI"))
    
    flakytests=circleci_handler.retrieveFlakyTests(project_slug=project_slug)
    workspace=getWorkspace(os.path.join("projects",project_slug.replace("/","__")))

    output={}
    for test in flakytests["flaky_tests"]:
        tmp=test
        jobname=tmp["job_name"]
        if jobname not in output:
            output[jobname]=[]

        del tmp["job_name"]

        output[jobname].append(tmp)

    for job in output:
        tmp=output[job]
        liblog.print("Job: "+job)
        for entry in tmp:
            liblog.print("\tClassname: "+entry["classname"])
            liblog.print("\tTest Name: "+entry["test_name"])
            liblog.print("\tTimes Flaked: "+str(entry["times_flaked"]))
            print()
        print()

    liblog.print("A copy of results is saved in "+os.path.join(workspace,"flaky_tests.json"))
    libfile.save_json(os.path.join(workspace,"flaky_tests.json"),flakytests)