import struct

class Stream:
    def __init__(self, stream):
        self.stream = stream
    
    def tell(self):
        return self.stream.tell()
    
    def seek(self, *args, **kwargs):
        return self.stream.seek(*args, **kwargs)

    def skip(self, length):
        self.stream.seek(length, 1)

    def __len__(self):
        current = self.stream.tell()
        self.stream.seek(0, 2)
        stream_end = self.stream.tell()
        self.stream.seek(current, 0)
        return stream_end

    def read(self, length):
        return self.stream.read(length)

    def read_tag_name(self):
        (value, ) = struct.unpack("4s", self.stream.read(4))
        return value[::-1].decode("ascii")

    def read_uint(self):
        (value, ) = struct.unpack("<I", self.stream.read(4))
        return value

    def read_short(self):
        (value, ) = struct.unpack("<h", self.stream.read(2))
        return value

    def read_string(self):
        size = self.read_short()
        (value, ) = struct.unpack("{}s".format(size), self.stream.read(size))
        return value.decode("iso-8859-1")
