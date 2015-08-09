import struct

def isValid(f):
	(footprint, ) = struct.unpack("<I", f.read(4))
	return footprint == 0x4e4f4230 #NOB0

def readLine(f):
	(size, ) = struct.unpack("<h", f.read(2))
	format = "{0}c".format(size)
	string = struct.unpack(format, f.read(size))
	string = "".join(string)
	#string = str(f.read(size))
	return string

def readLineS(f):
	(size_all, size) = struct.unpack("<hh", f.read(4))
	format = "{0}c".format(size)
	string = struct.unpack(format, f.read(size))
	string = "".join(string)
	#string = str(f.read(size))
	return string

def readLineL(f):
	(size_all, wat, size) = struct.unpack("<hIh", f.read(8))
	format = "{0}c".format(size)
	string = struct.unpack(format, f.read(size))
	string = "".join(string)
	#string = str(f.read(size))
	return string

def readLineR(f):
	(size, wat) = struct.unpack("<hI", f.read(6))
	format = "{0}c".format(size)
	string = struct.unpack(format, f.read(size))
	string = "".join(string)
	#string = str(f.read(size))
	return string

def tag_u(f, tag):
	result = []
	result.append(readLine(f))
	print tag + "_u " + " ".join(result)

def tag_us(f, tag):
	result = []
	result.append(readLineS(f))
	print tag + "_u " + " ".join(result)

def tag_SFLN(f):
	result = []
	result.append(readLineS(f))
	print "SFLN " + " ".join(result)

def tag_STGT(f):
	result = []
	result.append(readLineS(f))
	print "STGT " + " ".join(result)

def tag_STXT(f):
	result = []
	result.append(readLineL(f))
	result.append(readLine(f))
	print "STXT " + " ".join(result)

def tag_SRAD(f):
	result = []
	result.append(readLine(f))
	print "SRAD"

def tag_SBNC(f):
	result = []
	result.append(readLine(f))
	print "SBNC"

def tag_SDMG(f):
	result = []
	result.append(readLine(f))
	print "SDMG"

def tag_STOU(f):
	result = []
	result.append(readLine(f))
	print "STOU"

def tag_new(f):
	result = []
	result.append(readLine(f))
	result.append(readLine(f))
	print "new " + " ".join(result)

def tag_sel(f):
	result = []
	result.append(readLine(f))
	print "sel " + " ".join(result)

def parseTag(tag, f):
	if tag == "NOB0":
		return tag_u(f, tag)
	if tag == "_new":
		return tag_new(f)
	if tag == "_sel":
		return tag_sel(f)
	if tag == "SFLN":
		return tag_SFLN(f)
	if tag == "STGT":
		return tag_STGT(f)
	if tag == "STXT":
		return tag_STXT(f)
	if tag == "SRAD":
		return tag_SRAD(f)
	if tag == "SBNC":
		return tag_SBNC(f)
	if tag == "SDMG":
		return tag_SDMG(f)
	if tag == "STOU":
		return tag_STOU(f)


	if tag[0] == "S":
		return tag_us(f, tag)
	return tag_u(f, tag)


def readTag(f):
	tag = struct.unpack("4c", f.read(4))
	tag = "".join(tag)[::-1]
	parseTag(tag, f)

def parse(f):

	if(not isValid(f)):
		print("file invalid")
		return

	f.seek(0, 2)
	fileEnd = f.tell()
	f.seek(0, 0)


	while f.tell() != fileEnd:
		readTag(f)


def main():
	name = "_main.n"
	f = open(name, "rb")
	parse(f)
	f.close()

main()
