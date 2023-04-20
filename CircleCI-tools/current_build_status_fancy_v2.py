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
configparser_handler=configparser.ConfigParser()
circleci_handler=""

console_message_boxEntries=[]


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
    layout["side"].split(Layout(name="box1"))#, Layout(name="box2"))
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
    _build={}



    for a in _pipelines['items'][0:1]:
        _pipelines_workflows=circleci_handler.retrievePipelineWorkflow(str(a['id']))
        #with open("workspace/"+branch.replace("/","__")+".json","w") as f:
        #    json.dump(_pipelines_workflows,f)

        _pipelines_info=_pipelines_workflows['items']   
        for b in _pipelines_info:
            _build[b["name"]]={"status":b['status'],"jobs":[]}
            if b['status'] in ["failed","failing"] and (b["name"] not in _build or _build[b["name"]]["status"] not in "success"):
                last_status="failed"
                _jobs=circleci_handler.retrieveWorkflowJobs(b['id'])
                _build[b["name"]]["jobs"]=_jobs["items"]

            elif b['status'] in ["running"]:
                if last_status not in ["failed"]:
                    last_status="running"
                _jobs=circleci_handler.retrieveWorkflowJobs(b['id'])
                _build[b["name"]]["jobs"]=_jobs["items"]
                for j in _jobs['items']:
                    if j['status'] not in ["running",'blocked'] and overall_status not in ["failed","failing"]:
                        overall_status=j['status']
            elif b['status'] in ["success"]:
                if last_status not in ["failed","running","cancelled"]:
                    last_status="success"
            else:
                last_status=b['status'] 
    
    return [last_status,overall_status,_build]

def getData(releases_info):
    data={}
    for release in releases_info:
        if "project" in releases_info[release] and releases_info[release]["project"]:
            project_slug="github/OpenNMS/"+releases_info[release]["project"]

        status=getPipelinesInformation(project_slug=project_slug,branch=releases_info[release]["branch"])

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
                if data[row][-1][s]["status"] in "failed":
                    _tmp_msg+="\t"+s+" -> "+data[row][-1][s]["status"]+"\n"
                    for j in data[row][-1][s]["jobs"]:
                        if j["status"] in ["failing","failed"]:
                            _tmp_url=circleci_handler.retrieveJob(j["project_slug"],j["job_number"])
                            if "web_url" in _tmp_url:
                                web_url="Link::"+_tmp_url["web_url"]+"::Link "
                            _tmp_msg+="\t\t"+web_url+""+j["name"]+" -> "+j["status"]+"\n"
            console_message_boxEntries.append(row+"\n"+_tmp_msg)
        elif value in 'running':
            _color="[turquoise2]"
            if data[row][1]:
                _msg="Running ("+data[row][1]+")"
            else:
                _msg="Running"

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
    layout["box1"].update(Panel(generate_table(_data,[now,now+timedelta(seconds=delay)]),title="Release Status", border_style="red"))
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
                    layout["box1"].update(Panel(generate_table(_data,[now,now+timedelta(seconds=delay)]),title="Release Status", border_style="red"))
                    layout["body"].update(mainBox())
            






