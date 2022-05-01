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

        # Read Keep reading until we're sure we have all the headers.
        headers_length = -1
        while headers_length == -1:
            current: str = s.recv(1024).decode()
            response += current
            headers_length = response.find("\r\n\r\n")

        # Now that we have all headers, try to find content length.
        content_length = self.__find_content_length(response)
        print(f"Content length is {content_length}")

        if content_length == -1:
            # Handle chunked.
            is_end = False
            while not is_end:
                current: str = s.recv(1024).decode()
                chunk_size = self.__get_chunk_size(current)
                is_end = current.endswith('0\r\n\r\n')
                # Chunk starts with its size, in hex format, followed by \r\n.
                # Then the chunk itself, then another \r\n.
                # For this simple client, we will not verify the size.
                # We just do a simple slicing.
                #start_of_chunk = current.index('\r\n') + len('\r\n')
                #current = current[start_of_chunk:len(current) - len('\r\n')]
                response += current
        else:
            # We have content-length specified. So keep reading until we complete
            # the incoming data.
            expected_total_length = headers_length + len("\r\n\r\n") + content_length
            while len(response) < expected_total_length:
                current: str = s.recv(1024).decode()
                response += current

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

    def __get_chunk_size(self, data: str):
        chunk_size_hex = ""
        for c in data:
            if c.lower() in "0123456789abcdef":
                chunk_size_hex += c
            else:
                break

        if chunk_size_hex == "":
            raise ValueError("Expected hex number in beginning of a chunk.")
        if data[len(chunk_size_hex):len(chunk_size_hex) + len('\r\n')] != '\r\n':
            raise ValueError("Expected \r\n after hex chunk size.")

        return int(chunk_size_hex, 16)
