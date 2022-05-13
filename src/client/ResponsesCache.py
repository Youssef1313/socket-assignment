class ResponsesCache:
    def __init__(self):
        # Key: (filename, hostname, port)
        # Value: The response
        self.cache: dict[tuple[str, str, int], bytes] = {}

    def try_get(self, filename: str, hostname: str, port: int):
        return self.cache.get((filename, hostname, port))

    def add_to_cache(self, filename: str, hostname: str, port: int, response: bytes):
        self.cache[(filename, hostname, port)] = response
