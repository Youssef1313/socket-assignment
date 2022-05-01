from argparse import ArgumentError
from src.client.HttpMethod import HttpMethod


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
        self.port_number = 80 if port_number is None else port_number

    def get_url(self) -> str:
        if (not self.file_name.startswith('/')
                and not self.host_name.endswith('/')):
            return self.host_name + "/" + self.file_name
        # TODO: Check if double slashes are okay.
        return "https://" + self.host_name + self.file_name
