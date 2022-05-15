from socket import socket


class SocketWrapper:
    def __init__(self, s: socket):
        self.accumulator: bytes = b''
        self.s = s

    def recv(self):
        if len(self.accumulator) > 0:
            temp = self.accumulator
            self.accumulator = b''
            return temp
        return self.s.recv(1024)

    def add_back(self, b: bytes):
        self.accumulator += b
