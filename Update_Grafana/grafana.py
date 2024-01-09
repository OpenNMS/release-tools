import json
from semver import Semver

class Grafana:
    _URL_GRAFANA_VERSIONS="https://grafana.com/api/grafana/versions"
    _URL_GRAFANA_PACKAGE="https://grafana.com/api/grafana/versions/##_REPLACE_ME_WITH_VERSION_##/packages"

    _https_connector=None

    _GRAFANA_VERSIONS=[]
    _GRAFANA_TMP_DATA={}

    _SEMVERSION=None


    def __init__(self,https_connector) -> None:
        self._https_connector=https_connector
        self._SEMVERSION=Semver()

    def GetVersions(self) -> list:
        if len(self._GRAFANA_VERSIONS)>0:
            return self._GRAFANA_VERSIONS
        
        stable_versions=json.loads(self._https_connector.getPage("https://grafana.com/api/grafana/versions"))
        self._GRAFANA_TMP_DATA=stable_versions
        for entry in stable_versions["items"]:
            self._GRAFANA_VERSIONS.append(entry["version"])
        
        return self._GRAFANA_VERSIONS
    
    def GetLatestVersion(self,current_version="",keep_current_major=False) -> str:
        if not current_version or not keep_current_major:
            return self.GetVersions()[0]
        
        s1=self._SEMVERSION.Parse(current_version)
        for version in self.GetVersions():
            s2=self._SEMVERSION.Parse(version)
            if keep_current_major:
                if int(s1[0]) == int(s2[0]):
                    if int(s1[1]) >= int(s2[1]) and int(s1[2]) <= int(s2[2]):
                        return version
                    
    def CompareVersions(self,version1,version2):
        s1=self._SEMVERSION.Parse(version1)
        s2=self._SEMVERSION.Parse(version2)
        item=version1 #Assume version1 is always bigger
        major_match=False
        minor_match=False
        patch_match=False
        if int(s1[0]) > int(s2[0]):
            print("Version1 ("+version1+") Major ("+s1[0]+") is bigger than Version2 ("+version2+") Major ("+s2[0]+")")
            return item
        if int(s1[0]) == int(s2[0]):
            print("Version1 ("+version1+") Major ("+s1[0]+") is equal to Version2 ("+version2+") Major ("+s2[0]+")")
            major_match=True
        else:
            print("Version1 ("+version1+") Major ("+s1[0]+") is smaller than Version2 ("+version2+") Major ("+s2[0]+")")
            item=version2

        if int(s1[1]) > int(s2[1]):
            print("Version1 ("+version1+") Minor ("+s1[1]+") is bigger than Version2 ("+version2+") Major ("+s2[1]+")")
            return item
        if int(s1[1]) == int(s2[1]):
            print("Version1 ("+version1+") Minor ("+s1[1]+") is equal to Version2 ("+version2+") Major ("+s2[1]+")")
            minor_match=True
        else:
            print("Version1 ("+version1+") Minor ("+s1[1]+") is smaller than Version2 ("+version2+") Major ("+s2[1]+")")
            item=version2

        if int(s1[2]) > int(s2[2]):
            print("Version1 ("+version1+") Patch ("+s1[2]+") is bigger than Version2 ("+version2+") Major ("+s2[2]+")")
            return item
        if int(s1[2]) == int(s2[2]):
            print("Version1 ("+version1+") Patch ("+s1[2]+") is equal to Version2 ("+version2+") Major ("+s2[2]+")")
        else:
            print("Version1 ("+version1+") Patch ("+s1[2]+") is smaller than Version2 ("+version2+") Major ("+s2[2]+")")
            item=version2
        
        return item

    def DownloadPackage(self,version,package_type="rpm",package_arch="amd64",download_folder="downloads")->None:
        package_content=json.loads(self._https_connector.getPage("https://grafana.com/api/grafana/versions/"+version+"/packages"))
        for pkg in package_content["items"]:
            _pkg_url=pkg["url"]
            _pkg_sha=pkg["sha256"].strip()
            if package_type in _pkg_url:
                filename=_pkg_url.split("/")[-1]
                self._https_connector.download_file(_pkg_url,download_folder+"/"+filename)
                with open(download_folder+"/version","w") as f:
                    f.write(version)
                with open(download_folder+"/"+filename+".sha256","w") as f:
                    outputdata=_pkg_sha+" "+filename
                    f.write(outputdata)
                    f.flush()
                with open(download_folder+"/"+filename.replace(".rpm","")+".json","w") as f:
                    json.dump(pkg,f,indent=4)
                break


        

        
