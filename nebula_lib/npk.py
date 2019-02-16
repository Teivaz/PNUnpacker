import struct, os, io

from .tag_stream import InputTagStream, OutputTagStream
from .stream import OutputStream

class File:
	def __init__(self, offset, length, name, path):
		self.offset = offset
		self.length = length
		self.name = name
		self.path = path

	def write_from_data(self, data):
		os.makedirs(self.path, exist_ok=True)
		full_name = os.path.join(self.path, self.name)
		end = self.offset + self.length
		with open(full_name, "wb") as f:
			f.write(data[self.offset:end])

	def write_from_stream(self, stream, base_offset):
		os.makedirs(self.path, exist_ok=True)
		full_name = os.path.join(self.path, self.name)
		stream.seek(base_offset + self.offset, 0)
		with open(full_name, "wb") as f:
			f.write(stream.read(self.length))

class Unpacker:
	def __init__(self, source, verbosity=0):
		self.directory_stack = []
		self.source = source
		self.files = []
		self.verbosity = verbosity
		self.metadata_length = 0

		self._run()

	def _open_dir(self, name):
		if self.verbosity > 0:
			pad = "    " * len(self.directory_stack)
			text = pad + "dir: " + str(name)
			print(text)

		self.directory_stack.append(name)

	def _close_dir(self):
		self.directory_stack.pop()

	def _open_file(self, offset, length, name):
		if self.verbosity > 0:
			pad = "    " * len(self.directory_stack)
			text = pad + "file: " + name
			print(text)

		path = os.path.join("_"+self.source, *self.directory_stack)
		self.files.append(File(offset, length, name, path))

	def _read_DIR(self, stream, length, reader):
		name = stream.read_string()
		self._open_dir(name)

	def _read_DEND(self, stream, length, reader):
		self._close_dir()

	def _read_FILE(self, stream, length, reader):
		offset = stream.read_uint()
		length = stream.read_uint()
		name = stream.read_string()
		self._open_file(offset, length, name)

	def _read_DATA(self, stream, length, reader):
		base_offset = stream.tell()
		for f in self.files:
			f.write_from_stream(reader.stream, base_offset)

	def _read_NPK0(self, stream, length, reader):
		self.metadata_length = stream.read_uint()

	def _run(self):
		readers = {
			"NPK0": self._read_NPK0,
			"FILE": self._read_FILE,
			"DIR_": self._read_DIR,
			"DEND": self._read_DEND,
			"DATA": self._read_DATA,
		}
		with open(self.source, "rb") as f:
			reader = InputTagStream(f)
			length = len(reader.stream)
			while reader.stream.tell() != length:
				reader.read(readers)

def unpack(source, verbosity=0):
	Unpacker(source, verbosity)

class Packer:
	def __init__(self, source, target):
		self.source = source
		self.target = target
		self.data_buffer = OutputStream(io.BytesIO())
		self.tag_buffer = OutputStream(io.BytesIO())

		self._run()

	def _write_NPK0(self, stream, writer):
		stream.write_uint(len(self.tag_buffer) + 12)

	def _write_FILE(self, path, name):
		offset = self.data_buffer.tell()
		with open(path, "rb") as f:
			self.data_buffer.write(f.read())
			length = f.tell()
		def writer(stream, writer):
			stream.write_uint(offset)
			stream.write_uint(length)
			stream.write_string(name)
		return writer
		
	def _write_directory_content(self, path, writer):
		dir_content = os.listdir(path)
		files = [f for f in dir_content if os.path.isfile(os.path.join(path, f))]
		dirs = [f for f in dir_content if os.path.isdir(os.path.join(path, f))]
		for f in files:
			file_path = os.path.join(path, f)
			writer.write("FILE", self._write_FILE(file_path, f))

		for d in dirs:
			dir_path = os.path.join(path, d)
			writer.write("DIR_", self._write_DIR(d))
			self._write_directory_content(dir_path, writer)
			writer.write("DEND", self._write_DEND)

	def _write_DIR(self, name):
		def writer(stream, writer):
			stream.write_string(name)
		return writer

	def _write_DEND(self, stream, writer):
		pass

	def _write_DATA(self, stream, writer):
		stream.write(self.data_buffer.readall())
		
	def _run(self):
		writer = OutputTagStream(self.tag_buffer)
		self._write_directory_content(self.source, writer)
		with open(self.target, "wb") as f:
			writer = OutputTagStream(f)
			writer.write("NPK0", self._write_NPK0)
			writer.stream.write(self.tag_buffer.readall())
			writer.write("DATA", self._write_DATA)


def pack(source, target):
	Packer(source, target)
