import ssl
from src.client.HttpResponseHeaderParser import HttpResponseHeaderParser
from src.client.ChunkedEncodingHandler import ChunkedEncodingHandler
from src.client.HttpRequest import HttpRequest
from src.common.helpers import first_receive
import socket


class WebClient:
    def send_request(self, request: HttpRequest) -> None:
        raw_http = self.__get_raw_http(request)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if request.port_number == 443:
                # https uses port 443, and needs special handling.
                ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
                with ssl_context.wrap_socket(s, server_hostname=request.host_name) as ssl_socket:
                    ssl_socket.connect((request.host_name, request.port_number))
                    data = self.__send_receive(ssl_socket, raw_http)
            else:
                s.connect((request.host_name, request.port_number))
                data = self.__send_receive(s, raw_http)
            path = f"C:\\received-{request.host_name}.txt"
            print(f"Writing response in '{path}'")
            with open(path, 'wb') as f:
                f.write(data)

    def __send_receive(self, s: socket.socket, data: str) -> bytes:
        s.sendall(bytes(data, encoding="utf-8"))

        headers_body = first_receive(s)
        headers = headers_body[0]
        body = headers_body[1]

        response_header_parser = HttpResponseHeaderParser(headers)
        response_header_parser.parse()

        content_length = response_header_parser.headers.get("content-length")
        transfer_encoding = response_header_parser.headers.get("transfer-encoding")
        if content_length is not None:
            content_length = int(content_length)
            # We have content-length specified. So keep reading until we complete
            # the incoming data.
            expected_total_length = len(headers) + content_length
            while len(headers) + len(body) < expected_total_length:
                current = s.recv(1024)
                body += current
            return headers + body
        elif transfer_encoding is not None and transfer_encoding.lower() == "chunked":
            # Handle chunked.
            chunked_handler = ChunkedEncodingHandler()

            if len(body) > 0:
                chunked_handler.add_data(body)

            while not chunked_handler.is_complete:
                chunked_handler.add_data(s.recv(1024))
            return headers + b''.join(chunked_handler.chunks)
        else:
            while True:
                current = s.recv(1024)
                if len(current) == 0:
                    return headers + body
                body += current

    def __get_raw_http(self, request: HttpRequest) -> str:
        raw_http: str = request.method.name + " " + request.file_name + " HTTP/1.1\r\n"
        raw_http += "Host: " + request.host_name + "\r\n"
        # TODO: Add optional headers on the form of `header_name: value` followed by CRLF
        raw_http += "\r\n"
        return raw_http
