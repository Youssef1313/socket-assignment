class ChunkedEncodingHandler:
    def __init__(self):
        self.is_complete = False
        self.chunks: list[str] = []
        self.data_accumulator = b""
        self.current_chunk_size = 0
        self.position = 0
        self.expecting_new_chunk = True
        self.CRLF = b"\r\n"
        self.CRLF_LENGTH = len(self.CRLF)

    def __set_chunk_size_and_advance_position(self):
        if self.position == len(self.data_accumulator):
            # There is nothing to read.
            return

        chunk_size_hex = ""
        for i in range(self.position, len(self.data_accumulator)):
            c = chr(self.data_accumulator[i])
            if c.lower() in "0123456789abcdef":
                chunk_size_hex += c
            else:
                break

        if chunk_size_hex == "":
            raise ValueError("Expected hex number in beginning of a new chunk.")

        position_after_hex = self.position + len(chunk_size_hex)
        data_after_hex = self.data_accumulator[position_after_hex:position_after_hex + self.CRLF_LENGTH]
        if data_after_hex != self.CRLF and len(data_after_hex) == self.CRLF_LENGTH:
            # There is data after the hex, but it's not \r\n
            raise ValueError("Expected CRLF after hex chunk size.")
        elif data_after_hex != self.CRLF:
            # Data containing new line isn't yet read. Skip for now.
            return

        self.position = position_after_hex + self.CRLF_LENGTH
        self.current_chunk_size = int(chunk_size_hex, 16)
        self.expecting_new_chunk = False
        if self.current_chunk_size == 0:
            self.is_complete = True

    def add_data(self, data: bytes) -> None:
        self.data_accumulator += data
        if self.expecting_new_chunk:
            self.__set_chunk_size_and_advance_position()
        self.__add_to_chunks()

    def __add_to_chunks(self):
        while True:
            chunk = self.data_accumulator[self.position:self.position + self.current_chunk_size]
            if len(chunk) == self.current_chunk_size:
                position_after_chunk = self.position + self.current_chunk_size
                data_after_chunk = self.data_accumulator[position_after_chunk:position_after_chunk + self.CRLF_LENGTH]
                if data_after_chunk != self.CRLF and len(data_after_chunk) == self.CRLF_LENGTH:
                    raise ValueError("Expecting CRLF after chunk.")
                elif data_after_chunk != self.CRLF:
                    return

                self.chunks.append(chunk.decode())
                self.position = position_after_chunk + self.CRLF_LENGTH
                self.expecting_new_chunk = True
                self.__set_chunk_size_and_advance_position()
            else:
                break
