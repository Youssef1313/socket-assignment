from src.client.HttpResponseHeaderParser import HttpResponseHeaderParser
from src.client.ChunkedEncodingHandler import ChunkedEncodingHandler
from src.client.HttpRequest import HttpRequest
from src.client.SocketFactory import SocketFactory
from src.common.HttpMethod import HttpMethod
from src.common.HttpVersion import HttpVersion
from src.common.helpers import first_receive
import socket


class WebClient:
    def __init__(self):
        self.socket_factory = SocketFactory()

    def send_request(self, request: HttpRequest) -> None:
        raw_http = self.__get_raw_http(request)
        socket = self.socket_factory.get_or_create_socket(request.host_name, request.port_number)
        try:
            data = self.__send_receive(socket, raw_http, request)
        except ConnectionAbortedError:
            socket = self.socket_factory.create_socket(request.host_name, request.port_number)
            data = self.__send_receive(socket, raw_http, request)
        path = f"C:\\received-{request.host_name}.txt"
        print(f"Writing response in '{path}'")
        with open(path, 'wb') as f:
            f.write(data)

    def __send_receive(self, s: socket.socket, data: bytes, request: HttpRequest) -> bytes:
        s.sendall(data)
        headers_body = first_receive(s)
        headers = headers_body[0]
        body = headers_body[1]

        response_header_parser = HttpResponseHeaderParser(headers)
        response_header_parser.parse()

        content_length = response_header_parser.headers.get("content-length")
        transfer_encoding = response_header_parser.headers.get("transfer-encoding")
        connection = response_header_parser.headers.get("connection")
        should_close = connection == "close" or (connection is None and response_header_parser.version == HttpVersion.HTTP_1_0)
        if content_length is not None:
            content_length = int(content_length)
            # We have content-length specified. So keep reading until we complete
            # the incoming data.
            expected_total_length = len(headers) + content_length
            while len(headers) + len(body) < expected_total_length:
                current = s.recv(1024)
                body += current
            if should_close:
                self.socket_factory.remove_socket(request.host_name, request.port_number)
            return headers + body
        elif transfer_encoding is not None and transfer_encoding.lower() == "chunked":
            # Handle chunked.
            chunked_handler = ChunkedEncodingHandler()

            if len(body) > 0:
                chunked_handler.add_data(body)

            while not chunked_handler.is_complete:
                chunked_handler.add_data(s.recv(1024))
            if should_close:
                self.socket_factory.remove_socket(request.host_name, request.port_number)
            return headers + b''.join(chunked_handler.chunks)
        else:
            while True:
                current = s.recv(1024)
                if len(current) == 0:
                    if should_close:
                        self.socket_factory.remove_socket(request.host_name, request.port_number)
                    return headers + body
                body += current

    def __get_raw_http(self, request: HttpRequest) -> bytes:
        raw_http: bytes = request.method.name.encode() + b" " + request.file_name.encode() + b" HTTP/1.1\r\n"
        raw_http += b"Host: " + request.host_name.encode() + b"\r\n"
        if request.method == HttpMethod.POST:
            with open(request.file_name, "rb") as f:
                content = f.read()
            raw_http += b"Content-Length: " + str(len(content)).encode() + b"\r\n"
        # TODO: Add optional headers on the form of `header_name: value` followed by CRLF
        raw_http += b"\r\n"
        if request.method == HttpMethod.POST:
            raw_http += content
        return raw_http
