import requests

class MattermostHandler:
    def __init__(self, webhook_url, 
                 username="devops",
                 channel="devops-status",
                 icon_url="https://www.opennms.com/wp-content/uploads/2021/04/OpenNMS_Favicon_36px.png"):
        self.webhook_url = webhook_url
        self.username = username
        self.channel = channel
        self.icon_url = icon_url
    
    def post(self,message):
        payload={
            "text":message,
            "username": self.username,
            "channel": self.channel,
            "icon_url": self.icon_url
        }

        response = requests.post(self.webhook_url, json=payload)
        if response.status_code == 200:
            return "Message posted successfully!"
        else:
            return "Failed to post message: {response.status_code} - {response.text}"
