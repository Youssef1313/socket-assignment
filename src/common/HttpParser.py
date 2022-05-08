from src.common.HttpMethod import HttpMethod
from src.common.HttpVersion import HttpVersion


class HttpParser:
    def __init__(self, raw_http: bytes):
        self.position: int = 0
        self.raw_http: bytes = raw_http
        self.headers: dict[str, str] = {}
        self.method: HttpMethod = None
        self.url: bytes = None
        self.version: HttpVersion = None
        self.body: bytes = b""

    def __reached_end(self) -> bool:
        return self.position >= len(self.raw_http)

    def __current_byte(self) -> bytes:
        return self.raw_http[self.position:self.position + 1]

    def __eat_required(self, token: bytes):
        if not self.__has_current_token(token):
            raise ValueError(f"Cannot find required token '{token.decode()}'.")
        self.position += len(token)

    def __has_current_token(self, token: bytes):
        return self.raw_http[self.position:self.position + len(token)] == token

    def __parse_until_space(self) -> bytes:
        return self.__parse_until_token(b' ')

    def __parse_until_token(self, token: bytes) -> bytes:
        end = self.position
        while not self.__reached_end() and self.__current_byte() != token:
            end += 1
        if self.position == end:
            raise ValueError("Error parsing until token.")

    def __parse_method(self) -> HttpMethod:
        if self.__has_current_token(b"GET"):
            return HttpMethod.GET
        elif self.__has_current_token(b"POST"):
            return HttpMethod.POST
        raise ValueError("GET/POST method was expected.")

    def __parse_header(self):
        header_name = self.__parse_until_token(b': ')
        self.__eat_required(b': ')
        header_value = self.__parse_until_token(b'\r\n')
        self.__eat_required(b'\r\n')
        return (header_name, header_value)

    def __parse_headers_and_newline(self):
        while not self.__has_current_token('\r\n'):
            header = self.__parse_header()
            header_name = header[0]
            header_value = header[1]
            self.headers[header_name.decode().lower()] = header_value.decode()
        self.__eat_required(b'\r\n')
