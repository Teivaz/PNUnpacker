import struct

def peek(f, length=1):
	pos = f.tell()
	data = f.read(length) # Might try/except this line, and finally: f.seek(pos)
	f.seek(pos)
	return data

def isValid(f):
	(footprint, ) = struct.unpack("<I", f.read(4))
	return footprint == 0x4e4f4230 #NOB0
def readShortI(f):
	(size, ) = struct.unpack("<H", f.read(2))
	return size
def peekShortI(f):
	(size, ) = struct.unpack("<h", peek(f,2))
	return size
def readInt(f):
	(value, ) = struct.unpack("<i", f.read(4))
	return "{}".format(value)
def readBool(f):
	(value, ) = struct.unpack("<?", f.read(1))
	return "{}".format(value)

def readFloat(f):
	(value, ) = struct.unpack("<f", f.read(4))
	return "{}".format(value)

def readString(f):
	size = readShortI(f)
	format = "{}s".format(size)
	(string,) = struct.unpack(format, f.read(size))
	string.decode(encoding="latin-1", errors="replace")
	return string

def readVoid(f):
	return ""

def readNBytes(f, size):
	format = "{}b".format(size)
	data = struct.unpack(format, f.read(size))
	return "{}".format(data)

def readBytes(f):
	(size, ) = struct.unpack("<h", f.read(2))
	#strSize = peekShortI(f)
	#if strSize+2 == size:
	#	return readString(f)
	format = "{}b".format(size)
	data = struct.unpack(format, f.read(size))
	return "{}".format(data)

def readTag(f, parseTag):
	try:
		(tag,) = struct.unpack("4s", f.read(4))
		tag = str(tag[::-1].decode("utf-8"))
		pos = f.tell()
		parseTag(tag, f)
	except NameError as e:
		raise NameError(str(e) + " Pos {}".format(hex(pos)))