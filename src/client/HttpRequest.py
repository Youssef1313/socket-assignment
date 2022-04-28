from argparse import ArgumentError
from client.HttpMethod import HttpMethod


class HttpRequest:
    def __init__(
            self,
            method: HttpMethod,
            file_name: str,
            host_name: str,
            port_number: int):
        if method is not HttpMethod.GET and method is not HttpMethod.POST:
            raise ArgumentError("Invalid HttpMethod.")

        self.method = method
        self.file_name = file_name
        self.host_name = host_name
        self.port_number = port_number
