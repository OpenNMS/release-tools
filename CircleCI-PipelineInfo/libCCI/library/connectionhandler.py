import requests


class connectionhandler:
    def __init__(self) -> None:
        self._session = requests.Session()

    def getPage(self, _url):
        return self._session.get(_url).text

    def connect(self, _url, token, data):
        if data:
            return self._post_connect(_url, token, data)
        else:
            return self._session.get(
                _url,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Circle-Token": token,
                },
            )

    def _post_connect(self, _url, token, data):
        print(data)
        return self._session.post(
            _url,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Circle-Token": token,
            },
            json=data,
        )

    def option_connect(self, _url, token):
        return self._session.options(
            _url,
            headers={
                "Accept": "*/*",
                "Host": "circleci.com",
                "Origin": "https://app.circleci.com",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
                "Content-Type": "application/json",
                "Circle-Token": token,
            },
        )
