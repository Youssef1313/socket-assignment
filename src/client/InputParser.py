from src.client.HttpRequest import HttpRequest
from src.client.HttpMethod import HttpMethod
from src.client.ParsingState import ParsingState


class InputParser:
    def __init__(self, input: str) -> None:
        self.input = input
        self.position = 0

    def __reached_end(self) -> bool:
        return self.position >= len(self.input)

    def __eat_required(self, token: str, error: str) -> None:
        if self.input[self.position:self.position + len(token)] == token:
            self.position += len(token)
            return
        raise ValueError(error)

    def __parse_method(self) -> HttpMethod:
        if self.input[self.position:self.position + len("GET")].upper() == "GET":
            self.position += len("GET")
            return HttpMethod.GET
        elif self.input[self.position:self.position + len("POST")].upper() == "POST":
            self.position += len("POST")
            return HttpMethod.POST
        raise ValueError(f"Expected a GET or POST method at position '{self.position}'.")

    def __parse_string(self) -> str:
        start_index = self.position
        while (not self.__reached_end() and
               self.input[self.position] != ' ' and
               self.input[self.position] != '\r'):
            self.position += 1
        return self.input[start_index:self.position]

    def __try_parse_port(self) -> int:
        start_index = self.position
        while (not self.__reached_end() and
               self.input[self.position].isdigit()):
            self.position += 1
        if start_index == self.position:
            # No digits were found. The port is optional, so we
            # don't throw an exception. Instead, we return None.
            return None

        return int(self.input[start_index:self.position])

    def parse_input(self) -> list[HttpRequest]:
        class ParseData:
            method: HttpMethod = None
            host_name: str = None
            file_name: str = None
            port_number: int = None

            def clear(self) -> None:
                self.method = None
                self.host_name = None
                self.file_name = None
                self.port_number = None

            def to_request(self) -> HttpRequest:
                return HttpRequest(self.method, self.file_name, self.host_name, self.port_number)

        state: ParsingState = ParsingState.EXPECTING_HTTP_METHOD
        requests: list[HttpRequest] = []
        data: ParseData = ParseData()

        while not self.__reached_end():
            if state == ParsingState.EXPECTING_HTTP_METHOD:
                data.method = self.__parse_method()
                self.__eat_required(" ", "A space is expected after Http method.")
                state = ParsingState.EXPECTING_FILE_NAME
            elif state == ParsingState.EXPECTING_FILE_NAME:
                data.file_name = self.__parse_string()
                self.__eat_required(" ", "A space is expected after file name.")
                state = ParsingState.EXPECTING_HOST_NAME
            elif state == ParsingState.EXPECTING_HOST_NAME:
                data.host_name = self.__parse_string()
                state = ParsingState.EXPECTING_OPTIONAL_PORT_NUMBER
            elif state == ParsingState.EXPECTING_OPTIONAL_PORT_NUMBER:
                if self.input[self.position] == " ":
                    # When parsing the host name, we don't eat the space.
                    # If there is a space, then we expect a port number.
                    # We increment position to eat the space and parse the port.
                    self.position += 1
                    data.port_number = self.__try_parse_port()
                else:
                    # If there is no space, then the port number was omitted.
                    data.port_number = None
                # Whether a port number was specified or not, a crlf (or end of file) must be found.
                if not self.__reached_end():
                    self.__eat_required("\r\n", f"Expected CRLF at position '{self.position}'.")
                state = ParsingState.EXPECTING_OPTIONAL_HEADERS
            elif state == ParsingState.EXPECTING_OPTIONAL_HEADERS:
                # Not yet implemented.
                requests.append(data.to_request())
                data.clear()
                state = ParsingState.EXPECTING_HTTP_METHOD

        # The whole file is now consumed.
        if (state == ParsingState.EXPECTING_OPTIONAL_PORT_NUMBER or
                state == ParsingState.EXPECTING_OPTIONAL_HEADERS):  # TODO: Other optional states.
            requests.append(data.to_request())
            state = ParsingState.EXPECTING_HTTP_METHOD

        if state != ParsingState.EXPECTING_HTTP_METHOD:
            raise ValueError(f"Reached end of file at state '{state.name}'.")
        return requests
