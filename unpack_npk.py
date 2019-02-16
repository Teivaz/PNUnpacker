import struct, os

FILE = "data.npk"
VERBOSE = 0


TAG_NPK = 0x4e504b30	# "NPK0"
TAG_FILE = 0x46494c45	# "FILE"
TAG_DIR = 0x4449525f	# "DIR_"
TAG_DEND = 0x44454e44	# "DEND"
TAG_DATA = 0x44415441	# "DATA"

def read_uint(f):
	(value, ) = struct.unpack("<I", f.read(4))
	return value

def read_short(f):
	(value, ) = struct.unpack("<h", f.read(2))
	return value

def read_string(f):
	size = read_short(f)
	format = "{}s".format(size)
	(value, ) = struct.unpack(format, f.read(size))
	return value.decode("iso-8859-1")

class File:
	def __init__(self, offset, length, name, path):
		self.offset = offset
		self.length = length
		self.name = name
		self.path = path

	def write(self, data):
		os.makedirs(self.path, exist_ok=True)
		full_name = os.path.join(self.path, self.name)
		end = self.offset + self.length
		with open(full_name, "wb") as f:
			f.write(data[self.offset:end])


class Decoder:
	def __init__(self, source):
		self.directory_stack = []
		self.source = source
		self.data = {}
		self.files = []

	def _open_dir(self, name):
		if VERBOSE > 0:
			pad = "    " * len(self.directory_stack)
			text = pad + "dir: " + str(name) 
			print(text)

		self.directory_stack.append(name)

	def _close_dir(self):
		self.directory_stack.pop()

	def _open_file(self, offset, length, name):
		if VERBOSE > 0:
			pad = "    " * len(self.directory_stack)
			text = pad + "file: " + name 
			print(text)

		path = os.path.join("_"+self.source, *self.directory_stack)
		self.files.append(File(offset, length, name, path))
		
	def _read_DIR(self, data, length):
		name = read_string(data)
		self._open_dir(name)

	def _read_DEND(self, data, length):
		self._close_dir()

	def _read_FILE(self, data, length):
		offset = read_uint(data)
		length = read_uint(data)
		name = read_string(data)
		self._open_file(offset, length, name)

	def _read_DATA(self, data, length):
		self.data = data.read(length)

	def _read_tag(self, tag, data, length):
		if tag == TAG_NPK:
			None
		if tag == TAG_DIR:
			self._read_DIR(data, length)
		if tag == TAG_DEND:
			self._read_DEND(data, length)
		if tag == TAG_FILE:
			self._read_FILE(data, length)
		if tag == TAG_DATA:
			self._read_DATA(data, length)

	def _read_stream_tag(self, tag, data, length):
		position = data.tell()
		self._read_tag(tag, data, length)
		data.seek(position+length, 0)

	def _write_files(self):
		for f in self.files:
			f.write(self.data)

	def run(self):
		with open(self.source, "rb") as f:
			f.seek(0, 2)
			file_end = f.tell()
			f.seek(0, 0)

			while f.tell() != file_end:
				tag = read_uint(f)
				length = read_uint(f)
				self._read_stream_tag(tag, f, length)
				
		self._write_files()

	
if __name__ == "__main__":
	Decoder(FILE).run()
