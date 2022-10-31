**Note:** Update `circleci.conf` file before running the script.
* A token can be generated from `Personal API Tokens` page on CircleCI web interface.

# 
`main.py`; (**Note:** At the moment we only support OpenNMS repository)
```
usage: CircleCI [-h] [--branch BRANCH] [--all_branches] [--items ITEMS] [--branch_list] [--save SAVE]

options:
  -h, --help            show this help message and exit
  --branch BRANCH, -b BRANCH
                        The branch we want to get pipeline information for.
  --all_branches, -ab   Retrieve and save pipeline data for all branches we can find
  --items ITEMS, -i ITEMS
                        Number of pipelines are returned. Defaults to 5
  --branch_list, -bl    Retrieve and save branch lists to workspace/branches.json
  --save SAVE, -s SAVE  File name
```
> Common Usage:
> * `-ab` : Get all pipeline information (regardless who ran them)
> * `-bl` : Get/Update the branch list
* `getPlanUsage.py`: Gets the Plan Usage and creates two files, `billing_periods.json` and `planUsage.json` [**Output Location:** `workspace/plan_usage/`]
* `Category.py`: Gets the number of builds broken down into `main`,`dependabot` and `side` builds [**Output Location:** `workspace/pipelinesPerCategory/`]
* `pipelinesPerUser.py`: Gets the number of builds broken down by github id [**Output Location:** `workspace/pipelinesPerUser/`]
* `pipelinesPerDay.py`: Gets the number of builds broken down by day [**Output Location:** `workspace/PipelinesPerDay/`]
* `pipelinesPerDay-html.py`: Gets the number of builds broken down by day and saves it into a HTML format [**Output Location:** `workspace/pipelinesPerDay-html/`]

## Sample Usage
1) Run `python3 main.py -ab`
2) Run `python3 pipelinesPerDay-html.py`
