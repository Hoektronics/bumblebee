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
        self._rest_api = rest_api
        self._websocket_api = websocket_api

    def command(self, name, data=None):
        command = {
            "command": name
        }
        if data is not None:
            command["data"] = data

        if not self._websocket_api.connected:
            response = self._rest_api.post("/host", command)

            response_json = response.json()

            try:
                if response.ok:
                    return response_json["data"]
                else:
                    raise ErrorResponse(
                        code=response_json["code"],
                        message=response_json["message"]
                    )
            finally:
                if response is not None:
                    response.close()