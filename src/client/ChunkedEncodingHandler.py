class ChunkedEncodingHandler:
    def __init__(self):
        self.is_complete = False
        self.chunks: list[str] = []
        self.data_accumulator = ""
        self.current_chunk_size = 0
        self.position = 0
        self.expecting_new_chunk = True
        self.CRLF = "\r\n"
        self.CRLF_LENGTH = len(self.CRLF.encode())

    def __set_chunk_size_and_advance_position(self):
        if self.position == len(self.data_accumulator):
            # There is nothing to read.
            return

        chunk_size_hex = ""
        for i in range(self.position, len(self.data_accumulator)):
            c = self.data_accumulator[i]
            if c.lower() in "0123456789abcdef":
                chunk_size_hex += c
            else:
                break

        if chunk_size_hex == "":
            raise ValueError("Expected hex number in beginning of a new chunk.")

        position_after_hex = self.position + len(chunk_size_hex)
        data_after_hex = self.data_accumulator[position_after_hex:position_after_hex + len('\r\n')]
        if data_after_hex != '\r\n' and len(data_after_hex) == len('\r\n'):
            # There is data after the hex, but it's not \r\n
            raise ValueError("Expected CRLF after hex chunk size.")
        elif data_after_hex != '\r\n':
            # Data containing new line isn't yet read. Skip for now.
            return

        self.position = position_after_hex + len('\r\n')
        self.current_chunk_size = int(chunk_size_hex, 16)
        self.expecting_new_chunk = False
        if self.current_chunk_size == 0:
            self.is_complete = True

    def add_data(self, data: str) -> None:
        self.data_accumulator += data
        if self.expecting_new_chunk:
            self.__set_chunk_size_and_advance_position()
        self.__add_to_chunks()

    def __add_to_chunks(self):
        while True:
            chunk = self.data_accumulator[self.position:self.position + self.current_chunk_size]
            if len(chunk) == self.current_chunk_size:
                self.chunks.append(chunk)
                position_after_chunk = self.position + self.current_chunk_size
                data_after_chunk = self.data_accumulator[position_after_chunk:position_after_chunk + len('\r\n')]
                if data_after_chunk != '\r\n' and len(data_after_chunk) == len('\r\n'):
                    raise ValueError("Expecting CRLF after chunk.")
                elif data_after_chunk != '\r\n':
                    return

                self.position = position_after_chunk + len('\r\n')
                self.expecting_new_chunk = True
                self.__set_chunk_size_and_advance_position()
            else:
                break
