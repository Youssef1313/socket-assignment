import socket
import ssl


class SocketFactory:
    def __init__(self):
        self.socket_cache: dict[tuple[str, int], socket.socket] = {}

    def get_or_create_socket(self, host_name, port_number):
        existing_socket = self.socket_cache.get((host_name, port_number))
        if existing_socket is not None:
            return existing_socket
        new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if port_number == 443:
            # https uses port 443, and needs special handling.
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            ssl_socket = ssl_context.wrap_socket(new_socket, server_hostname=host_name)
            ssl_socket.connect((host_name, port_number))
            self.socket_cache[(host_name, port_number)] = ssl_socket
            return ssl_socket
        else:
            new_socket.connect((host_name, port_number))
            self.socket_cache[(host_name, port_number)] = new_socket
            return new_socket

    def create_socket(self, host_name, port_number):
        existing_socket = self.socket_cache.get((host_name, port_number))
        if existing_socket is not None:
            existing_socket.close()
        new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if port_number == 443:
            # https uses port 443, and needs special handling.
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            ssl_socket = ssl_context.wrap_socket(new_socket, server_hostname=host_name)
            ssl_socket.connect((host_name, port_number))
            self.socket_cache[(host_name, port_number)] = ssl_socket
            return ssl_socket
        else:
            new_socket.connect((host_name, port_number))
            self.socket_cache[(host_name, port_number)] = new_socket
            return new_socket
