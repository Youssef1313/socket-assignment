import os
import socket
import threading
from urllib.parse import urlparse
from src.common.HttpMethod import HttpMethod
from src.common.HttpVersion import HttpVersion
from src.common.helpers import first_receive
from src.server.HttpRequestHeaderParser import HttpRequestHeaderParser
from src.server.SocketTracker import SocketTracker


class WebServer:
    def __init__(self, port: int):
        self.host: str = 'localhost'
        self.port: int = port
        self.server_path: str = os.path.dirname(__file__)
        self.socket_tracker = SocketTracker()

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
        return urlparse(url.decode()).path

    @staticmethod
    def get_status_and_content_of_file(filename: str) -> tuple[bytes, bytes]:
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
        return (error_code_and_name, content)

    @staticmethod
    def get_raw_http_response(error_code_and_name: bytes, content: bytes, should_close: bool) -> bytes:
        # https://datatracker.ietf.org/doc/html/rfc2616#section-6
        response = b"HTTP/1.1 " + error_code_and_name + b"\r\n"
        response += b"Content-Length: " + str(len(content)).encode() + b"\r\n"
        if should_close:
            response += b"Connection: close\r\n"
        # Add any more headers here.
        response += b"\r\n"
        response += content
        return response

    def init_server(self) -> None:
        # Create Socket
        # AF_INET used for (host, port) address format with ipv4 host address
        socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
        while True:  # TODO: Handle closing idle connections..
            try:
                self.socket_tracker.use_socket(client_connection)
                headers_body = first_receive(client_connection)
            except OSError:
                # We get here if the connection got closed due to inactivity.
                # We don't want to call kill_socket here. The socket is already killed.
                return

            if headers_body is None:
                self.socket_tracker.kill_socket(client_connection)
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
            connection = request_header_parser.headers.get("connection")
            should_close = connection == "close" or (connection is None and request_header_parser.version == HttpVersion.HTTP_1_0)
            if request_header_parser.method == HttpMethod.GET:
                status_content = WebServer.get_status_and_content_of_file(filename)
                response = WebServer.get_raw_http_response(status_content[0], status_content[1], should_close)
            elif request_header_parser.method == HttpMethod.POST:
                WebServer.create_file(filename, body)
                response = WebServer.get_raw_http_response(b"201 Created", body, should_close)
            else:
                response = WebServer.get_raw_http_response(b"501 Not Implemented", b"", should_close)

            client_connection.sendall(response)
            if should_close:
                self.socket_tracker.kill_socket(client_connection)
                return
