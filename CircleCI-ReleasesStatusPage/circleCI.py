from libCCI import circleci
from common import common

import configparser

import json

import sys

import datetime
import re
import os


class CircleCI:
    def _localPrint(self, msg):
        print("[[CircleCI]]", msg, file=sys.stdout)

    def __init__(self) -> None:
        self._cfg = configparser.ConfigParser()
        self._cfg.read("configurations/circleci.conf")
        self._project_slug = "github/OpenNMS/" + self._cfg.get("Common", "Project")
        self._cci_handler = circleci.circleci(self._cfg.get("Tokens", "CircleCI"))

    def getBranchesNew(self, projectSlug):
        _repository = projectSlug.split("/")[-1]
        if not os.path.exists("workspace/branches/branches" + _repository + ".json"):
            self._localPrint(
                "workspace/branches/branches"
                + _repository
                + ".json not found >>Loading from server<<"
            )
            _branches = self._cci_handler.retrieveBranches(project_slug=projectSlug)
            _branches["datetime"] = str(datetime.datetime.now())
            common.backup_save(
                "branches" + _repository + ".json", _branches, folder="branches"
            )
        else:
            self._localPrint(
                "workspace/branches/branches"
                + _repository
                + ".json found >>Loading from cache<<"
            )
            with open("workspace/branches/branches" + _repository + ".json") as f:
                _branches = json.load(f)

        return _branches

    def getOpenNMS(self, force=False):
        _list = self._cfg.get("projects - opennms", "Branches").split(",")
        _project_slug = self._cfg.get("projects - opennms", "Project_Slug")
        output = {}
        _filePath = "workspace/pipelines/currentstatus_opennms.json"
        if force:
            self._localPrint(_filePath + " not found >>Loading from server<<")
            for item in _list:
                output[item] = "N/A"
                _pipelines = self._cci_handler.retrievePipelines_new(
                    _project_slug,
                    branch=item,
                    allpages=False,
                    trackPipelinesID=False,
                )
                _data = self._cci_handler.retrievePipelineWorkflow(
                    _pipelines["items"][0]["id"]
                )
                overall_status = "N/A"
                if len(_data["items"]) > 0:
                    _lastest_pipeline = _data["items"][0]
                    if overall_status in "N/A":
                        overall_status = _lastest_pipeline["status"]
                    if _lastest_pipeline["status"] in "success":
                        if overall_status not in ["failing", "failed"]:
                            overall_status = _lastest_pipeline["status"]
                    elif _lastest_pipeline["status"] in "running":
                        overall_status = _lastest_pipeline["status"]
                    else:
                        overall_status = _lastest_pipeline["status"]

                output[item] = overall_status
            output["datetime"] = str(datetime.datetime.now())

            common.backup_save(
                "currentstatus_opennms.json",
                output,
                folder="pipelines",
            )
        else:
            self._localPrint(_filePath + " found >>Loading from cache<<")
            if os.path.exists(_filePath):
                with open(_filePath, "r") as f:
                    output = json.load(f)

        return output

    def getOpenNMSPrime(self, force=False):
        _list = []
        _branch = self._cfg.get("projects - opennms-prime", "Branches").split(",")

        for year in self._cfg.get("projects - opennms-prime", "Years").split(","):
            for branch in _branch:
                _tmp = branch + str(year)
                if branch in "release-":
                    _tmp += ".x"
                _list.append(_tmp)

        _project_slug = self._cfg.get("projects - opennms-prime", "Project_Slug")
        output = {}
        _filePath = "workspace/pipelines/currentstatus_opennmsprime.json"
        if force:
            self._localPrint(_filePath + " not found >>Loading from server<<")
            for item in _list:
                output[item] = "N/A"
                _pipelines = self._cci_handler.retrievePipelines_new(
                    _project_slug,
                    branch=item,
                    allpages=False,
                    trackPipelinesID=False,
                )
                _data = self._cci_handler.retrievePipelineWorkflow(
                    _pipelines["items"][0]["id"]
                )
                overall_status = "N/A"
                if len(_data["items"]) > 0:
                    _lastest_pipeline = _data["items"][0]
                    if overall_status in "N/A":
                        overall_status = _lastest_pipeline["status"]
                    if _lastest_pipeline["status"] in "success":
                        if overall_status not in ["failing", "failed"]:
                            overall_status = _lastest_pipeline["status"]
                    elif _lastest_pipeline["status"] in "running":
                        overall_status = _lastest_pipeline["status"]
                    else:
                        overall_status = _lastest_pipeline["status"]
                output[item] = overall_status
            output["datetime"] = str(datetime.datetime.now())

            common.backup_save(
                "currentstatus_opennmsprime.json",
                output,
                folder="pipelines",
            )
        else:
            self._localPrint(_filePath + " found >>Loading from cache<<")
            if os.path.exists(_filePath):
                with open(_filePath, "r") as f:
                    output = json.load(f)

        return output

    def getPoweredBy(self, force=False):
        _list = []
        for year in self._cfg.get("projects - poweredby", "Years").split(","):
            _list.append("poweredby-" + str(year))

        _branch = self._cfg.get("projects - poweredby", "Branches")
        output = {}
        _filePath = "workspace/pipelines/currentstatus_PoweredBy.json"

        if force:
            self._localPrint(_filePath + " not found >>Loading from server<<")
            for item in _list:
                output[item] = "N/A"
                _project_slug = "github/OpenNMS/" + item
                _pipelines = self._cci_handler.retrievePipelines_new(
                    _project_slug,
                    branch=_branch,
                    allpages=False,
                    trackPipelinesID=False,
                )
                _data = self._cci_handler.retrievePipelineWorkflow(
                    _pipelines["items"][0]["id"]
                )
                overall_status = "N/A"
                if "items" in _data and len(_data["items"]) > 0:
                    _lastest_pipeline = _data["items"][0]
                    if overall_status in "N/A":
                        overall_status = _lastest_pipeline["status"]
                    if _lastest_pipeline["status"] in "success":
                        if overall_status not in ["failing", "failed"]:
                            overall_status = _lastest_pipeline["status"]
                    elif _lastest_pipeline["status"] in "running":
                        overall_status = _lastest_pipeline["status"]
                    else:
                        overall_status = _lastest_pipeline["status"]
                output[item] = overall_status
            output["datetime"] = str(datetime.datetime.now())

            common.backup_save(
                "currentstatus_PoweredBy.json",
                output,
                folder="pipelines",
            )
        else:
            self._localPrint(_filePath + " found >>Loading from cache<<")
            if os.path.exists(_filePath):
                with open(_filePath, "r") as f:
                    output = json.load(f)

        return output

    def getBuildStatusAcrossAllProjects(self, force=False):
        # replacement for getCurrentStatus

        # 1. Get projects from configuration file
        _projects = self._cfg.get("Common", "Projects").split(",")

        # 2. Generate the project_slug for each project
        for _project in _projects:
            _project_slugs = []
            _cfg_project_section = "projects - " + _project
            _tmp_project_slug = self._cfg.get(_cfg_project_section, "Project_Slug")

            # Check to see if we have placeholder variable
            _matched = re.match(".*\<(.*)\>.*", _tmp_project_slug)

            if _matched:
                for match_group in _matched.groups():
                    # If match_group is not empty
                    if match_group:
                        for item in self._cfg.get(
                            _cfg_project_section, match_group
                        ).split(","):
                            _project_slugs.append(
                                _tmp_project_slug.replace("<" + match_group + ">", item)
                            )
            else:
                if _tmp_project_slug not in _project_slugs:
                    _project_slugs.append(_tmp_project_slug)

        # 3. Loop through the project slugs
        for _project_slug in _project_slugs:
            _branchWithLatestPipeline = {}
            _branchWithLatestPipeline["items"] = []
            _cfg_branchList = self._cfg.get(_cfg_project_section, "Branches").split(",")
            _repositoryName = _project_slug.split("/")[-1]
            self._localPrint("Repository::" + _repositoryName)
            _branchList = self.getBranchesNew(_project_slug)["items"]
            print(_branchList)

            # Populate the branch list
            _branchlistfiltered = []
            for _branch in _branchList:
                if _branch["name"] not in _branchlistfiltered:
                    _branchlistfiltered.append(_branch["name"])

            for _branch in _cfg_branchList:
                _tmp_branch = ""
                for _branchFiltered in _branchlistfiltered:
                    if re.search(_branch, _branchFiltered):
                        _tmp_branch = _branchFiltered
                        break
                if _tmp_branch:
                    self._localPrint(
                        "\t_branch, " + _branch + " maps to " + _tmp_branch
                    )
                else:
                    continue

            # Let's get the pipeline for the branch
            _pipelines = self._cci_handler.retrievePipelines_new(
                _project_slug,
                branch=_tmp_branch,
                allpages=False,
                trackPipelinesID=False,
            )
            _pipelines["datetime"] = str(datetime.datetime.now())
            _branchWithLatestPipeline["items"].append(
                {
                    "name": _tmp_branch,
                    "data": self._cci_handler.retrievePipelineWorkflow(
                        _pipelines["items"][0]["id"]
                    ),
                }
            )
            _branchWithLatestPipeline["datetime"] = str(datetime.datetime.now())
            common.backup_save(
                "currentstatus__" + _repositoryName + "__.json",
                _branchWithLatestPipeline,
                folder="pipelines",
            )
