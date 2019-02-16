from .errors import StreamError
from .stream import InputStream, OutputStream
import io

class InputTagStream():
    def __init__(self, stream):
        self.stream = InputStream(stream)

    # tag_reader = {
    #   "NPK0": lambda (stream, length, reader): stream.skip(length)
    # }
    def read(self, tag_readers):
        tag = self.stream.read_tag_name()
        length = self.stream.read_uint()
        start = self.stream.tell()
        end = start + length
        try:
            reader = tag_readers[tag]
        except KeyError:
            raise StreamError("No reader for the tag '{}'".format(tag)) from None
        result = reader(self.stream, length, self)

        if self.stream.tell() > end:
            raise StreamError("Reader '{}' exceeded bounds".format(tag))

        if self.stream.tell() < end:
            self.stream.seek(end, 0)

        return result

class OutputTagStream:
    def __init__(self, stream):
        self.stream = OutputStream(stream)

    # tag_writer = lambda (stream, writer): stream.write_uint(10)
    def write(self, tag, tag_writer):
        tag_stream = OutputStream(io.BytesIO())
        tag_writer(tag_stream, self)
        length = tag_stream.tell()
        self.stream.wtite_tag_name(tag)
        self.stream.write_uint(length)
        self.stream.write(tag_stream.readall())
