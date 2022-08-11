from os import stat
from libCCI import circleci
from library import libfile,liblog
import configparser

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



if __name__ == "__main__":
    libfile=libfile.libfile()
    liblog=liblog.liblog()
    configparser_handler=configparser.ConfigParser()
    configparser_handler.read("configurations/circleci.conf")
    project_slug="github/OpenNMS/"+configparser_handler.get("Common","Project")
    circleci_handler=circleci.circleci(configparser_handler.get("Tokens","CircleCI"))
    
    releases_info=libfile.load_json("database/releases.json")

    for release in releases_info:
        if "project" in releases_info[release] and releases_info[release]["project"]:
            project_slug="github/OpenNMS/"+releases_info[release]["project"]

        status=getPipelinesInformation(project_slug=project_slug,branch=releases_info[release]["branch"])
        if status in 'success':
            liblog.success(release)
        elif status in 'running':
            liblog.info(release,prefix="Running")
        elif status in 'cancelled':
            liblog.warning(release,prefix="Cancelled",use_same_color=True)
        elif status in 'failed':
            liblog.error(release,prefix="Failed",use_same_color=True)

