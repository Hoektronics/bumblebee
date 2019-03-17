from bumblebee.host.api.rest import RestApi
from bumblebee.host.api.socket import WebSocketApi


class ErrorResponse(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        
        super(ErrorResponse, self).__init__(f"Error {code}: {message}")


class BotQueueApi(object):
    def __init__(self,
                 rest_api: RestApi,
                 websocket_api: WebSocketApi):
        self.rest_api = rest_api
        self.websocket_api = websocket_api

    def command(self, name, data):
        if not self.websocket_api.connected:
            response = self.rest_api.post("/host", {
                "command": name,
                "data": data
            })

            response_json = response.json()

            if response.ok:
                return response_json["data"]
            else:
                raise ErrorResponse(
                    code=response_json["code"],
                    message=response_json["message"]
                )