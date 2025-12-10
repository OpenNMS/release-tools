import json
import os
import re


class MARKDOWN:
    def __init__(self):
        pass

    def filter_summary(self,input_text):
        output=input_text
        patterns = [
            r"CVE-\d{4}-\d+\s*\(([^)]+)\)",  # CVE-style
            r"Vulnerabilities in\s+([^\s\]]+)",  # Trivy Bug: Vulnerabilities in <lib>
            r"Trivy Bug:\s*Library\s+([^\s]+)",  # Trivy Bug: Library <lib>
            r"Trivy Bug:\s*\(Vuln ID:\s*CVE-\d{4}-\d+\):\s*([a-zA-Z0-9._\-:]+)",  # Trivy Bug: (Vuln ID...) <lib>
            r"Trivy Bug:\s*([a-zA-Z0-9._\-:]+):",  # Trivy Bug: <lib>:
        ]
        for pattern in patterns:
            match = re.search(pattern, input_text)
            if match:
                output = f"Update {match.group(1)} library"
                break
        return output
    
    def create_markdown(self,output_filename,release_version,input_data,markdown=False,sort_keys=True):
        if markdown:
            prefix="#"
            level_1=1
            level_2=2
        else:
            prefix="="
            level_1=2
            level_2=3
        with open(output_filename,"w") as fp:
            if not markdown:
                fp.write("[[releasenotes-changelog-"+release_version+"]]\n")
                fp.write("\n")
            
            fp.write(f"{prefix*level_1} Release "+release_version+"\n")
            fp.write("\n")
            fp.write("\n")
            if sort_keys:
                entries = sorted(input_data)
            else:
                entries = input_data
            for entry in entries:
                fp.write(f"{prefix*level_2} "+entry+"\n")
                fp.write("\n")
                for entry_2 in sorted(input_data[entry]):
                    fp.write("* "+entry_2+"\n")
                fp.write("\n")

    def create_breakdown_json(self,release_version,input_data,output_filename=""):
        filtered_data={}
        for key in sorted(input_data):
            filtered_data[key] = sorted(input_data[key])

        self._jsonBreakdown={
            "release_version": release_version,
            "description": "REPLACE ME",
            "categories":filtered_data
        }
        with open(output_filename,"w") as fp:
            json.dump(self._jsonBreakdown,fp,indent=4,sort_keys=True)

    def print_issues(self,input_filename,release_version="",output_filename=""):
        _meridian=False
        _horizon=False

        issues={}
        output={}
        output_md={}

        with open(input_filename,"r") as fp:
            resolved_issues = json.load(fp)['issues']
        
        for issue in resolved_issues:
            issue_type = issue["fields"]["issuetype"]["name"]
            if issue_type not in issues:
                issues[issue_type]={}
            if self.filter_summary(issue["fields"]["summary"].strip()) not in issues[issue_type]:
                issues[issue_type][self.filter_summary(issue["fields"]["summary"].strip())]=[]
            issues[issue_type][self.filter_summary(issue["fields"]["summary"].strip())].append(issue["key"])

        for issue_type in issues:
            if issue_type not in output:
                output[issue_type]=[]
            if issue_type not in output_md:
                output_md[issue_type]=[]

            for issue in issues[issue_type]:
                issues_list=issues[issue_type][issue]
                output[issue_type].append(f"{issue} (Issue{'s' if len(issues_list)>1 else ''} {', '.join(f'https://issues.opennms.org/browse/{k}[{k}]' for k in issues_list)})")
                output_md[issue_type].append(f"{issue} (Issue{'s' if len(issues_list)>1 else ''} {', '.join(f'[{k}](https://issues.opennms.org/browse/{k})' for k in issues_list)})")
        

        if "Meridian" in release_version:
            release_year=int(release_version.split("-")[1].split(".")[0])
            _meridian=True
        else:
            release_year=int(release_version.split(".")[0])
            _horizon=True
        
        if (_meridian and release_year<=2020) or (_horizon and release_year<=29):
            _tmp="="*4
        else:
            _tmp="="*2
        
        self.create_markdown(output_filename=output_filename,
                             release_version=release_version,
                             input_data=output)

        self.create_markdown(output_filename=output_filename.replace("adoc","md"),
                             release_version=release_version,
                             input_data=output_md,
                             markdown=True)
        
        self.create_breakdown_json(output_filename=output_filename.replace("adoc","_breakdown.json"),
                             release_version=release_version,
                             input_data=output)
        
    def get_json(self):
        return self._jsonBreakdown

