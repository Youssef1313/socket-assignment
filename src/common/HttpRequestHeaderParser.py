from src.common.HttpParser import HttpParser
from src.common.HttpVersion import HttpVersion


class HttpRequestHeaderParser(HttpParser):
    def parse(self):
        self.method = self.__parse_method()
        self.__eat_required(b' ')
        self.url = self.__parse_until_space()
        self.__eat_required(b' ')
        self.__eat_required(b'HTTP/1.')
        if self.__current_byte() == '0':
            self.version = HttpVersion.HTTP_1_0
        elif self.__current_byte() == '1':
            self.version = HttpVersion.HTTP_1_1
        else:
            raise ValueError("Unexpected HTTP version.")
        self.__eat_required(b'\r\n')

        self.__parse_headers_and_newline()
