from datetime import datetime
import socket
import threading


class SocketTracker:
    IDLE_THRESHOLD_IN_SECONDS = 30

    def __init__(self):
        self.__open_sockets: dict[socket.socket, datetime] = {}
        threading.Thread(target=self.track_sockets, args=()).start()

    def use_socket(self, s: socket.socket):
        self.__open_sockets[s] = datetime.now()

    def kill_socket(self, s: socket.socket):
        self.__open_sockets.pop(s)
        s.shutdown(socket.SHUT_RDWR)
        s.close()

    def should_kill_socket(self, s: socket.socket):
        last_use = self.__open_sockets[s]
        idle_seconds = (datetime.now() - last_use).total_seconds()
        if idle_seconds >= self.IDLE_THRESHOLD_IN_SECONDS:
            return True

    def track_sockets(self):
        while True:
            for s in list(self.__open_sockets.keys()):
                if self.should_kill_socket(s):
                    print("Killing socket due to inactivity:")
                    print(s)
                    self.kill_socket(s)
