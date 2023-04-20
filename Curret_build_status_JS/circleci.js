class webConnector{
    constructor(){
        console.log("webConnector");
    }

    get(url){
        console.log("Get Command");
        return fetch(url)
    }

    post(url,data,header){
        console.log("Post Command");
        /*fetch(url,{
            method: "POST",
            body: JSON.stringify(data),
            headers: header
        })*/
    }
}


class circleci{
    constructor(){
        this._connectionHandler=new webConnector();
        console.log("circleci");
        
    }

    async getPipeline(slug,branch){
        let response = await this._connectionHandler.get("https://circleci.com/api/v2/project/"+slug+"/pipeline?branch="+branch).then(res=>res.json());
            return response;
    }

    async getPipelineWorkflow(pipeline_id){
        let response = await this._connectionHandler.get("https://circleci.com/api/v2/pipeline/"+pipeline_id+"/workflow").then(res=>res.json());
            return response;
    }

    async getWorkflowJobs(job_id){
        let response = await this._connectionHandler.get("https://circleci.com/api/v2/workflow/"+job_id+"/job").then(res=>res.json());
        return response;

    }
}