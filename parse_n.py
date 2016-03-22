import struct

def isValid(f):
	(footprint, ) = struct.unpack("<I", f.read(4))
	return footprint == 0x4e4f4230 #NOB0

def readLine(f):
	(size, ) = struct.unpack("<h", f.read(2))
	format = "{}c".format(size)
	string = struct.unpack(format, f.read(size))
	string = "".join(string)
	#return "{}|{} ".format(size, string)
	return string

def readNBytes(f, size):
	format = "{}b".format(size)
	data = struct.unpack(format, f.read(size))
	return "{}".format(data)

def readBytes(f):
	(size, ) = struct.unpack("<h", f.read(2))
	format = "{}b".format(size)
	data = struct.unpack(format, f.read(size))
	return "{}".format(data)

def readLineS(f):
	string = ""
	(size, ) = struct.unpack("<h", f.read(2))
	if size > 1:
		(sizeS, ) = struct.unpack("<h", f.read(2))
		format = "{0}c".format(sizeS)
		string = struct.unpack(format, f.read(sizeS))
		string = "".join(string)
		size -= sizeS+2
	if size > 0:
		format = "{}b".format(size)
		data = readNBytes(f, size)
		string = "{}#{}".format(string, data)
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


def tag_u(f):
	result = []
	result.append(readLine(f))
	return " ".join(result)

def tag_us(f):
	result = []
	result.append(readLineS(f))
	return " ".join(result)

def tag_SFLN(f):
	result = []
	result.append(readLineS(f))
	return " ".join(result)

def tag_STGT(f):
	result = []
	result.append(readLineS(f))
	return " ".join(result)

def tag_STXT(f):
	result = []
	result.append(readLineL(f))
	result.append(readLine(f))
	return " ".join(result)

def tag_SRAD(f):
	result = []
	result.append(readLine(f))
	return " ".join(result)

def tag_SBNC(f):
	result = []
	result.append(readLine(f))
	return " ".join(result)

def tag_SDMG(f):
	result = []
	result.append(readLine(f))
	return " ".join(result)

def tag_STOU(f):
	result = []
	result.append(readLine(f))
	return " ".join(result)

def tag_new(f):
	result = []
	result.append(readLine(f))
	result.append(readLine(f))
	return " ".join(result)

def tag_sel(f):
	result = []
	result.append(readLine(f))
	return " ".join(result)

###################
def fun_v_f(f):
	f.read(2)
	r = struct.unpack("<f", f.read(4))
	return "{}".format(r[0])
def fun_v_fff(f):
	f.read(2)
	v = struct.unpack("<fff", f.read(12))
	return "{}, {}, {}".format(v[0], v[1], v[2])
def fun_v_o(f): #TODO object may be not a string
	f.read(2)
	s = readLine(f)
	return s
def fun_v_s(f):
	f.read(2)
	s = readLine(f)
	return s
def fun_v_ss(f):
	f.read(2)
	s1 = readLine(f)
	s2 = readLine(f)
	return "{}, {}".format(s1, s2)
def fun_b_ss(f):
	f.read(2)
	f.read(4)
	s1 = readLine(f)
	s2 = readLine(f)
	return "{}, {}".format(s1, s2)

Tags = {
	"NOB0": (tag_u, ""),
	"_new": (tag_new, "new"),
	"_sel": (tag_sel, "sel"),
	"SRAD": (fun_v_f, "setradius"),
	"SCHN": (fun_v_s, "setchannel"),
	"STGT": (fun_v_o, "settarget"), #object
	"SXYZ": (fun_v_fff, "sxyz"),
	"TXYZ": (fun_v_fff, "txyz"),
	"STXT": (fun_b_ss, "settexture"), #TODO return bool
	"SFAF": (fun_v_f, "setfinishedafter"),
	"SRPT": (fun_v_s, "setreptype"),

	"SFLN": (tag_SFLN, "_SFLN"),
	"SBNC": (tag_SBNC, "_SBNC"),
	"SDMG": (tag_SDMG, "_SDMG"),
	"STOU": (tag_STOU, "_STOU"),
	"SMSN": (readLineS, "_SMSN"),
	"SOCN": (readLineS, "_SOCN"),
	"SACC": (readLineS, "_SACC"),
	"SICN": (readLineS, "_SICN"),
	"SLFT": (readLineS, "_SLFT"),
	"SRAC": (readLineS, "_SRAC"),
	"SSTB": (readLineS, "_SSTB"),
	"SUTR": (readLineS, "_SUTR"),
	"SAFM": (readLineS, "_SAFM"),
	"SAFU": (readLineS, "_SAFU"),
	"SAUD": (readBytes, "_SAUD"),
	"SRDO": (readBytes, "_SRDO"),
}

def parseTag(tag, f):
	name = tag
	result = ""
	pos = f.tell()
	if tag in Tags:
		(fun, name) = Tags[tag]
		result = fun(f)
	else:
		result = readBytes(f)

	print("{} {}".format(name, result))
	#print("0x{:0x}: {} {}".format(pos, tag, result))
	return

	if tag[0] == "S": tag_u,(f, tag)
	return tag_u(f, tag)


def readTag(f):
	tag = struct.unpack("4c", f.read(4))
	tag = "".join(tag)[::-1]
	pos = f.tell()
	try:
		parseTag(tag, f)
	except:
		print("exception at {} - {}".format(tag, hex(pos)))

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
	name = "a_ammo.n/_main.n"
	f = open(name, "rb")
	parse(f)
	f.close()

main()
