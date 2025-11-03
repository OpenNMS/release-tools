# Jira-tools
Helps with interacting with JIRA server.

**Note:** Update the credential configuration file before running the script.
You need create an API Token. See `https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/`

## Features:

- Retrieve Issue(s) which contain "Next" in the fixed Version
- Retrieve Project and Release List (these information is required in order to generate the release notes)
- Retrieve the fixed items for a release
- (Additional Item) Get list of unresolved items assigned to the current user
- A copy of the information shown on screen is saved under 'workspace' directory in either json,csv or txt format
- Retrieve all child issues under an Epic
- Get list of unresolved items assigned to the current user.
- **Check closed issues:**
  - Verify that each closed issue has a `fixVersion`.
  - Optionally verify that the issue key appears in GitHub commits/PRs.
- A copy of the information shown on screen is saved under the `workspace` directory in JSON format.

## Usage:
```
❯ python main.py -h

usage: Jira-tools [-h] [--version VERSION] [--releases] [--releasesWithInfo] [--projects] [--checkInvalidVersion] [--myitems]

options:
  -h, --help            show this help message and exit
  --version VERSION, -v VERSION
                        Release version(For example, 30.0.2 or Meridian-2019.0.1)
  --releases, -r        Retrieve and update the release file
  --releasesWithInfo, -ri
                        Retrieve release and show the status of items under it
  --projects, -p        Retrieve and update the projects file
  --checkInvalidVersion, -ivv
                        Check for issue(s) that contain value Next in their fixed version
  --myitems, -me        Get Items assigned to me that are not resolved
  --epic EPIC, -e EPIC  Get all child issues under the given Epic key (e.g., NMS-11231)
  --checkClosedIssues, -cci
                        Check closed issues for missing fixVersion or missing GitHub references
 ```

## Examples:

- **Get release notes for version 34.0.0**  
  ```
  python main.py --version 34.0.0
  ```
- **Check closed issues for version 34.0.0**
  ```
  python main.py --version 34.0.0 -cci
  ```
- **Check all closed issues (no version filter)**
  ```
  python main.py -cci
  ```
