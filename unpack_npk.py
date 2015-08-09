import struct, json, os

FILE = "data.npk"

VERBOSE = 1

def isChar(b):
	return (32 <= b) and (126 >= b)

def toString(bytes, size):
	format = str(size) + "c"
	bytes = struct.unpack(format, bytes)
	string = ""
	byteString = ""
	for b in bytes:
		bByte = ord(b)
		if isChar(bByte):
			string += " " + b + "|"
		else:
			string += "  |"
		byteString += "{:02x}|".format(bByte)


	return string, byteString

TAG_NPK = 0x4e504b30
TAG_FILE = 0x46494c45
TAG_DIR = 0x4449525f
TAG_DEND = 0x44454e44
TAG_DATA = 0x44415441

TAG_NAMES = {
	TAG_NPK: "NPK0",
	TAG_FILE: "FILE",
	TAG_DIR: "DIR_",
	TAG_DEND: "DEND",
	TAG_DATA: "DATA"
}

CD = []
DATA = {}
FILES = []

def openDir(name):
	if VERBOSE > 0:
		pad = "    " * len(CD)
		text = pad + "dir: " + str(name) 
		print(text)

	CD.append(name)

def closeDir():
	CD.pop()

def openFile(name):
	if VERBOSE > 0:
		pad = "    " * len(CD)
		text = pad + "file: " + name 
		print(text)

	path = list()
	path.extend(CD)
	path.append(name)
	fileName = "/".join(path)
	currentFile = {}
	currentFile["fullName"] = fileName
	currentFile["name"] = name
	FILES.append(currentFile)
	return currentFile


def readDIR(data, length):
	format = "<h{0}c".format(length-2)
	result = struct.unpack(format, data)
	nameLen = result[0]
	name = str(b"".join(result[1:]))
	openDir(name)

def readDEND(data, length):
	closeDir()

def readFILE(data, length):
	format = "<IIh{0}c".format(length-10)
	result = struct.unpack(format, data)
	start = result[0]
	length = result[1]
	nameLen = result[2]
	name = "".join(result[3:])
	CF = openFile(name)
	CF["start"] = start
	CF["length"] = length
	CF["nameLen"] = nameLen

def readDATA(data, length):
	#format = "{0}c".format(length)
	DATA["d"] = data# = struct.unpack(format, data)
	#string, bytes = toString(data, length)
	#print("{0}\n{1}\n".format(string, bytes))

def readTag(tag, data, length):
	if tag == TAG_NPK:
		None
	if tag == TAG_DIR:
		readDIR(data, length)
	if tag == TAG_DEND:
		readDEND(data, length)
	if tag == TAG_FILE:
		readFILE(data, length)
	if tag == TAG_DATA:
		readDATA(data, length)

def readStreamTag(tag, stream, size):
	data = stream.read(size)
	readTag(tag, data, size)

def createDir(parent):
	if not os.path.exists(parent):
		os.mkdir(parent)

def createFile(f):
	fullName = f["fullName"]
	dirs = fullName.split("/")
	name = dirs.pop()
	parent = "_" + FILE
	createDir(parent)
	for d in dirs:
		parent = "{0}/{1}".format(parent, d)
		createDir(parent)
	return open(parent + "/" + name, "wb")

def writeFiles(files):
	for f in files:
		#print(f)
		handle = createFile(f)
		start = f["start"]
		end = start + f["length"]
		handle.write("".join(DATA["d"][start:end]))
		handle.close()

f = open(FILE, "rb")
f.seek(0, 2)
fileEnd = f.tell()
f.seek(0, 0)

while f.tell() != fileEnd:
	addr = f.tell()
	(tag, size) = struct.unpack("<II", f.read(8))
	#print("{0}: {1} {2}".format(hex(addr), size, TAG_NAMES[tag]))
	#readPayload(f, size)
	readStreamTag(tag, f, size)
#print(DATA)

writeFiles(FILES)

#print(json.dumps(FILES, indent=2))

print("ok")

f.close()
