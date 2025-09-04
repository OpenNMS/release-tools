# CircleCI Build Status
Gathers and prints the status of CircleCI Pipelines.

## Requirements:
* Python3
* Requests Python3 library
* CircleCI Token
* Mattermost Webhook URL (When posting to Mattermost)

## How to use on a local system:

1. Setup `.env` file and update `CIRCLECI_TOKEN` and `MATTERMOST_WEBHOOK_URL`

```json
{
    "CIRCLECI_TOKEN":"",
    "MATTERMOST_WEBHOOK_URL":""
}
```

2. Install requirements for the script

```bash

# Optional steps
python3 -m venv venv
source venv/bin/activate 

# Required steps:
pip3 install -r requirements.txt

```

3. Run the script

```bash

# Prints to console and posts to Mattermost
# See `Script Usage` section for list of options
python main.py -c -m 

```


# Script Usage

```bash

❯ python3 main.py -h
usage: CircleCI Build Status [-h] [--mattermost] [--console]

options:
  -h, --help        show this help message and exit
  --mattermost, -m  Post status update to Mattermost (default: False)
  --console, -c     Print status update to the console (default: False)

```