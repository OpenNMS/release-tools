import os
import sys
import json
from typing import Literal

def display_icons(data, indent=0, prefix=""):
    for key, value in data.items():
        if isinstance(value, dict):
            if "pipeline" in value and "workflow" in value:
                full_key = f"{prefix}{key}"
                icon = get_icon(value["workflow"])
                print(" " * indent + f"{full_key}: {icon}")
            else:
                new_prefix = f"{prefix}{key}/"
                display_icons(value, indent + 4, new_prefix)
        else:
            full_key = f"{prefix}{key}"
            print(" " * indent + f"{full_key}: {value}")


def get_icon(workflow_status,output_target: Literal["console", "markdown"]="console"):
    if workflow_status == 'success':
        if output_target == "console":
            output='✅'
        elif output_target == "markdown":
            output=':white_check_mark:'
        return output
    elif workflow_status == 'failed':
        if output_target == "console":
            output='❌'
        elif output_target == "markdown":
            output=':x:'
        return output
    elif workflow_status == 'failing':
        if output_target == "console":
            output='⚠️'
        elif output_target == "markdown":
            output=':warning:'
        return output
    elif workflow_status == 'running':
        if output_target == "console":
            output='⏳'
        elif output_target == "markdown":
            output=':hourglass_flowing_sand:'
        return output
    elif workflow_status == 'cancelled':
        if output_target == "console":
            output='🚫'
        elif output_target == "markdown":
            output=':large_orange_square:'
        return output
    else:
        if output_target == "console":
            output='❓'
        elif output_target == "markdown":
            output=':question:'
        return output

    
def mattermost_text(data):
    OUTPUT=""
    OUTPUT+="| Branch | Status | Notes |\n"
    OUTPUT+="|----------|:--------:|:---------|\n"
    for e in data:
        OUTPUT+=f"|:building_construction:  **{e}:** |         |         |\n"
        for b in data[e]:
            if "pipeline" in data[e][b] and "workflow" in data[e][b]:
                STATUS=get_icon(data[e][b]["workflow"],"markdown")
                NOTES=""
                if data[e][b]["workflow"] in ["failed","failing","cancelled"]:
                    if "jobs" in data[e][b]:
                        if len(data[e][b]["jobs"])>1:
                            NOTES="The following jobs have failed: "
                        else:
                            NOTES="The following job has failed: "
                        for j in data[e][b]["jobs"]:
                            NOTES+=f"* {j} "
                    else:
                        NOTES=data[e][b]["workflow"]
                elif data[e][b]["workflow"] in ["running"]:
                    NOTES=data[e][b]["workflow"]

                OUTPUT+=f"|&nbsp;&nbsp;:herb:  {b}     |  {STATUS}   |  {NOTES}  |\n"
            else:
                OUTPUT+=f"|&nbsp;:package:  **{b}:** |         |         |\n"
                for z in data[e][b]:
                    STATUS=get_icon(data[e][b][z]["workflow"],"markdown")
                    NOTES=""
                    if data[e][b][z]["workflow"] in ["failed","failing","cancelled"]:
                        if "jobs" in data[e][b][z]:
                            if len(data[e][b][z]["jobs"])>1:
                                NOTES="The folowing jobs have failed: "
                            else:
                                NOTES="The folowing job has failed: "

                            for j in data[e][b][z]["jobs"]:
                                NOTES+=f"* {j} "
                        else:
                            NOTES=data[e][b][z]["workflow"]
                    elif data[e][b][z]["workflow"] in ["running"]:
                        NOTES=data[e][b][z]["workflow"]
                    OUTPUT+=f"|&nbsp;&nbsp;:herb:  {z}     |  {STATUS}   |  {NOTES}   |\n"

    OUTPUT+="\n"
    return OUTPUT


def getProperty(property_name):
    if os.getenv(property_name):
        OUTPUT=os.getenv(property_name)
    elif os.path.exists(".env"):
        with open(".env","r") as fp:
            env_file=json.load(fp)
        if property_name in env_file:
            OUTPUT=env_file[property_name]
    else:
        print(f"{property_name} is missing! Exiting...")
        sys.exit(1)
    return OUTPUT