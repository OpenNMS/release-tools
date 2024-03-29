# CircleCI-tools
Helps with interacting with CircleCI.

**Note:** Update `circleci.conf` file before running the script.
* A token can be generated from `Personal API Tokens` page on CircleCI web interface.

## `main.py` usage

### Features:

- List pipelines executed (and the job's status) of a branch

### Usage:
```
python main.py -h
usage: CircleCI-tools [-h] --branch BRANCH [--items ITEMS]

options:
  -h, --help            show this help message and exit
  --branch BRANCH, -b BRANCH
                        The branch we want to get pipeline information for.
  --items ITEMS, -i ITEMS
                        Number of pipelines are returned. Defaults to 5
```

## Other scripts
| Script | Notes |
|--------|-------|
|`current_build_status.py`| Shows build status for branches |
|`list_flaky_tests.py`| Lists the flaky tests for OpenNMS project |
|`current_build_status_fancy_v2.py`| A fancy version of https://opennms.github.io/opennms/ that runs in the console |
