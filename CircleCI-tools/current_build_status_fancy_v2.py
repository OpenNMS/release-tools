from os import stat
from libCCI import circleci
from library import libfile,liblog
import configparser
import time
from datetime import datetime,timedelta
from rich.live import Live
from rich.table import Table
from rich.layout import Layout
from rich import box
from rich.align import Align
from rich.console import Console, Group
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.text import Text
import re
import json
import argparse

configparser_handler=configparser.ConfigParser()
circleci_handler=""

console_message_boxEntries=[]


parse = argparse.ArgumentParser("CircleCI Release Build Status")
parse.add_argument('-a',"--showAllBuilds",action='store_false',help="Show all builds, regardless of their status")

args=parse.parse_args()
ShowFailedBuildsOnly=args.showAllBuilds

def make_layout() -> Layout:
    """Define the layout."""
    layout = Layout(name="root")

    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3),
    )
    layout["main"].split_row(
        Layout(name="side"),
        Layout(name="body", ratio=1, minimum_size=50),
    )
    layout["side"].split(Layout(name="box1"))
    return layout


def mainBox() -> Panel:
    console_output_message = Text()
    message = Table().grid(padding=1)
    message.add_column()
    if console_message_boxEntries:
        for cmb in console_message_boxEntries:
            if "integration-test" in cmb:
                icon="🧪"
            elif "test" in cmb:
                icon="💨"
            elif "merge" in cmb:
                icon="⛙"
            elif "image" in cmb:
                icon="🫙"
            else:
                icon=""
            cm=re.compile(r"Link::(.*)::Link", re.MULTILINE)
            if cm.search(cmb):
                web_url=cm.search(cmb).groups()[0]
                cmb=cm.sub("",cmb)
                web_url_text=""
                if web_url:
                    web_url_text="\tWeb URL: "+web_url+""
            else:
                web_url_text=""
            tmp=Text("\n "+icon+" "+cmb+""+web_url_text+"\n"+"__"*10+"\n", "green")
            tmp.highlight_regex(r">>(.*)<<", "bold yellow")
            tmp.highlight_regex(r"->", "bold red")
            tmp.highlight_regex(r"\\", "bold cyan")
            console_output_message+=tmp
   
    message_panel = Panel( 
         Group(console_output_message),
       
        box=box.ROUNDED,
        padding=(1, 2),
        title="[b cyan]Console Output",
        border_style="bright_blue",
    )
    return message_panel

class Header:
    """Display header with clock."""
    def __rich__(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="right", ratio=1)
        grid.add_row(
            "",
            "[b]OpenNMS[/b]",
            datetime.now().ctime().replace(":", "[blink]:[/]"),
        )
        return Panel(grid, style="white on black")

def getPipelinesInformation(maxitems=1,branch="develop",prefix="",project_slug=""):
    if project_slug:
        _pipelines=circleci_handler.retrievePipelines(project_slug,branch=branch)
    else:
        _pipelines=circleci_handler.retrievePipelines(project_slug,branch=branch)

    last_status=""
    prefix+=" "
    overall_status=""
    jobs={}

    for p in _pipelines['items'][0:1]:
        _pipelines_workflows=circleci_handler.retrievePipelineWorkflow(str(p['id']))
        for pw in _pipelines_workflows["items"]:
            
            if pw['name'] not in jobs:
                jobs[pw['name']]={"status":pw['status'],"created_at":pw['created_at'],"stopped_at":pw["stopped_at"],"id":pw["id"]}
            else:
                if pw['status'] not in jobs[pw['name']]["status"]:
                    if pw['created_at']>jobs[pw['name']]["created_at"]:
                        jobs[pw['name']]={"status":pw['status'],"created_at":pw['created_at'],"stopped_at":pw["stopped_at"],"id":pw["id"]}
        
    last_status="success"
    sub_jobs=""
    for j in jobs:
        if "success" not in jobs[j]['status']:
            last_status=jobs[j]['status']
            sub_jobs=circleci_handler.retrieveWorkflowJobs(jobs[j]['id'])["items"]
    return [last_status,overall_status,sub_jobs]

