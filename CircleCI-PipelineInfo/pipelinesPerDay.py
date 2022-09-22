from csv import excel
import json
import datetime
import glob
import os

_count = []
_branches = []
_day = {}
d = 0
for f in glob.glob("workspace/pipelines/*.json"):
    if "branches" not in f:
        with open(f, "r") as f:
            _d = json.load(f)

        print(
            "<<<",
            f.name.replace("workspace/", "").replace(".json", ""),
            ">>>",
            len(_d["items"]),
        )

        for a in _d["items"]:
            d += 1
            _created = datetime.datetime.strptime(
                a["created_at"].split("T")[0], "%Y-%m-%d"
            )
            if _created.year not in _day:
                _day[_created.year] = {}
            if _created.month not in _day[_created.year]:
                _day[_created.year][_created.month] = {}

            if _created.day not in _day[_created.year][_created.month]:
                _day[_created.year][_created.month][_created.day] = 1
            else:
                _day[_created.year][_created.month][_created.day] += 1
            _count.append(a["number"])

            _br = a["vcs"]["branch"]
            if _br not in _branches:
                _branches.append(_br)

today = datetime.datetime.now().strftime("%Y%m%d")
if not os.path.exists("workspace/PipelinesPerDay/"):
    os.mkdir("workspace/PipelinesPerDay")
with open("workspace/PipelinesPerDay/" + today + ".json", "w") as f:
    json.dump(_day, f, indent=4)
