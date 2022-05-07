import io
import socket
import pathlib
import base64
import re
from datetime import datetime


class WebServer:
    def __init__(self, port: int):
        self.host: str = 'localhost'
        self.port: int = port

    @staticmethod
    def check_img(filename: str):
        extension = pathlib.Path(filename).suffix[1:]
        if extension in ['jpg', 'jpeg', 'png', 'gif']:
            return [True, extension]
        return [False, extension]

    @staticmethod
    def create_file(data_type, payload):
        filename = f"{datetime.timestamp(datetime.now())}.{data_type}"
        output_file = open(filename, "w")
        output_file.write(payload)
        output_file.close()
        return filename

    @staticmethod
    def get_request_method(request: bytes) -> bytes:
        headers = request.split(b'\r\n')
        method = headers[0].split()[0]
        return method

    @staticmethod
    def get_filename(request: bytes) -> str:
        headers = request.split(b'\r\n')
        filename = headers[0].split()[1][1:]
        print("headers")
        print(headers)
        return filename.decode()

    @staticmethod
    def response_get(filename: str):
        # TODO: Send content-length.
        if filename == '/' or filename == '':
            filename = 'index.html'

        try:
            img_checker = WebServer.check_img(filename)

            if img_checker[0]:
                file = Image.open(filename, mode='r')
                file_bytes = io.BytesIO()
                file.save(file_bytes, format=img_checker[1])
                img_bytes = file_bytes.getvalue()
                img_data = (base64.b64encode(img_bytes))
                # TODO: Send raw bytes directly. Don't wrap in HTML or base64.
                content = f"<html><img src='data:image/{img_checker[1]};base64,{str(img_data)[2:]}/></html>"
                # file.show()    To show externally outside the browser
            else:
                file = open(filename)
                # TODO: Read as bytes.
                content = file.read()
            file.close()
            response = b'HTTP/1.0 200 OK\n\n' + content.encode() + b'\r\n'
        except IOError:
            filename = 'error.html'
            file = open(filename)
            content = file.read()
            file.close()
            response = b'HTTP/1.0 404 NOT FOUND\n\n' + content.encode() + b'\r\n'
        return response

    @staticmethod
    def response_post(request: bytes):
        # TODO: Parse HTTP properly.
        request: str = request.decode()
        content_length_regx = re.compile("Content-Length: (.*?)\r")
        content_length = int(content_length_regx.findall(request)[0])
        payload = request[-content_length:]

        content_type_regx = re.compile("Content-Type: (.*?)\r")
        content_type = str(content_type_regx.findall(request)[0])

        if content_type == 'application/json':
            file_path = WebServer.create_file('json', payload=payload)
        elif content_type == 'text/plain':
            file_path = WebServer.create_file('txt', payload=payload)
        elif content_type == 'text/html':
            file_path = WebServer.create_file('html', payload=payload)
        elif content_type.startswith('multipart/form-data'):
            return request

        response = 'HTTP/1.0 201 CREATED\n\n' + f'<html><body><h3>HTTP/1.0 201 CREATED</h3>' \
                                                f'<h3>Data successfully added</h3>' \
                                                f'<h4>check file named {file_path} in the server directory</h4>' \
                                                f'<p>data: {payload} ' \
                                                f'<br>Type: {content_type} <br>' \
                                                f'Length: {content_length}' \
                                                f'</p></body></html>'
        return response

    def init_server(self) -> None:
        # Create Socket
        # AF_INET used for (host, port) address format with ipv4 host address
        socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            socket_server.bind((self.host, self.port))
            # Queue incoming requests
            socket_server.listen(5)
            print(f"Listening on {self.host} PORT: {self.port}.....")

            while True:
                # Accepting and receiving client requests
                print("Before accept.")
                (client_conn, client_address) = socket_server.accept()
                print("Client connection opened")
                request: bytes = client_conn.recv(1024)
                print("Request : ")
                print(request.decode())

                # Parsing
                filename = self.get_filename(request)
                method = self.get_request_method(request)
                if method == b'GET':
                    response = self.response_get(filename)
                elif method == b'POST':
                    response = self.response_post(request)
                else:
                    # TODO: Respond with a valid HTTP.
                    response = b"Only GET and POST methods are supported\r\n"

                client_conn.sendall(response)
                print("Response : ")
                print(response)
                client_conn.shutdown(socket.SHUT_RDWR)
                # client_conn.close()
                print("Client connection closed")
        except KeyboardInterrupt:
            print("\n Shutting down server...\n")
        except Exception as exp:
            print(exp)
        socket_server.close()


server = WebServer(6678)
server.init_server()
