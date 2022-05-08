from src.client.HttpRequest import HttpRequest
from src.common.HttpMethod import HttpMethod


class InputParser:
    @staticmethod
    def parse_input(input: str) -> list[HttpRequest]:
        commands = input.splitlines()
        requests: list[HttpRequest] = []
        for command in commands:
            # GET|POST file-name host-name optional-port
            command_parts = command.split()
            if len(command_parts) not in [3, 4]:
                raise ValueError(f"The command '{command}' is not valid.")
            method: HttpMethod = None
            if command_parts[0] == "GET":
                method = HttpMethod.GET
            elif command_parts[0] == "POST":
                method = HttpMethod.POST
            else:
                raise ValueError(f"The command '{command}' has invalid method '{command_parts[0]}'.")

            file_name: str = command_parts[1]
            host_name: str = command_parts[2]
            port_number: int = None
            if len(command_parts) == 4:
                port_number = int(command_parts[3])

            requests.append(HttpRequest(method, file_name, host_name, port_number))
        return requests
