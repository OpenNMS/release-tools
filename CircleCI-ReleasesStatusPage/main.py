import json
import shutil
from circleCI import CircleCI

# Need to fix the cfg for `opennms`
Force_Update = False

CircleCI_Handler = CircleCI()
final_output = {}
final_output["opennms"] = CircleCI_Handler.getOpenNMS(force=Force_Update)
final_output["opennmsprime"] = CircleCI_Handler.getOpenNMSPrime(force=Force_Update)
final_output["poweredby"] = CircleCI_Handler.getPoweredBy(force=Force_Update)

with open("workspace/result.json", "w") as f:
    json.dump(final_output, f, indent=4)

html_template = ""
with open("template/static.html", "r") as f:
    html_template = f.readlines()


opennms_pipeline_status = []
opennms_prime_pipeline_status = []
poweredby_pipeline_status = []
others_pipeline_status = []


for pipeline_repo in final_output:
    tmp = []
    for pipeline in final_output[pipeline_repo]:
        if "datetime" in pipeline:
            continue
        className = ""
        if "success" in final_output[pipeline_repo][pipeline]:
            bgClassName = "success-bg"
            className = "success"
        elif "failed" in final_output[pipeline_repo][pipeline]:
            bgClassName = "failed-bg"
            className = "failed"
        elif "running" in final_output[pipeline_repo][pipeline]:
            bgClassName = "running-bg"
            className = "running"
        elif "canceled" in final_output[pipeline_repo][pipeline]:
            bgClassName = "canceled-bg"
            className = "canceled"
        else:
            bgClassName = "unknown-bg"
            className = "unknown"

        tmp.append(
            "<tr class='"
            + bgClassName
            + "'><td >"
            + pipeline
            + "</td><td >"
            + '<div class="'
            + className
            + '">'
            + final_output[pipeline_repo][pipeline]
            + "</div></td></tr>"
        )

    if pipeline_repo in "opennms":
        opennms_pipeline_status = tmp
    elif pipeline_repo in "opennmsprime":
        opennms_prime_pipeline_status = tmp
    elif pipeline_repo in "poweredby":
        poweredby_pipeline_status = tmp
    elif pipeline_repo in "others":
        others_pipeline_status = tmp

output = ""
for html_entry in html_template:
    if "#opennms#" in html_entry.strip():
        output += html_entry.replace("#opennms#", "\n".join(opennms_pipeline_status))
    elif "#opennms-prime#" in html_entry.strip():
        output += html_entry.replace(
            "#opennms-prime#", "\n".join(opennms_prime_pipeline_status)
        )
    elif "#poweredby#" in html_entry.strip():
        output += html_entry.replace(
            "#poweredby#", "\n".join(poweredby_pipeline_status)
        )
    elif "#others#" in html_entry.strip():
        output += html_entry.replace("#others#", "\n".join(others_pipeline_status))
    else:
        output += html_entry

shutil.copy(
    "template/images/OpenNMS_Horizontal-Logo_Dark-BG-60px.png",
    "workspace/OpenNMS_Horizontal-Logo_Dark-BG-60px.png",
)
with open("workspace/index.html", "w") as f:
    f.write(output)
