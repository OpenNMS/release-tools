from connectionhandler import connectionhandler
from grafana import Grafana
from semver import Semver
import os


semver=Semver()
connection_handler=connectionhandler()
grafana=Grafana(connection_handler)


if os.path.exists("downloads/version"):
    with open("downloads/version","r") as f:
        Our_Current_Version=f.read().strip()
else:
    Our_Current_Version="9.5.2"
Our_Current_Package="rpm"
Our_Current_Arch="amd64"
Download_Location="downloads"

print("Latest Grafana we have downloaded "+Our_Current_Version)
#print(grafana.GetVersions())
#print(grafana.GetLatestVersion())
#version=grafana.GetLatestVersion(current_version=Our_Current_Version,keep_current_major=False)
#print(version)
version=grafana.GetLatestVersion(current_version=Our_Current_Version,keep_current_major=True)
print("Latest Grafana release "+version)
print()
#print(version)
#print(grafana.CompareVersions(Our_Current_Version,version))
if Our_Current_Version != grafana.CompareVersions(Our_Current_Version,version):
    print("We will download Grafana version "+version)
    grafana.DownloadPackage(version,package_type="rpm",package_arch="amd64",download_folder="downloads")
else:
    print("Won't download Grafana version "+version)
