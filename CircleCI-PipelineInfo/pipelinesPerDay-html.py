from csv import excel
import json
import datetime
import glob
import shutil
import bs4, os
import calendar

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


for today_year in sorted(_day.keys(), reverse=True):
    if not os.path.exists("workspace/pipelinesPerDay-html"):
        os.mkdir("workspace/pipelinesPerDay-html")
    if not os.path.exists("workspace/pipelinesPerDay-html/" + str(today_year)):
        os.mkdir("workspace/pipelinesPerDay-html/" + str(today_year))
    shutil.copy("style.css", "workspace/pipelinesPerDay-html/" + str(today_year) + "/")
    _output = []

    for today_month in sorted(_day[today_year].keys(), reverse=True):
        pc = calendar.HTMLCalendar()
        strd = pc.formatmonth(today_year, today_month)

        bb = bs4.BeautifulSoup(strd, features="html.parser")

        sty = bb.new_tag(
            "link",
            attrs={"rel": "stylesheet", "type": "text/css", "href": "./style.css"},
        )
        bb.append(sty)
        s = bb.find("table")
        s.attrs["border"] = "1px"
        tr = s.find("tr")
        td = s.find_all("td")
        for col in td:
            if (
                col.text not in "\xa0"
                and int(col.text) in _day[today_year][today_month].keys()
            ):
                t = bb.new_tag("div", attrs={"class": "number"})
                t.string = col.text
                t2 = bb.new_tag("div", attrs={"class": "numbuilds"})
                t2.string = str(_day[today_year][today_month][int(col.text)])
                col.string = ""
                col.append(t)
                col.append(t2)
            else:
                if col.text != " ":
                    t = bb.new_tag("div", attrs={"class": "number"})
                    t.string = col.text
                    t2 = bb.new_tag("div", attrs={"class": "numbuilds"})
                    t2.string = str(0)
                    col.string = ""
                    col.append(t)
                    col.append(t2)

        _output.append(str(bb))

    with open(
        "workspace/pipelinesPerDay-html/"
        + str(today_year)
        + "/"
        + str(today_year)
        + ".html",
        "w",
    ) as f:
        for a in _output:
            f.write(a)
            f.write("<br/>")
