
import json 

class markup_helper:

    def __init__(self):
        pass

    def print(self,filename,prefix=""):
        with open(filename,"r") as f:
            data=json.load(f)
        
        if "issues" in data:
            data=data["issues"]


        for entry in data:
            if prefix:
                if "fields" in entry:
                    if "summary" in entry["fields"]:
                        print(prefix,entry["key"],entry["fields"]["summary"].strip())
                    else:
                        print(prefix,entry,entry["fields"]["Summary"].strip())
                else:
                    print(prefix,entry,data[entry]["Summary"].strip())
            else:
                print(entry,entry["Summary"].strip())

    def print_issues(self,filename,release="",output_filename="",show_output=True):
        meridian=False
        horizon=False
        with open(filename,"r") as f:
            data=json.load(f)

        break_down={}
        
        import re
        for entry in data["issues"]:
            if entry["key"].startswith("MPLUG"):
                continue

            summary = entry["fields"]["summary"].strip()

            # --- CVE-style issues → "Update <lib> library" ---
            m = re.match(r"CVE-\d{4}-\d+\s*\(([^)]+)\)", summary)
            if m:
                summary = f"Update {m.group(1)} library"

            # --- Trivy Bug: Vulnerabilities in <lib> ---
            t = re.search(r"Vulnerabilities in\s+([^\s\]]+)", summary)
            if t:
                summary = f"Update {t.group(1)} library"

            # --- Trivy Bug: Library <lib> ---
            lib = re.search(r"Trivy Bug:\s*Library\s+([^\s]+)", summary)
            if lib:
                summary = f"Update {lib.group(1)} library"

            # --- Trivy Bug: (Vuln ID: CVE-xxxx-xxxx): <lib>: ---
            vuln = re.search(r"Trivy Bug:\s*\(Vuln ID:\s*CVE-\d{4}-\d+\):\s*([a-zA-Z0-9._\-:]+)", summary)
            if vuln:
                summary = f"Update {vuln.group(1)} library"

            # --- Trivy Bug: <lib>: <details> ---
            bug = re.match(r"Trivy Bug:\s*([a-zA-Z0-9._\-:]+):", summary)
            if bug:
                summary = f"Update {bug.group(1)} library"

            # Put into breakdown
            issue_type = entry["fields"]["issuetype"]["name"]
            if issue_type not in break_down:
                break_down[issue_type] = {}

            # Merge duplicates by summary
            if summary in break_down[issue_type]:
                break_down[issue_type][summary].append(entry["key"])
            else:
                break_down[issue_type][summary] = [entry["key"]]

        # Rebuild with merged issue links
        for issue_type in break_down:
            formatted_entries = []
            for summary, keys in break_down[issue_type].items():
                if len(keys) == 1:
                    issues_text = f"(Issue https://issues.opennms.org/browse/{keys[0]}[{keys[0]}])"
                else:
                    links = ", ".join(
                        f"https://issues.opennms.org/browse/{k}[{k}]" for k in keys
                    )
                    issues_text = f"(Issues {links})"
                formatted_entries.append(f"{summary} {issues_text}")
            break_down[issue_type] = formatted_entries

        if show_output:
            print("[[releasenotes-changelog-"+release+"]]")
            print()
        if "Meridian" in release:
            release_year=int(release.split("-")[1].split(".")[0])
            meridian=True
        else:
            release_year=int(release.split(".")[0])
            horizon=True

        if (meridian and release_year<=2020) or (horizon and release_year<=29):
            _tmp="="*4
        else:
            _tmp="="*2
        if show_output:
            print(_tmp+" Release "+release)
            print()
            print()
        for entry in break_down:
            if (meridian and release_year<=2020) or (horizon and release_year<=29):
                _tmp="="*5
            else:
                _tmp="="*3
            if show_output:
                print(_tmp+" "+entry)
                print()
                for entry_2 in break_down[entry]:
                    print("*",entry_2)
                print()

        if output_filename:
            with open(output_filename,"w") as f:
                f.write("[releasenotes-changelog-"+release+"]\n")
                f.write("= Release "+release+"\n")
                f.write("\n")
                f.write("\n")
                for entry in break_down:
                    f.write("== "+entry+"\n")
                    for entry_2 in break_down[entry]:
                        f.write("* "+entry_2+"\n")
                    f.write("\n")

    def print_closed_issues(self, filename, prefix="*"):
        import json
        with open(filename, "r") as f:
            data = json.load(f)
    
        issues = data.get("invalid_closed_issues", [])
        if not issues:
            print("✅ All closed issues have fixVersion and GitHub references.")
            return
    
        print("❌ Closed issues with problems:")
        for issue in issues:
            key = issue.get("key", "UNKNOWN")
            summary = issue.get("fields", {}).get("summary", "")
            reason = issue.get("check_error", "Unknown error")
            print(f"{prefix} {key}: {summary} → {reason}")
    