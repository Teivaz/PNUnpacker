import struct, os

from .tag_reader import TagReader

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
			reader = TagReader(f)
			length = len(reader.stream)
			while reader.stream.tell() != length:
				reader.read(readers)

def unpack(source, verbosity=0):
	Unpacker(source, verbosity)
