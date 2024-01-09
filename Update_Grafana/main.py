from connectionhandler import connectionhandler
from semver import Semver
import json 
import os

#def compare_semvers(input1,input2):
#    s1=semver.Parse(input1)
#    s2=semver.Parse(input2)
#    if s1[0] == s2[0]:
#        print("Major matches")
#    elif s1[0] > s2[0]:
#        print("s1 Major higher")
#    elif s1[0] < s2[0]:
#        print("s2 Major higher")


semver=Semver()
x=connectionhandler()
stable_versions=json.loads(x.getPage("https://grafana.com/api/grafana/versions"))
if os.path.exists("downloads/version"):
    with open("downloads/version","r") as f:
        Our_Current_Version=f.read().strip()
else:
    Our_Current_Version="9.5.2"
Our_Current_Package="rpm"
Our_Current_Arch="amd64"
Download_Location="downloads"

latest_packages=""

s1=semver.Parse(Our_Current_Version)
for entry in stable_versions["items"]:
    s2=semver.Parse(entry["version"])
    if s1[0] == s2[0] and entry["channels"]["stable"]:
        if s1[1] == s2[1] or s1[1] <s2[1]:
            if s1[2] <s2[2]:
                print(entry["id"],entry["product"],entry["version"],entry["releaseDate"])
                for p in entry["links"]:
                    package_content=json.loads(x.getPage("https://grafana.com/api/grafana/versions/"+entry["version"]+"/packages"))
                    for pl in package_content["items"]:
                        if pl["os"] == "rhel" and Our_Current_Package in pl["url"] and Our_Current_Arch in pl["arch"]:
                            print("\t",pl["arch"],pl["archName"],pl["os"],pl["osName"],pl["url"],pl["sha256"])
                            latest_packages=pl["url"]
                            filelocation=pl["url"].split("/")[-1]
                            x.download_file(latest_packages,Download_Location+"/"+filelocation)
                            with open(Download_Location+"/version","w") as f:
                                f.write(entry["version"])
                            with open(Download_Location+"/"+filelocation+".sha1","w") as f:
                                outputdata=pl["sha256"].strip()+" "+filelocation
                                f.write(outputdata)
                                f.flush()
                            with open(Download_Location+"/"+filelocation.replace(".rpm","")+".info","w") as f:
                                json.dump(entry,f,indent=4)
                            latest_packages=Download_Location+"/"+filelocation
                            break
                    if latest_packages:
                        break
                break
