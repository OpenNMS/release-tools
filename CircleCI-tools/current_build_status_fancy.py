from os import stat
from libCCI import circleci
from library import libfile,liblog
import configparser
import time
from datetime import datetime,timedelta
from rich.live import Live
from rich.table import Table


configparser_handler=configparser.ConfigParser()
circleci_handler=""

def getPipelinesInformation(maxitems=1,branch="develop",prefix="",project_slug=""):
    if project_slug:
        _pipelines=circleci_handler.retrievePipelines(project_slug,branch=branch)
    else:
        _pipelines=circleci_handler.retrievePipelines(project_slug,branch=branch)

    last_status=""
    prefix+=" "
    for a in _pipelines['items'][0:1]:
        _pipelines_workflows=circleci_handler.retrievePipelineWorkflow(str(a['id']))
        for b in _pipelines_workflows['items']:
            if b['status'] in ["failed","failing"]:
                last_status="failed"
            elif b['status'] in ["running"]:
                if last_status not in ["failed"]:
                    last_status="running"
            elif b['status'] in ["success"]:
                if last_status not in ["failed","running","cancelled"]:
                    last_status="success"
            else:
                last_status=b['status']      
    return last_status

def getData(releases_info):
    data={}
    for release in releases_info:
        if "project" in releases_info[release] and releases_info[release]["project"]:
            project_slug="github/OpenNMS/"+releases_info[release]["project"]


        status=getPipelinesInformation(project_slug=project_slug,branch=releases_info[release]["branch"])
        data[release]=status

    return data

def generate_table(data) -> Table:
    """Make a new table."""
    table = Table(show_lines=True)
    table.add_column("Release")
    table.add_column("Status")

    for row in data:
        value = data[row]
        if value in 'success':
            _color="[green3]"
            _msg="Successful"
        elif value in 'failed':
            _color="[bright_red]"
            _msg="Failed"
        elif value in 'running':
            _color="[turquoise2]"
            _msg="Running"
        else:
            _color="[bright_magenta]"
            _msg=value

        table.add_row(
            f"{_color+row}", _color+_msg
        )
    return table


if __name__ == "__main__":
    libfile=libfile.libfile()
    liblog=liblog.liblog()
    configparser_handler=configparser.ConfigParser()
    configparser_handler.read("configurations/circleci.conf")
    project_slug="github/OpenNMS/"+configparser_handler.get("Common","Project")
    circleci_handler=circleci.circleci(configparser_handler.get("Tokens","CircleCI"))
    

    releases_info=libfile.load_json("database/releases.json")
    print("Getting Data")
    _data=getData(releases_info)

    with Live(generate_table(_data), refresh_per_second=5) as live:
        print("Updated:",datetime.now(),"->",datetime.now()+timedelta(seconds=1800),";Default Sleep:",1800)
        live.update(generate_table(_data))
        time.sleep(1800)
        _data=getData(releases_info)
