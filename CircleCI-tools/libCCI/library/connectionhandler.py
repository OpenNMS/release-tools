import requests

class connectionhandler:
    def __init__(self) -> None:
        self._session=requests.Session()

    def getPage(self,_url):
        return self._session.get(_url).text


    def connect(self,_url,token):
        return self._session.get(_url,headers={'Accept': 'application/json',
                                               'Content-Type': 'application/json',
                                               'Circle-Token': token})
