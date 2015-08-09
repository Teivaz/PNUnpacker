import struct, os
from FbxCommon import *

if 1:
	PATH = "_data.npk"
else:	
	PATH = "nvx"
VERBOSITY = 0


FORMAT_MESH = 3
FORMAT_COLLISION = 1

def readInt(f):
	(r, ) = struct.unpack("<I", f.read(4))
	return r

def readBits(short, num, offset):
	if offset > 0:
		short = short >> offset
	mask = 0xffffffff >> 32-num
	#print short
	result = mask & short
	return int(result)

def parseVertexMesh(f, Vertices):
	tell = f.tell()

	pos = struct.unpack("<fff", f.read(12))
	norm = struct.unpack("<fff", f.read(12))
	uv = struct.unpack("<ff", f.read(8))

	vertex = {"pos": pos, "norm": norm, "uv": uv}
	if VERBOSITY > 2:
		print("{0}: {1}".format(hex(tell), vertex))
	Vertices.append(vertex)


def parseVertexNorm(f, Vertices):
	tell = f.tell()
	pos = struct.unpack("<fff", f.read(12))
	vertex = {"pos": pos}
	if VERBOSITY > 2:
		print("{0}: {1}".format(hex(tell), vertex))
	Vertices.append(vertex)

def validateIndex(i, a):
	if(i[0] == i[1] or i[0] == i[2] or i[1] == i[2]):
		raise NameError("{0}: index validation failed".format(hex(a)))

def parseIndices(f, Indices):
	tell = f.tell()
	index = struct.unpack("<HHH", f.read(6))

	validateIndex(index, tell)

	if VERBOSITY > 1:
		print("{0}: {1}".format(hex(tell), index))
	Indices.append(index)

def parseIndex2(f, Indices):
	tell = f.tell()
	index = (struct.unpack("<HH", f.read(4)), 0)
	if VERBOSITY > 1:
		print("{0}: {1}".format(hex(tell), index))
	Indices.append(index)



def readVertices(f, NumVerts, Vertices, Format):
	if Format == FORMAT_MESH:
		for i in range(NumVerts):
			parseVertexMesh(f, Vertices)
	elif Format == FORMAT_COLLISION:
		for i in range(NumVerts):
			parseVertexNorm(f, Vertices)

	else:
		raise NameError("Unknown format {0}".format(Format))

def convert(f):
	footprint = readInt(f)
	if 0x4e565831 != footprint:
		raise NameError("File is not recognized as .NVX")

	NumVerts = readInt(f)
	NumIndices = readInt(f)
	_a = readInt(f)
	_b = readInt(f)
	Format = readBits(_b, 2, 0)
	_b = readBits(_b, 30, 2)
	dataOffset = readInt(f)
	dataSize = readInt(f)

	print(_a, _b)

	Vertices = []
	Indices = []

	f.seek(dataOffset)

	readVertices(f, NumVerts, Vertices, Format)
	'''
	for i in range(NumIndices-1):
		parseIndices(f, Indices)
	parseIndex2(f, Indices)

	print("{0} of {1}".format(len(Indices), NumIndices))

	currentPos = f.tell()
	print("{0} {1} {2}".format(currentPos, dataOffset, dataSize))
	if currentPos - dataOffset != dataSize:
		raise NameError("File length error")
	'''
	return (Format, Vertices, Indices)


def saveMesh(mesh, fName):
	None

logFile = open("nvx.log", 'w')

def convertFile(name):
	if VERBOSITY > 0:
		print("Converting {0}".format(name))
	f = open(name, "rb")

	try:

		try:
			mesh = convert(f)
		except NameError as e:
			error = "Error in file `{0}`:\n\t{1}".format(name, e)
			#print(error)
			logFile.write(error + "\n")
			f.close()
			return

	except:
		error = "Unknown error in file `{0}`".format(name)
		logFile.write(error + "\n")
		f.close()
		pass
	else:
		f.close()
		saveMesh(mesh, name)


def listDirsAndFiles(path):
	dirs = os.listdir(path)
	dPath = []
	fPath = []
	for d in dirs:
		fullPath = os.path.join(path, d)
		if os.path.isdir(fullPath):
			dPath.append(fullPath)
		elif os.path.splitext(fullPath)[-1] == ".nvx":
			fPath.append(fullPath)
	return dPath, fPath


def convertDir(path):
	dNames, fNames = listDirsAndFiles(path)
	for fName in fNames:
		convertFile(fName)
	for dName in dNames:
		convertDir(dName)

def main():
	convertDir(os.path.abspath(PATH))
	logFile.close()

main()
