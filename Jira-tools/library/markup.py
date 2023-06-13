
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
                        print(prefix,entry["key"],entry["fields"]["summary"])
                    else:
                        print(prefix,entry,entry["fields"]["Summary"])
                else:
                    print(prefix,entry,data[entry]["Summary"])
            else:
                print(entry,entry["Summary"])

    def print_issues(self,filename,release="",output_filename=""):
        meridian=False
        horizon=False
        with open(filename,"r") as f:
            data=json.load(f)

        break_down={}
        
        for entry in data["issues"]:
            issue_type=entry["fields"]["issuetype"]["name"]
            if  issue_type not in break_down:
                break_down[issue_type]=[]
            
            break_down[issue_type].append(entry["fields"]["summary"] +" (Issue https://issues.opennms.org/browse/"+entry["key"]+"["+entry["key"]+'])')

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
        print(_tmp+" Release "+release)
        print()
        print()
        for entry in break_down:
            if (meridian and release_year<=2020) or (horizon and release_year<=29):
                _tmp="="*5
            else:
                _tmp="="*3
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
                    
                    
