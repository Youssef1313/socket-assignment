import ssl
from src.client.ChunkedEncodingHandler import ChunkedEncodingHandler
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
            with open('C:\\received.txt', 'w', encoding="utf-8") as f:
                f.write(data)
            #print(data)

    def __send_receive(self, s: socket.socket, data: str) -> str:
        s.sendall(bytes(data, encoding="utf-8"))
        response: bytes = b""

        # Read Keep reading until we're sure we have all the headers.
        headers_length = -1
        while headers_length == -1:
            current: bytes = s.recv(1024)
            response += current
            headers_length = response.find(b"\r\n\r\n")

        # Now that we have all headers, try to find content length.
        content_length = self.__find_content_length(response)
        print(f"Content length is {content_length}")

        if content_length == -1:
            # Handle chunked.
            chunked_handler = ChunkedEncodingHandler()
            while not chunked_handler.is_complete:
                chunked_handler.add_data(s.recv(1024))
            return ''.join(chunked_handler.chunks)
        else:
            # We have content-length specified. So keep reading until we complete
            # the incoming data.
            expected_total_length = headers_length + len("\r\n\r\n") + content_length
            while len(response.encode()) < expected_total_length:
                current: str = s.recv(1024).decode()
                response += current
            return response.decode()

    def __find_content_length(self, data: bytes) -> int:
        lines = data.split(b"\r\n")
        for line in lines:
            if line == b"":
                break
            if line.lower().startswith(b"content-length: "):
                return int(line[len(b"content-length: "):].decode())
            if line.lower() == b"transfer-encoding: chunked":
                return -1

    def __get_raw_http(self, request: HttpRequest) -> str:
        raw_http: str = request.method.name + " " + request.get_url() + " HTTP/1.1\r\n"
        raw_http += "Host: " + request.host_name + "\r\n"
        # TODO: Add optional headers on the form of `header_name: value` followed by CRLF
        raw_http += "\r\n"
        return raw_http
