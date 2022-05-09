from socket import socket


def first_receive(s: socket):
    headers: bytes = b""
    headers_length = -1
    while headers_length == -1:
        current = s.recv(1024)
        headers += current
        headers_length = headers.find(b'\r\n\r\n')

    body = headers[headers_length + len(b"\r\n\r\n"):]
    headers = headers[:headers_length + len(b"\r\n\r\n")]
    return (headers, body)
