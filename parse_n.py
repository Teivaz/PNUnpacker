import struct

def peek(f, length=1):
    pos = f.tell()
    data = f.read(length) # Might try/except this line, and finally: f.seek(pos)
    f.seek(pos)
    return data

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

######################
def isValid(f):
	(footprint, ) = struct.unpack("<I", f.read(4))
	return footprint == 0x4e4f4230 #NOB0
def readShortI(f):
	(size, ) = struct.unpack("<h", f.read(2))
	return size
def peekShortI(f):
	(size, ) = struct.unpack("<h", peek(f,2))
	return size
def readInt(f):
	(value, ) = struct.unpack("<I", f.read(4))
	return "{}".format(value)

def readFloat(f):
	(value, ) = struct.unpack("<f", f.read(4))
	return "{}".format(value)

def readString(f):
	size = readShortI(f)
	format = "{}c".format(size)
	string = struct.unpack(format, f.read(size))
	string = "".join(string)
	#print string
	return string

######################
def op_new(f):
	a0 = readString(f)
	a1 = readString(f)
	return "{}, {}".format(a0, a1)
def op_sel(f):
	a0 = readString(f)
	return "{}".format(a0)

def fun_v_v(f):
	return ""
def fun_v_f(f):
	a = readFloat(f)
	return "{}".format(a)
def fun_v_i(f):
	a = readInt(f)
	return "{}".format(a)
def fun_v_fff(f):
	a0 = readFloat(f)
	a1 = readFloat(f)
	a2 = readFloat(f)
	return "{}, {}, {}".format(a0, a1, a2)
def fun_b_ff(f):
	f.read(4) # ret bool
	a0 = readFloat(f)
	a1 = readFloat(f)
	return "{}, {}".format(a0, a1)
def fun_v_o(f): #TODO object may be not a string
	a = readString(f)
	return a
def fun_v_s(f):
	a = readString(f)
	return a
def fun_v_ss(f):
	a0 = readString(f)
	a1 = readString(f)
	return "{}, {}".format(a0, a1)
def fun_b_ss(f):
	f.read(4) # ret bool
	a0 = readString(f)
	a1 = readString(f)
	return "{}, {}".format(a0, a1)
def fun_v_i6f(f):
	a0 = readInt(f)
	a1 = readFloat(f)
	a2 = readFloat(f)
	a3 = readFloat(f)
	a4 = readFloat(f)
	a5 = readFloat(f)
	a6 = readFloat(f)
	return "{}, {}, {}, {}, {}, {}".format(a0, a1, a2, a3, a4, a5, a6)


Operators = {
	"_new": (op_new, "new"),
	"_sel": (op_sel, "sel"),
}

Functions = {
	#"NOB0": (tag_u, ""),
	"SRAD": (fun_v_f, "setradius"),
	"SCHN": (fun_v_s, "setchannel"),
	"STGT": (fun_v_o, "settarget"), #object
	"SXYZ": (fun_v_fff, "sxyz"),
	"TXYZ": (fun_v_fff, "txyz"),
	"STXT": (fun_b_ss, "settexture"), #TODO return bool
	"SFAF": (fun_v_f, "setfinishedafter"),
	"SRPT": (fun_v_s, "setreptype"),
	"SKEY": (fun_v_i6f, "setkey"),
	"BKEY": (fun_v_i, "beginkeys"),
	"EKEY": (fun_v_v, "endkeys"),
	"SSCL": (fun_v_f, "setscale"),

	#nparticlesystem
	"SLFT": (fun_v_f, "setlifetime"),
	"SFRQ": (fun_v_f, "setfreq"),
	"SSPD": (fun_v_f, "setspeed"),
	"SACC": (fun_v_fff, "setaccel"),
	"SICN": (fun_v_f, "setinnercone"),
	"SOCN": (fun_v_f, "setinnercone"),
	"SSPN": (fun_v_f, "setspin"),
	"SSPA": (fun_v_f, "setspinaccel"),
	#"SSTR" :
	"SEMT": (fun_v_s, "setemmiter"),


	"SMSN": (fun_v_s, "_SMSN"),




	"SFLN": (fun_v_s, "_SFLN"),
	"STMS": (fun_v_fff, "_STMS"),
}

'''
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
'''


def parseTag(tag, f):
	name = tag
	result = ""

	pos = f.tell()
	if tag in Operators:
		(fun, name) = Operators[tag]
		result = fun(f)
	elif tag in Functions:
		(fun, name) = Functions[tag]
		tagSize = readShortI(f)
		result = fun(f)
		f.seek(pos + tagSize + 2)
	else:
		result = readBytes(f)

	print("{} {}".format(name, result))
	#print("0x{:0x}: {} {}".format(pos, name, result))
	return

	if tag[0] == "S": tag_u,(f, tag)
	return tag_u(f, tag)


def readTag(f):
	tag = struct.unpack("4c", f.read(4))
	tag = "".join(tag)[::-1]
	pos = f.tell()
	parseTag(tag, f)
	try:
		None
	except:
		print("exception at {} - {}".format(tag, hex(pos)))

def parse(f):

	f.seek(0, 2)
	fileEnd = f.tell()
	f.seek(0, 0)

	(footprint, ) = struct.unpack("<I", f.read(4))
	if footprint != 0x4e4f4230: #NOB0
		print("file invalid")
		return

	print readString(f)

	while f.tell() != fileEnd:
		readTag(f)


def main():
	name = "a_ammo.n/_main.n"
	f = open(name, "rb")
	parse(f)
	f.close()

main()
