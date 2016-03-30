import struct, os

USE_DEVELOPEMENT_FOLDER = True
VERBOSITY = 0

if USE_DEVELOPEMENT_FOLDER:
	PATH = "nvx/character.nax"
else:
	PATH = "_data.npk"

INTERP_STEP = 0
INTERP_LINEAR = 1
INTERP_QUAT = 2

REP_LOOP = 0
REP_ONCE = 1

KEY_VANILLA = 0
KEY_PACKED = 1

def ltof(float16):
	MASK = int(0b1111111111111111)
	result = 0
	C1 = 15
	C2 = 10
	M2 = MASK >> (15-C2)
	s = int((float16 >> C1) & 0b00001)	# sign
	e = int((float16 >> 11) & 0b01111)	# exponent
	m = int(float16 & 0b11111111111)		# mantis
	sign = 1.0
	if s: sign = -1.0
	if e == 0:
		if m == 0:
			result = 0.0
		else:
			result = sign * 2.0**(-13) * (m / 2048.0)
	else:
		result = sign * 2.0**(e-14) * (1.0 + m / 2048.0) 
	#print(bin(s), bin(e), bin(m))
	#print(s,e,m)
	#print float16, float(result)
	print("{:1b} {:04b} {:011b}".format(s, e, m))
	return result

def readByte(f):
	(value, ) = struct.unpack("<b", f.read(1))
	return value
def readShort(f):
	(value, ) = struct.unpack("<h", f.read(2))
	return value
def readUShort(f):
	(value, ) = struct.unpack("<H", f.read(2))
	return value
def readInt(f):
	(value, ) = struct.unpack("<i", f.read(4))
	return value
def readBool(f):
	(value, ) = struct.unpack("<?", f.read(1))
	return value
def readFloat(f):
	(value, ) = struct.unpack("<f", f.read(4))
	return value
def readString(f):
	size = readShort(f)
	format = "{}s".format(size)
	(value, ) = struct.unpack(format, f.read(size))
	return value
def readVoid(f):
	return ""
def readHFloat(f):
	val = readUShort(f)
	return ltof(val)
class Curve:
	Name = None
	StartKey = None
	NumKeys = None
	KeysPerSecond = None
	Interp = None
	Rep = None
	KeyType = None
	Data = None

	stream = None

	def __init__(self, f):
		self.stream = f

	def read(self):
		self.Data = []
		self.readCurveHeader()
		if self.KeyType == KEY_VANILLA:
			self.readCurveDataVanilla()
		elif self.KeyType == KEY_PACKED:
			self.readCurveDataPacked()
		else:
			raise NameError('Unknown key type {}'.format(self.KeyType))

	def readCurveHeader(self):
		footprint = readInt(self.stream)
		if footprint != 0x43484452: #CHDR
			raise NameError("Curve header does not match magic number 0x{:0x} at 0x{:0x}".format(footprint, self.stream.tell()))
		size = readInt(self.stream)
		streamStart = self.stream.tell()
		streamEnd = streamStart + size
		self.StartKey = readInt(self.stream)
		self.NumKeys = readInt(self.stream)
		self.KeysPerSecond = readFloat(self.stream)
		self.Interp = readByte(self.stream)
		self.Rep = readByte(self.stream)
		self.KeyType = readByte(self.stream)
		readByte(self.stream) # padding
		self.Name = readString(self.stream)

	def readCurveDataVanilla(self):
		footprint = readInt(self.stream)
		if footprint != 0x43445456: #CDTV
			raise NameError("Curve data vanilla does not match magic number 0x{:0x} at 0x{:0x}".format(footprint, self.stream.tell()))
		size = readInt(self.stream)
		streamStart = self.stream.tell()
		streamEnd = streamStart + size
		while self.stream.tell() != streamEnd:
			self.Data.append((readFloat(self.stream),readFloat(self.stream),readFloat(self.stream),readFloat(self.stream)))

	def readCurveDataPacked(self):
		footprint = readInt(self.stream)
		if footprint != 0x43445450: #CDTP
			raise NameError("Curve data packed does not match magic number 0x{:0x} at 0x{:0x}".format(footprint, self.stream.tell()))
		size = readInt(self.stream)
		streamStart = self.stream.tell()
		streamEnd = streamStart + size
		while self.stream.tell() != streamEnd:
			self.Data.append((readHFloat(self.stream),readHFloat(self.stream),readHFloat(self.stream),readHFloat(self.stream)))

	def __str__(self):
		result = []
		IntepolationTypes = ["Step", "Linear", "Quaternion"]
		RepeatTypes = ["Loop", "Once"]
		KeyTypes = ["Vanilla", "Packed"]
		interp = IntepolationTypes[self.Interp]
		rep = RepeatTypes[self.Rep]
		key = KeyTypes[self.KeyType]
		result.append('Name: {}, Interpolation: {}, Repeat: {}, Type: {}'.format(self.Name, interp, rep, key))
		for d in self.Data:
			result.append('  ({:5.3}, {:5.3}, {:5.3}, {:5.3})'.format(d[0], d[1], d[2], d[3]))
		return '\n'.join(result)

def readHeader(f):
	(footprint, ) = struct.unpack("<I", f.read(4))
	if footprint != 0x4e415830: #NAX0
		raise NameError("File has invalid format")
	four = readInt(f)
	numCurves = readInt(f)
	return numCurves

def parse(f, path):
	f.seek(0, 2)
	fileEnd = f.tell()
	f.seek(0, 0)

	numCurves = readHeader(f)
	curves = []
	for i in range(numCurves):
		curve = Curve(f)
		curve.read()
		curves.append(curve)
	return curves

def convertFile(name):
	f = open(name, "rb")
	curves = []
	try:
		curves = parse(f, name)
	except NameError as e:
		print("Parsing error {}".format(e))
	f.close()

	if VERBOSITY > 1:
		for c in curves:
			print(str(c))

def listDirsAndFiles(path):
	dirs = os.listdir(path)
	dPath = []
	fPath = []
	for d in dirs:
		fullPath = os.path.join(path, d)
		if os.path.isdir(fullPath):
			dPath.append(fullPath)
		elif os.path.splitext(fullPath)[-1] == ".nax":
			fPath.append(fullPath)
	return dPath, fPath

def convertDir(path):
	if not os.path.isdir(path):
		convertFile(path)
	else:
		dNames, fNames = listDirsAndFiles(path)
		for fName in fNames:
			convertFile(fName)
		for dName in dNames:
			convertDir(dName)

def main():
	convertDir(os.path.abspath(PATH))

main()
