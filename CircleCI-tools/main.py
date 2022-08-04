from libCCI import circleci

import configparser

import argparse


parse = argparse.ArgumentParser("CircleCI-tools")
parse.add_argument("--branch","-b",default="develop",help="The branch we want to get pipeline information for.",required=True)
parse.add_argument("--items","-i",default="",help="Number of pipelines are returned. Defaults to 5")

args=parse.parse_args()

branch=args.branch
items=args.items

if items:
    maxitems=int(items)
else:
    maxitems=5


_cfg=configparser.ConfigParser()
_cfg.read("configurations/circleci.conf")
_project_slug="github/OpenNMS/"+_cfg.get("Common","Project")
cci_handler=circleci.circleci(_cfg.get("Tokens","CircleCI"))

print()
_pipelines=cci_handler.retrievePipelines(_project_slug,branch=branch)
for a in _pipelines['items'][0:maxitems]:
    if 'commit' in a['vcs']:
        print(a['number'],a['trigger']['actor']['login'],a['errors'],a['vcs']['commit']['subject'])
    else:
        print(a['number'],a['trigger']['actor']['login'],a['errors'],a['vcs']['revision'][:6])
    _pipelines_workflows=cci_handler.retrievePipelineWorkflow(str(a['id']))
    for b in _pipelines_workflows['items']:
        output=""
        if b['status'] in ["failed","failing"]:
            output = " * "+""+b['name']+" > "+b['status']+""
        elif b['status'] in ["running"]:
            output = " * "+""+b['name']+" > "+b['status']+""
        elif b['status'] in ["success"]:
            output=" * "+""+b['name']+" > "+b['status']+""
        else:
            output=" * "+""+b['name']+" > "+b['status']
        print(output)
    print("-"*10)
