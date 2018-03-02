from event import Event, EventBag


class AuthFlowEvents(EventBag):
    class HostRequestMade(Event):
        def __init__(self, host_request):
            self.host_request = host_request

    class HostMade(Event):
        def __init__(self, host):
            self.host = host