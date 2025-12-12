import configparser
from pathlib import Path
import json
from requests.auth import HTTPBasicAuth

from library.http_connector import HTTP_CONNECTOR

class JIRA:
    WORK_AREA="workarea"
    CONFIGURATION_FILE=""

    CONFIGURATIONS={
        "SERVER_URL": "",
        "APIs":{},
        "QUERIES":{}
    }

    LOGIN_CREDENTIAL=()

    HTTP_CONNECTOR=None
    
    def __init__(self,WORK_AREA="workarea",CONFIGURATION_FILE="jira.conf",CREDENTIAL_CONFIGURATION_FILE="credential.conf"):
        self.WORK_AREA=WORK_AREA
        self.CONFIGURATION_FILE=CONFIGURATION_FILE
        self.CREDENTIAL_CONFIGURATION_FILE=CREDENTIAL_CONFIGURATION_FILE
        self.__parse_expand_configurations()

        if self.LOGIN_CREDENTIAL:
            self.HTTP_CONNECTOR=HTTP_CONNECTOR()

    def __parse_expand_configurations(self):
        if not Path(self.CONFIGURATION_FILE).exists():
            print("Jira","Unable to find the configuration file")
        
        config_handler=configparser.ConfigParser()
        config_handler.read(self.CONFIGURATION_FILE)

        self.CONFIGURATIONS["SERVER_URL"]=config_handler.get("JIRA","URL")
        
        for item in config_handler.items("URLs"):
            self.CONFIGURATIONS["APIs"][item[0]]=item[1]
        
        for item in config_handler.items("Queries"):
            self.CONFIGURATIONS["QUERIES"][item[0]]=item[1].replace("'","")
        
        
        config_handler.read(self.CREDENTIAL_CONFIGURATION_FILE)

        self.LOGIN_CREDENTIAL=HTTPBasicAuth(config_handler.get("jira","Emailaddress"),config_handler.get("jira","Authtoken"))


    def getFixedIssues(self,release_name):
        payload = {
            "jql": self.CONFIGURATIONS["QUERIES"]["fixed_issues"].replace("#release_info#",release_name),
            "maxResults": 100,
            "fields": ["key", "summary", "issuetype", "status", "assignee"]
        }
        _output=self.HTTP_CONNECTOR.post(
            self.CONFIGURATIONS["SERVER_URL"] + self.CONFIGURATIONS["APIs"]["search"],
            data=json.dumps(payload),
            header={"Content-Type": "application/json"},
            auth=self.LOGIN_CREDENTIAL
        )

        output_data=_output.json()

        if "nextPageToken" in output_data:
            while "nextPageToken" in output_data:
                payload["nextPageToken"] = output_data["nextPageToken"]
                _next_page=self.HTTP_CONNECTOR.post(
                self.CONFIGURATIONS["SERVER_URL"] + self.CONFIGURATIONS["APIs"]["search"],
                    data=json.dumps(payload),
                    header={"Content-Type":"application/json","Accept":"application/json"},
                    auth=self.LOGIN_CREDENTIAL
                )
                if _next_page.status_code == 200:
                    next_page_data=_next_page.json()
                    output_data["issues"].extend(next_page_data["issues"])
                    if "nextPageToken" in next_page_data:
                        output_data["nextPageToken"]=next_page_data["nextPageToken"]
                    else:
                        del output_data["nextPageToken"]
                else:
                    print("SOMETHING WENT WRONG")
                    break

        if _output.status_code == 200:
            return output_data
        else:
            print("SOMETHING WENT WRONG")

    
    def getReleases(self):
        params={
            "status":"unreleased",
            "expand":"operations,issuesstatus"
        }
        releases=self.HTTP_CONNECTOR.get(
            self.CONFIGURATIONS["SERVER_URL"] + self.CONFIGURATIONS["APIs"]["releases"],
            header={"Content-Type":"application/json","Accept":"application/json"},
            auth=self.LOGIN_CREDENTIAL,
            param=params
            )
        
        _output=[]
        if releases.status_code == 200:
            release_info=releases.json()["values"]
            for release in release_info:
                if not release["released"]:
                    if release["name"] not in _output:
                        _output.append(release["name"])
        else:
            print("SOMETHING WENT WRONG")
        
        return _output












    
