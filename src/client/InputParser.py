from client.HttpRequest import HttpRequest
from client.HttpMethod import HttpMethod
from client.ParsingState import ParsingState


class InputParser:
    def __init__(self, input: str) -> None:
        self.input = input
        self.position = 0

    def __reached_end(self) -> bool:
        return self.position > len(self.input)

    def __eat_required(self, tokens_to_eat: list[str], error: str) -> None:
        for token in tokens_to_eat:
            if self.input[self.position:self.position + len(token) + 1] == token:
                self.position += len(token)
                return
        raise ValueError(error)

    def __parse_method(self) -> HttpMethod:
        if self.input[self.position:self.position + len("GET") + 1].upper() == "GET":
            return HttpMethod.GET
        elif self.input[self.position:self.position + len("POST") + 1].upper() == "POST":
            return HttpMethod.POST
        raise ValueError(f"Expected a GET or POST method at position '{self.position}'.")

    def __parse_string(self) -> str:
        end_index = self.position
        while end_index < len(self.input) and self.input[end_index] != ' ' and self.input[end_index] != '\r':
            end_index += 1
        # TODO: end_index + 1?
        parsed_string = self.input[self.position:end_index]
        # The `+ 1` eats the space after the string.
        # TODO: + 2 for \r\n?
        self.position = end_index + 1
        return parsed_string

    def __try_parse_port(self) -> int:
        end_index = self.position
        while end_index < len(self.input) and self.input[end_index].isdigit():
            end_index += 1
        if end_index == self.position:
            # No digits were found. The port is optional, so we
            # don't throw an exception. Instead, we return None.
            return None
        # end_index + 1 ??
        self.position = end_index
        return int(self.input[self.position:end_index])

    def parse_input(self) -> list[HttpRequest]:
        state: ParsingState = ParsingState.EXPECTING_HTTP_METHOD
        requests: list[HttpRequest] = []

        method: HttpMethod
        host_name: str
        file_name: str
        port_number: int

        while not self.__reached_end():
            if state == ParsingState.EXPECTING_HTTP_METHOD:
                method = self.__parse_method()
                self.__eat_required([" "], "A space is expected after Http method.")
                state = ParsingState.EXPECTING_FILE_NAME
            elif state == ParsingState.EXPECTING_FILE_NAME:
                file_name = self.__parse_string()
                self.__eat_required([" "], "A space is expected after file name.")
                state == ParsingState.EXPECTING_HOST_NAME
            elif state == ParsingState.EXPECTING_HOST_NAME:
                host_name = self.__parse_string()
                state == ParsingState.EXPECTING_OPTIONAL_PORT_NUMBER
            elif state == ParsingState.EXPECTING_OPTIONAL_PORT_NUMBER:
                if self.input[self.position] == " ":
                    # When parsing the host name, we don't eat the space.
                    # If there is a space, then we expect a port number.
                    # We increment position to eat the space and parse the port.
                    self.position += 1
                    port_number = self.__try_parse_port()
                else:
                    # If there is no space, then the port number was omitted.
                    port_number = None
                # Whether a port number was specified or not, a crlf must be found.
                self.__eat_required(["\r\n"], f"Expected CRLF at position '{self.position}'.")
                state == ParsingState.EXPECTING_OPTIONAL_HEADERS
            elif state == ParsingState.EXPECTING_OPTIONAL_HEADERS:
                # Not yet implemented.
                requests.append(HttpRequest(method, file_name, host_name, port_number))
                state = ParsingState.EXPECTING_HTTP_METHOD

        if state != ParsingState.EXPECTING_HTTP_METHOD:
            raise ValueError(f"Reached end of file at state '{state.name}'.")
        return requests
