import ssl
from src.client.HttpRequest import HttpRequest
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
            print("Received:")
            print(data)

    def __send_receive(self, s: socket.socket, data: str) -> str:
        s.sendall(bytes(data, encoding="utf-8"))
        response: str = ""

        headers_length = -1
        while True:
            current: str = s.recv(1024).decode()
            response += current
            if headers_length == -1:
                headers_length = response.find("\r\n\r\n")
                if headers_length != -1:
                    content_length = self.__find_content_length(response)
                    print(f"Content length is {content_length}")

            if content_length == -1:
                # Handle chunked.
                pass
            else:
                # end_of_headers_index
                expected_total_length = headers_length + len("\r\n\r\n") + content_length
                if len(response) >= expected_total_length:
                    break

    def __find_content_length(self, data: str) -> int:
        lines = data.split("\r\n")
        for line in lines:
            if line == "":
                break
            if line.lower().startswith("content-length: "):
                return int(line[len("content-length: "):])
            if line.lower() == "transfer-encoding: chunked":
                return -1

    def __get_raw_http(self, request: HttpRequest) -> str:
        raw_http: str = request.method.name + " " + request.get_url() + " HTTP/1.1\r\n"
        raw_http += "Host: " + request.host_name + "\r\n"
        # TODO: Add optional headers on the form of `header_name: value` followed by CRLF
        raw_http += "\r\n"
        return raw_http
