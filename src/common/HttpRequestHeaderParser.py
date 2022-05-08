from src.common.HttpParser import HttpParser
from src.common.HttpVersion import HttpVersion


class HttpRequestHeaderParser(HttpParser):
    def parse(self):
        self.method = self._parse_method()
        self._eat_required(b' ')
        self.url = self._parse_until_space()
        self._eat_required(b' ')
        self._eat_required(b'HTTP/1.')
        if self._current_byte() == b'0':
            self.version = HttpVersion.HTTP_1_0
            self.position += 1
        elif self._current_byte() == b'1':
            self.version = HttpVersion.HTTP_1_1
            self.position += 1
        else:
            raise ValueError("Unexpected HTTP version.")
        self._eat_required(b'\r\n')

        self._parse_headers_and_newline()
