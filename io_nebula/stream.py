import struct
from .errors import StreamError

class InputStream:
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
    
    def read_byte(self):
        (v, ) = struct.unpack("<B", self.stream.read(1))
        return v

    def read_tag_name(self):
        (value, ) = struct.unpack("4s", self.stream.read(4))
        return value[::-1].decode("ascii")

    def read_uint(self):
        (value, ) = struct.unpack("<I", self.stream.read(4))
        return value

    def read_float(self):
        (v, ) = struct.unpack("<f", self.stream.read(4))
        return v

    def read_short(self):
        (value, ) = struct.unpack("<h", self.stream.read(2))
        return value
    def read_ushort(self):
        (v, ) = struct.unpack("<H", self.stream.read(2))
        return v

    def read_string(self):
        size = self.read_short()
        (value, ) = struct.unpack("{}s".format(size), self.stream.read(size))
        return value.decode("iso-8859-1")


class OutputStream:
    def __init__(self, stream):
        self.stream = stream

    def tell(self):
        return self.stream.tell()
    
    def seek(self, *args, **kwargs):
        return self.stream.seek(*args, **kwargs)

    def read(self, length):
        return self.stream.read(length)

    def readall(self):
        current = self.stream.tell()
        self.stream.seek(0, 0)
        result = self.stream.read()
        self.stream.seek(current, 0)
        return result

    def __len__(self):
        current = self.stream.tell()
        self.stream.seek(0, 2)
        stream_end = self.stream.tell()
        self.stream.seek(current, 0)
        return stream_end

    def write_stream(self, src, buffer_size=16*1024*1024):
        while True:
            buf = src.read(buffer_size)
            if not buf:
                break
            self.stream.write(buf)
            
    def write(self, data):
        self.stream.write(data)

    def write_byte(self, value):
        self.stream.write(struct.pack("<B", value))

    def write_uint(self, value):
        self.stream.write(struct.pack("<I", value))

    def write_float(self, value):
        self.stream.write(struct.pack("<f", value))

    def write_short(self, value):
        self.stream.write(struct.pack("<h", value))
    def write_ushort(self, value):
        self.stream.write(struct.pack("<H", value))

    def wtite_tag_name(self, tag):
        if len(tag) != 4:
            raise StreamError("Tag must contain 4 ASCII characters")
        self.stream.write(tag.encode("ascii")[::-1])
    
    def write_string(self, value):
        value = value.encode("ascii")
        length = len(value)
        self.write_short(length)
        self.stream.write(value)
