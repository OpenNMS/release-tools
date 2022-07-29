import configparser
import os
import re
import csv
from library import web_connector
from library import log
from library import libfile
 

class jira:
    config_file=""
    configuration_file_handler=""

    base_url="https://localhost:8080"
    connection_handler=""

    release_path=os.path.join("workspace","releases.json")
    projects_list_path=os.path.join("workspace","projects.json")

    def __init__(self,configuration_file="",credential_file="",working_dir="workspace") -> None:
        self.log=log.log()
        self.file_library=libfile.libfile()

        if configuration_file:
            self.config_file=configuration_file
        else:
            self.config_file=os.path.join("configuration","jira.conf")

        if credential_file:
            self.cred_file=credential_file
        else:
            self.cred_file=os.path.join("configuration","credential.conf")

        if not os.path.exists(self.config_file):
            self.log.error("[JIRA]","Configuration File -"+self.config_file+"- not found")

        if not os.path.exists(self.cred_file):
            self.log.error("[JIRA]","Credential File -"+self.cred_file+"- not found")

        self.working_dir=working_dir

        if not os.path.exists(working_dir):
            os.mkdir(working_dir)

        self.configuration_file_handler=configparser.ConfigParser()
        self.configuration_file_handler.read(self.config_file)
        self.base_url=self.configuration_file_handler.get("JIRA","URL")

        self.credential_file_handler=configparser.ConfigParser()
        self.credential_file_handler.read(self.cred_file)
        self.base_auth=self.credential_file_handler.get("credentials","Authtoken")

        self.connection_handler=web_connector.web_connector()

    def getProjects(self):
        _request=self.connection_handler.get(self.base_url+self.configuration_file_handler.get("URLs","project_lists"))

        if _request.status_code == 200:
            _output=_request.json()
            self.file_library.save_json(self.projects_list_path,_output)
            return {"Operation":"Success","Filename":self.projects_list_path}
        else:
            self.log.error("JIRA","Unable to retrieve project list ("+str(_request.status_code)+")")
            return
        
    def getFixedIssuesWithMissingVersion(self):
        if os.path.exists(os.path.join(self.working_dir,"issues_withNextInFixedVersion.csv")):
            os.remove(os.path.join(self.working_dir,"issues_withNextInFixedVersion.csv"))

        if os.path.exists(os.path.join(self.working_dir,"issues_withNextInFixedVersion.json")):
            os.remove(os.path.join(self.working_dir,"issues_withNextInFixedVersion.json"))

        invalid_versionList=self.connection_handler.get(self.base_url+self.configuration_file_handler.get("URLs","issues_with_next_fixedversion"),header={"Authorization":"Basic "+self.base_auth})

        if invalid_versionList.status_code == 200:
            self.file_library.write_file(os.path.join(self.working_dir,"issues_withNextInFixedVersion.csv"),invalid_versionList.text)
        else:
            self.log.error("JIRA","Unable to retrieve issues with Next in the fixed Version field ("+str(invalid_versionList.status_code)+")")
            return


        
        data={}
        with open(os.path.join(self.working_dir,"issues_withNextInFixedVersion.csv"),"r") as f:
            csvReader=csv.DictReader(f)
        
            for r in csvReader:
                key=r["Issue key"]
                data[key]=r
        
        self.file_library.save_json(os.path.join(self.working_dir,"issues_withNextInFixedVersion.json"),data)

        return len(data)

    def getFixedIssues(self,release_name,project_name,filename="fixedIssues"):
        if os.path.exists(self.release_path):
            release_data=self.file_library.load_json(self.release_path)
        else:
            self.log.error("JIRA","Missing release List... Attempting to recover")
            self.getReleases()
            release_data=self.file_library.load_json(self.release_path)
        
        if not release_data:
            self.log.error("JIRA","Missing release List... Failed to recover")
            return

        if os.path.exists(self.projects_list_path):
            projects_list_data=self.file_library.load_json(self.projects_list_path)
        else:
            self.log.error("JIRA","Missing projects List... Attempting to recover")
            self.getProjects()
            projects_list_data=self.file_library.load_json(self.projects_list_path)
        
        if not projects_list_data:
            self.log.error("JIRA","Missing projects List... Failed to recover")


        release_info={}
        for release in release_data:
            if release_name in release["name"]:
                release_info=release
                del release_info["operations"]

        project_info={} 
        for project in projects_list_data:
            if re.match("^"+project_name+"$",project["name"]):
                project_info=project

        search_query=self.configuration_file_handler.get("Queries","fixed_issues").replace("'","").replace("#release_info#",release_info["name"])

        params = {'projectId':project_info['id'], 'maxResults':1000, 'jql':search_query}

        _output=self.connection_handler.get(self.base_url+self.configuration_file_handler.get("URLs","search"),param=params,header={"Authorization":"Basic "+self.base_auth,"Content-Type":"application/json"})

        if _output.status_code == 200:
            _output=_output.json()
            self.file_library.save_json(os.path.join(self.working_dir,filename),_output)
        else:
            self.log.error("JIRA","Unable to fixed issue list ("+str(_output.status_code)+")")
            return

        return {"Operation":"Success","Filename":filename}

    def getReleases(self,print_info=False):
        releases=self.connection_handler.get(self.base_url+self.configuration_file_handler.get("URLs","releases"),header={"Authorization":"Basic "+self.base_auth,"Content-Type":"application/json"})
        if releases.status_code == 200:
            self.file_library.save_json(self.release_path,releases.json())
            if print_info:
                release_info=releases.json()
                for release in release_info:
                    if not release["released"]:
                        print(release["name"])
                        print("","unmapped:",release["status"]["unmapped"]["count"])
                        print("","toDo:",release["status"]["toDo"]["count"])
                        print("","inProgress:",release["status"]["inProgress"]["count"])
                        print("","complete:",release["status"]["complete"]["count"])
                        print()
        else:
            self.log.error("JIRA","Unable to retrieve release list ("+str(releases.status_code)+")")
            return
    
    def getMyItems(self):
        filename="myItems.json"
        search_query=self.configuration_file_handler.get("Queries","my_items").replace("'","")
        params = {'maxResults':1000, 'jql':search_query}
        _output=self.connection_handler.get(self.base_url+self.configuration_file_handler.get("URLs","search"),param=params,header={"Authorization":"Basic "+self.base_auth,"Content-Type":"application/json"})
        if _output.status_code == 200:
            _output=_output.json()
            self.file_library.save_json(os.path.join(self.working_dir,filename),_output)
        else:
            self.log.error("JIRA","Unable to get your items("+str(_output.status_code)+")")
            return


        
