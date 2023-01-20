import os
import json
import configparser
from libCCI import circleci
import shutil
import datetime 

today=datetime.datetime.now()

## Created Jan 6,2023
#  
# This script gets the list of context and its environment variables
# 
##


_cfg = configparser.ConfigParser()
_cfg.read("configurations/circleci.conf")
cci_handler = circleci.circleci(_cfg.get("Tokens", "CircleCI"))
output=cci_handler.getContextForOwner("gh/OpenNMS")
for a in output['items']:
    print("→",a['name'])#,a['created_at'])
    for b in cci_handler.getContextEnvironmentVariable(a['id'])['items']:
        print("","⇉",b['variable'])#,b['created_at'])
