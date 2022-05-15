from src.common.SocketWrapper import SocketWrapper


def first_receive(s: SocketWrapper):
    headers: bytes = b""
    headers_length = -1
    while headers_length == -1:
        current = s.recv()
        if len(current) == 0:
            break
        headers += current
        headers_length = headers.find(b'\r\n\r\n')

    if headers_length == -1:
        if len(headers) == 0:
            return None
        else:
            raise ValueError(f"Got into unexpected state. Received part of headers?\r\n{headers}")

    body = headers[headers_length + len(b"\r\n\r\n"):]
    s.add_back(body)
    headers = headers[:headers_length + len(b"\r\n\r\n")]
    return headers
