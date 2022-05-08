from src.common.HttpParser import HttpParser
from src.common.HttpVersion import HttpVersion


class HttpResponseHeaderParser(HttpParser):
    def parse(self):
        # HTTP/1.x STATUS_CODE STATUS_NAME\r\n
        # Headers\r\n

        self._eat_required(b'HTTP/1.')
        if self._current_byte() == b'0':
            self.version = HttpVersion.HTTP_1_0
            self.position += 1
        elif self._current_byte() == b'1':
            self.version = HttpVersion.HTTP_1_1
            self.position += 1
        else:
            raise ValueError("Unexpected HTTP version.")
        self._eat_required(b' ')

        self.status_code = int(self._parse_until_space().decode())
        self._eat_required(b' ')
        # ignore status name by eating it and the new line next to it.
        self._parse_until_token(b'\r\n')
        self._eat_required(b'\r\n')

        self._parse_headers_and_newline()
