import ssl
from src.client.ChunkedEncodingHandler import ChunkedEncodingHandler
from src.common.HttpRequest import HttpRequest
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

        if content_length is None:
            while True:
                current = s.recv(1024)
                if len(current) == 0:
                    return response
                response += current
        elif content_length == -1:
            # Handle chunked.
            chunked_handler = ChunkedEncodingHandler()
            early_received_chunk = response[headers_length + len(b"\r\n\r\n"):]
            response = response[:headers_length + len(b"\r\n\r\n")]
            if len(early_received_chunk) > 0:
                chunked_handler.add_data(early_received_chunk)

            while not chunked_handler.is_complete:
                chunked_handler.add_data(s.recv(1024))
            return response + b''.join(chunked_handler.chunks)
        else:
            # We have content-length specified. So keep reading until we complete
            # the incoming data.
            expected_total_length = headers_length + len("\r\n\r\n") + content_length
            while len(response) < expected_total_length:
                current = s.recv(1024)
                response += current
            return response

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
        raw_http: str = request.method.name + " " + request.file_name + " HTTP/1.1\r\n"
        raw_http += "Host: " + request.host_name + "\r\n"
        # TODO: Add optional headers on the form of `header_name: value` followed by CRLF
        raw_http += "\r\n"
        return raw_http
