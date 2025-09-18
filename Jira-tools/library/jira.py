import configparser
import os
import re
import csv
from library import web_connector
from library import log
from library import libfile
 
from requests.auth import HTTPBasicAuth

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
        # self.auth = HTTPBasicAuth(self.credential_file_handler.get("credentials","Emailaddress"), self.credential_file_handler.get("credentials","Authtoken"))
        # self.auth = (self.credential_file_handler.get("credentials","Emailaddress").replace('"',''), self.credential_file_handler.get("credentials","Authtoken").replace('"',''))
        self.auth = HTTPBasicAuth(
            self.credential_file_handler.get("credentials","Emailaddress").replace('"',''),
            self.credential_file_handler.get("credentials","Authtoken").replace('"','')
            )

        self.connection_handler=web_connector.web_connector()

    def getUserInfo(self):
        filename="User.json"
        _request=self.connection_handler.get(self.base_url+self.configuration_file_handler.get("URLs","myself"),header={"Accept": "application/json"},auth=self.auth)
        print(self.base_auth)
        if _request.status_code == 200:
            _output=_request.json()
            self.file_library.save_json(os.path.join(self.working_dir,filename),_output)
            return {"Operation":"Success","Filename":self.projects_list_path}
        else:
            print(_request.text)
            self.log.error("JIRA","Unable to retrieve user information ("+str(_request.status_code)+")")
            return

    def getProjects(self):
        _request=self.connection_handler.get(self.base_url+self.configuration_file_handler.get("URLs","project_lists"),auth=self.auth)

        if _request.status_code == 200:
            _output=_request.json()
            self.file_library.save_json(self.projects_list_path,_output)
            return {"Operation":"Success","Filename":self.projects_list_path}
        else:
            self.log.error("JIRA","Unable to retrieve project list ("+str(_request.status_code)+")")
            return
    def get_issues_under_epic(self, epic_key):
        url = f"{self.base_url}/rest/agile/1.0/epic/{epic_key}/issue"
        resp = self.connection_handler.get(
            url, header={"Content-Type": "application/json"}, auth=self.auth
        )
        if resp.status_code == 200:
            return resp.json().get('issues', [])
        else:
            # fallback: JQL on Epic Link field
            epic_link_field = self.configuration_file_handler.get(
                "Fields", "epic_link_field", fallback="Epic Link"
            )
            jql = f'"{epic_link_field}" = {epic_key}'
            params = {'maxResults': 1000, 'jql': jql}
            fallback_resp = self.connection_handler.get(
                self.base_url + self.configuration_file_handler.get("URLs","search"),
                param=params, header={"Content-Type":"application/json"}, auth=self.auth
            )
            if fallback_resp.status_code == 200:
                return fallback_resp.json().get('issues', [])
            return []
    
    def getFixedIssuesWithMissingVersion(self):
        search_query = self.configuration_file_handler.get("Queries", "issues_resolved_contain_next").replace("'", "")
        
        import json
        payload = {
            "jql": search_query,
            "maxResults": 1000,
            "fields": ["key", "summary", "issuetype", "status", "assignee"]
        }
        url = self.base_url + self.configuration_file_handler.get("URLs", "search")
        _output = self.connection_handler.post(
            url,
            data=json.dumps(payload),
            header={"Content-Type": "application/json"},
            auth=self.auth
        )
        data = _output.json()
    
        self.file_library.save_json(
            os.path.join(self.working_dir, "issues_withNextInFixedVersion.json"), 
            data
        )
        return len(data.get("issues", []))

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
        for release in release_data['values']:
            if release_name in release["name"]:
                release_info=release
                if "operations" in release_info:
                    del release_info["operations"]

        project_info={} 
        for project in projects_list_data:
            if re.match("^"+project_name+"$",project["name"]):
                project_info=project

        search_query=self.configuration_file_handler.get("Queries","fixed_issues").replace("'","").replace("#release_info#",release_info["name"])

        import json
        payload = {
            "jql": search_query,
            "maxResults": 1000,
            "fields": ["key", "summary", "issuetype", "status", "assignee"]
        }
        url = self.base_url + self.configuration_file_handler.get("URLs", "search")
        _output = self.connection_handler.post(
            url,
            data=json.dumps(payload),
            header={"Content-Type": "application/json"},
            auth=self.auth
        )
        if _output.status_code == 200:
            _output = _output.json()
            self.file_library.save_json(os.path.join(self.working_dir, filename), _output)
        else:
            print("DEBUG Jira response:", _output.text)
            self.log.error("JIRA", "Unable to fixed issue list ("+str(_output.status_code)+")")
            return

        return {"Operation":"Success","Filename":filename}

    def getReleases(self,print_info=False):
        # we have to do this because of versions api doesn't support returning the status of issues under a release
        params={
            "status":"unreleased",
            "expand":"operations,issuesstatus"
        }
        releases=self.connection_handler.get(self.base_url+self.configuration_file_handler.get("URLs","releases"),header={"Content-Type":"application/json","Accept":"application/json"},auth=self.auth,param=params)

        if releases.status_code == 200:
            self.file_library.save_json(self.release_path,releases.json())

            if print_info:
                release_info=releases.json()["values"]
                for release in release_info:
                    if not release["released"]:
                        print(release["name"])
                        if "issuesStatusForFixVersion" not in release:
                            print("Not Sure about item status")
                        else:
                            print("","unmapped:",release["issuesStatusForFixVersion"]["unmapped"])
                            print("","toDo:",release["issuesStatusForFixVersion"]["toDo"])
                            print("","inProgress:",release["issuesStatusForFixVersion"]["inProgress"])
                            print("","done:",release["issuesStatusForFixVersion"]["done"])
                        print()
        else:
            self.log.error("JIRA","Unable to retrieve release list ("+str(releases.status_code)+")")
            return
    
    def getMyItems(self):
        import json
        filename = "myItems.json"
        search_query = self.configuration_file_handler.get("Queries", "my_items").replace("'", "")

        url = self.base_url + "/rest/api/3/search/jql"
        payload = {
            "jql": search_query,
            "maxResults": 50,
            "fields": ["key", "summary", "status", "issuetype", "assignee"]
        }

        _output = self.connection_handler.post(
            url,
            data=json.dumps(payload),
            header={"Accept": "application/json", "Content-Type": "application/json"},
            auth=self.auth
        )

        if _output.status_code == 200:
            raw = _output.json()
            self.file_library.save_json(os.path.join(self.working_dir, filename), raw)
            return {"Operation": "Success", "Filename": filename}
        else:
            print(_output.text)  # show Jira error message
            self.log.error("JIRA", f"Unable to get your items ({_output.status_code})")
            return