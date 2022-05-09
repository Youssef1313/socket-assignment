import os
import socket
import threading
from src.common.HttpMethod import HttpMethod
from src.common.HttpVersion import HttpVersion
from src.common.helpers import first_receive
from src.server.HttpRequestHeaderParser import HttpRequestHeaderParser


class WebServer:
    def __init__(self, port: int):
        self.host: str = 'localhost'
        self.port: int = port
        self.server_path: str = os.path.dirname(__file__)

    @staticmethod
    def get_path(file_name: str) -> str:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "./" + file_name))

    @staticmethod
    def create_file(file_name: str, file_content: bytes) -> None:
        file_name = WebServer.get_path(file_name)
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        with open(file_name, 'wb') as f:
            f.write(file_content)

    @staticmethod
    def get_request_method(request: bytes) -> bytes:
        headers = request.split(b'\r\n')
        method = headers[0].split()[0]
        return method

    @staticmethod
    def get_filename(url: bytes) -> str:
        # TODO: This can be absolute or relative.
        return url.decode()

    @staticmethod
    def response_get(filename: str) -> bytes:
        filename = WebServer.get_path('index.html' if filename == '/' else filename)

        try:
            with open(filename, 'rb') as file:
                content = file.read()
                error_code_and_name = b"200 OK"
        except IOError:
            filename = WebServer.get_path('error.html')
            with open(filename, 'rb') as file:
                content = file.read()
            error_code_and_name = b"404 Not Found"
        # https://datatracker.ietf.org/doc/html/rfc2616#section-6
        response = b"HTTP/1.1 " + error_code_and_name + b" \r\n"
        response += b"Content-Length: " + str(len(content)).encode() + b"\r\n"
        # Add any more headers here.
        response += b"\r\n"
        response += content
        return response

    @staticmethod
    def response_post(content: bytes) -> bytes:
        response = b"HTTP/1.1 201 Created\r\n"
        # https://datatracker.ietf.org/doc/html/rfc7231#section-6.3.2
        # The primary resource created by the request is identified
        # by either a Location header field in the response or, if no Location
        # field is received, by the effective request URI.
        response += b"Content-Length: " + str(len(content)).encode() + b"\r\n"
        response += b"\r\n"
        response += content
        return response

    def init_server(self) -> None:
        # Create Socket
        # AF_INET used for (host, port) address format with ipv4 host address
        socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            socket_server.bind((self.host, self.port))
            # Queue incoming requests
            socket_server.listen()
            print(f"Listening on {self.host} PORT: {self.port}.....")

            while True:
                # Accepting and receiving client requests
                (client_conn, client_address) = socket_server.accept()
                thread = threading.Thread(target=self.handle_request, args=(client_conn, client_address))
                thread.start()
        except KeyboardInterrupt:
            print("\n Shutting down server...\n")
        except Exception as exp:
            print(exp)
        socket_server.close()

    def handle_request(self, client_connection: socket.socket, client_address):
        print("Client connection opened")

        try:
            headers_body = first_receive(client_connection)
        except ConnectionAbortedError:
            return
        headers = headers_body[0]
        body = headers_body[1]

        request_header_parser = HttpRequestHeaderParser(headers)
        request_header_parser.parse()

        content_length = request_header_parser.headers.get('content-length')
        if content_length is not None:
            expected_total_length = len(headers) + int(content_length)
            while len(headers) + len(body) < expected_total_length:
                body += client_connection.recv(1024)

        filename = self.get_filename(request_header_parser.url)
        if request_header_parser.method == HttpMethod.GET:
            response = self.response_get(filename)
        elif request_header_parser.method == HttpMethod.POST:
            WebServer.create_file(filename, body)
            response = self.response_post(body)
        else:
            response = b"HTTP/1.1 501 Not Implemented\r\n"
            response += b"Content-Length: 0\r\n"
            response += b"\r\n"

        client_connection.sendall(response)
        connection = request_header_parser.headers.get("connection").lower()
        if connection == "close" or (connection is None and request_header_parser.version == HttpVersion.HTTP_1_0):
            client_connection.close()

        print("Client connection closed")
