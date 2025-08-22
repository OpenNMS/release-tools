import requests

class web_connector:
    def __init__(self) -> None:
        self._session=requests.Session()
    
    def get(self,url,header="",param="",auth="") -> None:
        return self._session.get(url,headers=header,params=param,auth=auth)
    
    def post(self,url,data,header="",param="",auth="") -> None:
        return self._session.post(url,data,headers=header,params=param,auth=auth)

    def printCookies(self):
        print(self._session.cookies.get_dict())
