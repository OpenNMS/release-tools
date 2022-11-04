from .library import connectionhandler
import json, os


class circleci:
    _baseUrl = "https://circleci.com"
    _baseApiUrl = "/api"
    _apiVersion = "/v2"
    _apiUrl = _baseUrl + _baseApiUrl + _apiVersion

    def __init__(self, token, connectionHandler=None) -> None:
        """
        token: Required, Contains the CircleCI token
        connectionHandler: Optional, Provide only if you want to use a custom handler for the requests
        """
        self._token = token

        if connectionHandler:
            self._connectionHandler = connectionHandler
        else:
            self._connectionHandler = connectionhandler.connectionhandler()

    def _navigateReturnResult(self, url, data=""):
        return self._connectionHandler.connect(url, self._token, data)

    def saveJson(self, path, filename, data):
        with open(os.path.join(path, filename + ".json"), "w") as f:
            json.dump(data, f, indent=4)

    def retrieveProjects(self):
        _url = (
            self._baseUrl
            + self._baseApiUrl
            + "/v1.1/user/repos/github?page=1&per-page=100"
        )
        return self._navigateReturnResult(_url).json()

    def retrieveBranches(self, project_slug):
        """Retrieve branches for a project
        Warning: Uses private api and can be unstable"""
        _url = (
            self._baseUrl
            + self._baseApiUrl
            + "/private/project/"
            + project_slug
            + "/branches"
        )
        return self._navigateReturnResult(_url).json()

    def retrievePipelines(
        self, organization_slug, branch="", page_token="", allpages=False, _data={}
    ):
        # This works well without recursion
        _url = self._apiUrl + "/project/" + organization_slug + "/pipeline"
        if branch:
            _url += "?branch=" + branch
        if page_token:
            if "?branch=" in _url:
                _url += "&page-token=" + page_token
            else:
                _url += "?page-token=" + page_token
        _data = self._navigateReturnResult(_url).json()
        if "next_page_token" in _data and _data["next_page_token"] and allpages:
            return self.retrievePipelines(
                organization_slug,
                branch,
                _data["next_page_token"],
                allpages=allpages,
                _data=_data,
            )

        return _data

    def retrievePipelines_new(
        self,
        organization_slug,
        branch="",
        page_token="",
        allpages=False,
        trackPipelinesID=False,
        _data={},
    ):
        _url = self._apiUrl + "/project/" + organization_slug + "/pipeline"
        if branch:
            _url += "?branch=" + branch
        if page_token:
            if "?branch=" in _url:
                _url += "&page-token=" + page_token
            else:
                _url += "?page-token=" + page_token

        tmp_data = self._navigateReturnResult(_url).json()
        if trackPipelinesID:
            filename = branch.replace("/", "--")
            outputpath = "workspace/pipeline_ids"
            if not os.path.exists(outputpath):
                os.mkdir(outputpath)

            _pipelineIDfile = outputpath + "/" + filename + ".json"
            if os.path.exists(_pipelineIDfile):
                with open(_pipelineIDfile, "r") as f:
                    pipeline_id = json.load(f)
            else:
                pipeline_id = {}
                pipeline_id["tokens"] = []

            for i in tmp_data["items"]:
                if i["id"] not in pipeline_id["tokens"]:
                    pipeline_id["tokens"].append(i["id"])
            with open(_pipelineIDfile, "w") as f:
                json.dump(pipeline_id, f, indent=4)

        if _data:
            _data["items"].extend(tmp_data["items"])
        else:
            _data = tmp_data
        if "next_page_token" in tmp_data and tmp_data["next_page_token"] and allpages:
            return self.retrievePipelines_new(
                organization_slug,
                branch,
                tmp_data["next_page_token"],
                allpages=allpages,
                trackPipelinesID=trackPipelinesID,
                _data=_data,
            )

        return _data

    def retrievePipelineWorkflow(self, pipeline_id):
        _url = self._apiUrl + "/pipeline/" + pipeline_id + "/workflow"
        return self._navigateReturnResult(_url).json()

    def retrieveWorkflow(self, id):
        _url = self._apiUrl + "/workflow/" + id
        return self._navigateReturnResult(_url).json()

    def retrieveWorkflowJobs(self, id):
        _url = self._apiUrl + "/workflow/" + id + "/job"
        return self._navigateReturnResult(_url).json()

    def retrieveJob(self, project_slug, id):
        _url = self._apiUrl + "/project/" + project_slug + "/job/" + str(id)
        return self._navigateReturnResult(_url).json()

    def retrieveJobStepDetails(self, project_slug, id):
        _url = (
            self._baseUrl
            + self._baseApiUrl
            + "/v1.1/project/"
            + project_slug
            + "/"
            + str(id)
        )
        return self._navigateReturnResult(_url).json()

    def retrieveJobArtifact(self, project_slug, id):
        _url = (
            self._apiUrl + "/project/" + project_slug + "/job/" + str(id) + "/artifacts"
        )
        return self._navigateReturnResult(_url).json()

    def retrieveCreditUsage(self, project_slug, workflow, branch):
        _url = self._apiUrl + "/insights/" + project_slug + "/workflows/" + workflow
        if branch:
            _url += "?branch=" + branch
        return self._navigateReturnResult(_url).json()

    def retrieveFlakyTests(self, project_slug):
        _url = self._apiUrl + "/insights/" + project_slug + "/flaky-tests"
        return self._navigateReturnResult(_url).json()

    def retrieveJobTimeseriesData(
        self, project_slug, workflow, branch="", granularity=""
    ):
        """Get timeseries data for all jobs within a workflow."""
        _url = (
            self._apiUrl
            + "/insights/time-series/"
            + project_slug
            + "/workflows/"
            + workflow
            + "/jobs"
        )
        if branch:
            if "?" not in _url:
                _url += "?"
            elif "&" in _url:
                _url += "&"
            _url += "branch=" + branch

        if granularity:
            if "?" not in _url:
                _url += "?"
            elif "&" in _url:
                _url += "&"
            _url += "granularity=" + granularity

        return self._navigateReturnResult(_url).json()

    def myProfile(self):
        _url = self._baseUrl + self._baseApiUrl + "/private/me"
        return self._navigateReturnResult(_url).json()

    def myCollaborations(self):
        """User's Organizations"""
        _url = self._apiUrl + "/me/collaborations"
        return self._navigateReturnResult(_url).json()

    def getOrganizationPlan(self, project_slug):
        """https://circleci.com/api/v1.1/organization/github/OpenNMS/plan"""
        _url = (
            self._baseUrl
            + self._baseApiUrl
            + "/v1.1/organization/"
            + project_slug
            + "/plan"
        )
        return self._navigateReturnResult(_url).json()

    # def getOrganizationId(self,project_id):
    #    """ https://circleci.com/private/orgs/dec41a64-8cda-4a5a-907a-5cabac40dfbc/plan """
    #    _url=self._baseUrl+"/private/orgs/"+project_id+"/plan"
    #    return self._navigateReturnResult(_url).json()

    # def getGraphQLUnstable(self, payload):
    #    """https://circleci.com/graphql-unstable"""
    #    _url = self._baseUrl + "/graphql-unstable"
    #    print(_url)
    #    self._connectionHandler.option_connect(_url, self._token)
    #    return self._navigateReturnResult(_url, payload)