def getData(releases_info):
    data={}
    for release in releases_info:
        if "project" in releases_info[release] and releases_info[release]["project"]:
            project_slug="github/OpenNMS/"+releases_info[release]["project"]

        status=getPipelinesInformation(project_slug=project_slug,branch=releases_info[release]["branch"])
        if status[0] not in 'success' and ShowFailedBuildsOnly:
            data[release]=status
        elif not ShowFailedBuildsOnly:
            data[release]=status

    return data

def generate_table(data,updated) -> Table:
    """Make a new table."""
    table = Table(show_lines=True,expand=True)
    table.add_column("Release")
    table.add_column("Status")
    table.add_row("[light_goldenrod2]Updated:"+str(updated[0]),"[light_goldenrod1]Next update:"+str(updated[1]))
    console_message_boxEntries.clear()

    for row in data:
        value = data[row][0]
        if value in 'success':
            _color="[green3]"
            _msg="Successful"
        elif value in 'failed':
            _color="[bright_red]"
            _msg="Failed"
            _tmp_msg=""
            web_url=""
            for s in data[row][-1]:
                if s["status"] in "failed":
                    _tmp_msg+="\t"+s['name']+" -> "+s["status"]+"\n"
                    #for j in data[row][-1][s]["jobs"]:
                    #    if j["status"] in ["failing","failed"]:
                    #        _tmp_url=circleci_handler.retrieveJob(j["project_slug"],j["job_number"])
                    #        if "web_url" in _tmp_url:
                    #            web_url="Link::"+_tmp_url["web_url"]+"::Link "
                    #        _tmp_msg+="\t\t"+web_url+""+j["name"]+" -> "+j["status"]+"\n"
            console_message_boxEntries.append(row+"\n"+_tmp_msg)
        elif value in 'running':
            _color="[turquoise2]"
            if data[row][1]:
                _msg="Running ("+data[row][1]+")"
            else:
                _msg="Running"
            _tmp_msg=""
            _tmp_waiting=0
            for j in data[row][-1]:
                if j["status"] in "running":
                    _tmp_msg+="\t"+j["name"]+" -> "+j["status"]+"\n"
                else:
                    _tmp_waiting+=1

            
            if _tmp_waiting>0:
                _tmp_msg+="\t>> "+str(_tmp_waiting)+" << job(s) is/are waiting for current job(s) to finish\n"

            console_message_boxEntries.append(row+"\n"+_tmp_msg)



        else:
            _color="[bright_magenta]"
            _msg=value

        table.add_row(
            f"{_color+row}", _color+_msg
        )
    return table


if __name__ == "__main__":
    libfile=libfile.libfile()
    liblog=liblog.liblog()
    configparser_handler=configparser.ConfigParser()
    configparser_handler.read("configurations/circleci.conf")
    project_slug="github/OpenNMS/"+configparser_handler.get("Common","Project")
    circleci_handler=circleci.circleci(configparser_handler.get("Tokens","CircleCI"))
    

    releases_info=libfile.load_json("database/releases.json")
    now=datetime.now()
    _data=getData(releases_info)

    delay=1800


    job_progress = Progress(
        "{task.description}",
        SpinnerColumn(),
        BarColumn(bar_width=None),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        expand=True
    )
    job_progress.add_task("[magenta]Delay", total=delay)
    total = sum(task.total for task in job_progress.tasks)

    overall_progress = Progress()
    overall_task = overall_progress.add_task("All Jobs", total=int(total))

    progress_table = Table.grid(expand=True,padding=0)
    progress_table.add_row(
        Panel(job_progress, title="[b]Progress", border_style="green"),
    )

    console = Console()
    layout = make_layout()
    layout["header"].update(Header())
    release_status_title="Release Status"
    if ShowFailedBuildsOnly:
        release_status_title+=" (Filter: Non-Successful builds only)"
    layout["box1"].update(Panel(generate_table(_data,[now,now+timedelta(seconds=delay)]),title=release_status_title, border_style="red"))
    layout["body"].update(mainBox())
    layout["footer"].update(progress_table)

    with Live(layout, refresh_per_second=10, screen=True) as live:
        while True:
            time.sleep(1)
            for job in job_progress.tasks:
                if not job.finished:
                    job_progress.advance(job.id)
                else:
                    now=datetime.now()
                    _data=getData(releases_info)
                    job_progress.reset(job.id)
                    layout["box1"].update(Panel(generate_table(_data,[now,now+timedelta(seconds=delay)]),title=release_status_title, border_style="red"))
                    layout["body"].update(mainBox())