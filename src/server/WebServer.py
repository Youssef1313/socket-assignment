import io
import socket
from socket import *
import pathlib
from PIL import Image
import base64
import re
from datetime import datetime

HOST = 'localhost'
PORT = 8888


def check_img(filename):
    extension = pathlib.Path(filename).suffix[1:]
    if extension in ['jpg', 'jpeg', 'png', 'gif']:
        return [True, extension]
    return [False, extension]

def create_file(data_type,payload):
    filename = f"{datetime.timestamp(datetime.now())}.{data_type}"
    output_file = open(filename, "w")
    output_file.write(payload)
    output_file.close()
    return filename

class WebServer:

    @staticmethod
    def get_request_method(request):
        headers = request.split('\n')
        method = headers[0].split()[0]
        return method

    @staticmethod
    def get_filename(request):
        headers = request.split('\n')
        filename = headers[0].split()[1][1:]
        print("headers")
        print(headers)
        return filename

    @staticmethod
    def response_GET(filename):
        if filename == '/' or filename == '':
            filename = 'index.html'

        try:
            img_checker = check_img(filename)

            if img_checker[0]:
                file = Image.open(filename, mode='r')
                file_bytes = io.BytesIO()
                file.save(file_bytes, format=img_checker[1])
                img_bytes = file_bytes.getvalue()
                img_data = (base64.b64encode(img_bytes))
                content = f"<html><img src='data:image/{img_checker[1]};base64,{str(img_data)[2:]}/></html>"
                # file.show()    To show externally outside the browser
            else:
                file = open(filename)
                content = file.read()
            file.close()
            response = 'HTTP/1.0 200 OK\n\n' + content + '\r\n'
        except IOError:
            filename = 'error.html'
            file = open(filename)
            content = file.read()
            file.close()
            response = 'HTTP/1.0 404 NOT FOUND\n\n' + content + '\r\n'
        return response

    @staticmethod
    def response_POST(request):
        content_length_regx = re.compile("Content-Length: (.*?)\r")
        content_length = int(content_length_regx.findall(request)[0])
        payload = request[-content_length:]

        content_type_regx = re.compile("Content-Type: (.*?)\r")
        content_type = str(content_type_regx.findall(request)[0])

        if content_type == 'application/json':
            file_path = create_file('json', payload=payload)
        elif content_type == 'text/plain':
            file_path = create_file('txt', payload=payload)
        elif content_type == 'text/html':
            file_path = create_file('html', payload=payload)
        elif content_type.startswith('multipart/form-data'):
            return request

        response = 'HTTP/1.0 201 CREATED\n\n'+f'<html><body><h3>HTTP/1.0 201 CREATED</h3>' \
                                              f'<h3>Data successfully added</h3>' \
                                              f'<h4>check file named {file_path} in the server directory</h4>' \
                                              f'<p>data: {payload} ' \
                                              f'<br>Type: {content_type} <br>' \
                                              f'Length: {content_length}' \
                                              f'</p></body></html>'
        return response

    def init_server(self):
        # Create Socket
        # AF_INET used for (host, port) address format with ipv4 host address
        socket_server = socket(AF_INET, SOCK_STREAM)
        socket_server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        try:
            socket_server.bind((HOST, PORT))
            # Queue incoming requests
            socket_server.listen(5)
            print(f"Listening on {HOST} PORT:{PORT}.....")

            while True:
                # Accepting and receiving client requests
                (client_conn, client_address) = socket_server.accept()
                print("Client connection opened")
                request = client_conn.recv(1024).decode()
                print("Request : ")
                print(request)

                # Parsing
                filename = self.get_filename(request)
                method = self.get_request_method(request)
                if method == 'GET':
                    response = self.response_GET(filename)
                elif method == 'POST':
                    response = self.response_POST(request)
                else:
                    response = "Only GET and POST methods are supported\r\n"

                client_conn.sendall(response.encode())
                print("Response : ")
                print(response)
                client_conn.shutdown(SHUT_WR)
                # client_conn.close()
                print("Client connection closed")
        except KeyboardInterrupt:
            print("\n Shutting down server...\n")
        except Exception as exp:
            print(exp)
        socket_server.close()


myServer = WebServer()
myServer.init_server()
