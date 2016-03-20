import struct, os
#from FbxCommon import *

if 0:
	PATH = "_data.npk"
else:	
	PATH = "viewer"
VERBOSITY = 1

ANALYZE_ONLY = 0


FORMAT_UNKNOWN_1 = 1     # 0b00000001 - 1
FORMAT_UNKNOWN_5 = 5     # 0b00000101 - 5
FORMAT_UNKNOWN_121 = 121 # 0b01111001 - 121
FORMAT_UNKNOWN_3 = 3     # 0b00000011 - 3
FORMAT_UNKNOWN_11 = 11   # 0b00001011 - 11
FORMAT_UNKNOWN_27 = 27   # 0b00011011 - 27
FORMAT_UNKNOWN_139 = 139 # 0b10001011 - 139

FORMAT_UNKNOWN_59 = 59   # 0b00111011 - 59
FORMAT_UNKNOWN_19 = 19   # 0b00010011 - 19
FORMAT_UNKNOWN_123 = 123 # 0b01111011 - 123

FORMAT_COLLISION = 1
#FORMAT_MESH = 3
FORMAT_MODEL = 11

def readInt(f):
	(r, ) = struct.unpack("<I", f.read(4))
	return r

def readShort(f):
	(r, ) = struct.unpack("<H", f.read(2))
	return r

def readFloat(f):
	(r, ) = struct.unpack("<f", f.read(4))
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


def parseModelVertices(f, NumVerts):
	Verts = []
	Normals = []
	UV = []
	for i in range(NumVerts):
		pos = struct.unpack("<fff", f.read(12))
		norm = struct.unpack("<fff", f.read(12))
		uv = struct.unpack("<ff", f.read(8))

		'''
		if uv[0] > 1 or uv[0] < 0:
			raise NameError("U is out of bounds at index {1}: {0}".format(uv[0], i))
		if uv[1] > 1 or uv[1] < 0:
			raise NameError("V is out of bounds at index {1}: {0}".format(uv[1], i))
		'''

		Verts.append(pos)
		Normals.append(norm)
		UV.append(uv)
		if VERBOSITY > 1:
			print("{:6.3f} {:6.3f} {:6.3f} | {:6.3f} {:6.3f} {:6.3f} | {:6.3f} {:6.3f}".format(pos[0], pos[1], pos[2], norm[0], norm[1], norm[2], uv[0], uv[1]))
	return (Verts, Normals, UV)


def parseCollisionVertices(f, NumVerts):
	Verts = []
	for i in range(NumVerts):
		pos = struct.unpack("<fff", f.read(12))
		Verts.append(pos)
		if VERBOSITY > 1:
			print("{:6.3f} {:6.3f} {:6.3f}".format(pos[0], pos[1], pos[2]))
	return (Verts, [], [])

def parsIndexArray(f, NumIndices):
	Indices = []
	for i in range(NumIndices):
		tell = f.tell()
		index = readShort(f)
		if VERBOSITY > 2:
			print("{0}: {1}".format(hex(tell), index))
		Indices.append(index)
	return Indices

# do not use this method
def parsIndexTris(f, NumTris):
	Indices = []
	for i in range(NumTris / 3):
		index = struct.unpack("<HHH", f.read(3*2))
		index = (index[1], index[0], index[2]);
		if VERBOSITY > 1:
			print("{:3} {:3} {:3}".format(index[0], index[1], index[2]))
		Indices.append(list(index))
	return Indices

def indicesToTriangles(indices):
	triangles = len(indices) / 3
	result = []
	for i in range(triangles):
		index = (indices[i*3+0], indices[i*3+1], indices[i*3+2])
		result.append(index)
		if VERBOSITY > 1:
			print("{:3} {:3} {:3}".format(index[0], index[1], index[2]))
	return result

def indicesToTriangleStrip(indices):
	triangles = (len(indices)-1) / 2
	result = []
	for i in range(triangles):
		index = (indices[i*2+0], indices[i*2+1], indices[i*2+2])
		result.append(index)
		if VERBOSITY > 1:
			print("{:3} {:3} {:3}".format(index[0], index[1], index[2]))
	return result

def parseQuads(f, NumQuads):
	result = []
	for i in range(NumQuads):
		quad = struct.unpack("<HHHH", f.read(4*2))
		quad = (quad[0], quad[1], quad[2], quad[3])
		result.append(quad)
		if VERBOSITY > 1:
			print("{:3} {:3} {:3} {:3}".format(quad[0], quad[1], quad[2], quad[3]))
	return result

def convert(f):
	footprint = readInt(f)
	if 0x4e565831 != footprint:
		raise NameError("File is not recognized as .NVX")

	NumVerts = readInt(f)
	NumIndices = readInt(f)
	NumQuads = readInt(f)
	Format = readInt(f)
	#Format = readBits(_b, 2, 0)
	#_c = readBits(_b, 30, 2)
	dataOffset = readInt(f)
	dataSize = readInt(f)

	if ANALYZE_ONLY:
		return "{}, {}, {}, {}".format(Format, NumIndices, NumQuads, NumVerts)


	print("Format: {4} Verts: {0} Indices: {1} Quads: {5}. Data: {2}, size: {3}".format(NumVerts, NumIndices, dataOffset, dataSize, Format, NumQuads))

	Vertices = []
	Normals = []
	Uvs = []
	Indices = []
	Quads = []

	f.seek(dataOffset)

	if Format == FORMAT_COLLISION:
		(Vertices, Normals, Uvs) = parseCollisionVertices(f, NumVerts)
		Indices = parsIndexArray(f, NumIndices)
	elif Format == FORMAT_MODEL:
		(Vertices, Normals, Uvs) = parseModelVertices(f, NumVerts)
		#Indices = parsIndexTris(f, NumIndices)
		Quads = parseQuads(f, NumQuads)
		Indices = parsIndexArray(f, NumIndices)
		Indices = indicesToTriangles(Indices)
		#Indices = indicesToTriangleStrip(Indices)
	else:
		raise NameError("File fromat unknown: {}, _a:{}".format(Format, _a))

	'''
	minIdx = min(Indices)
	maxIdx = max(Indices)
	if minIdx != 0 or maxIdx != NumVerts-1:
		raise NameError("Min idx is {0} when expected 0. Max idx is {1} when expected {2}".format(minIdx, maxIdx, NumVerts-1))
	'''

	#readVertices(f, NumVerts, Vertices, Format)
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
	Mesh = (Vertices, Normals, Uvs, Indices);
	return Mesh

def exportMeshToObj(mesh, fName):
	f = open(fName + ".obj", "w")
	hasNormals = len(mesh[1]) > 0
	hasUvs = len(mesh[2]) > 0
	for v in mesh[0]:
		f.write("v {0:.6f} {1:.6f} {2:.6f}\n".format(v[0], v[1], v[2]))
	for vn in mesh[1]:
		f.write("vn {0:.6f} {1:.6f} {2:.6f}\n".format(vn[0], vn[1], vn[2]))
	for vt in mesh[2]:
		f.write("vt {0:.6f} {1:.6f}\n".format(vt[0], vt[1]))

	f.write("s off\n")
	indexes = mesh[3]
	indexNum = len(indexes)
	strFormat = "f {0} {1} {2}\n"
	if hasNormals:
		if hasUvs:
			strFormat = "f {0}/{0}/{0} {1}/{1}/{1} {2}/{2}/{2}\n"
		else:
			strFormat = "f {0}//{0} {1}//{1} {2}//{2}\n"
	else:
		if hasUvs:
			strFormat = "f {0}/{0} {1}/{1} {2}/{2}\n"
		else:
			strFormat = "f {0} {1} {2}\n"

	#strFormat = "f {0}/{0} {1}/{1} {2}/{2}\n"
	for i in range(indexNum/3):
		f.write(strFormat.format(indexes[i+0], indexes[i+1], indexes[i+2]))

	f.close()

def exportMeshToRaw(mesh, fName):
	f = open(fName + ".raw", "w")

	verts = mesh[0]
	indexes = mesh[3]
	indexNum = len(indexes)
	strFormat = "{} {} {} {} {} {} {} {} {}\n"
	for i in range(indexNum/3):
		a = verts[indexes[i+0]]
		b = verts[indexes[i+1]]
		c = verts[indexes[i+2]]
		f.write(strFormat.format(a[0], a[1], a[2], b[0], b[1], b[2], c[0], c[1], c[2]))

	f.close()

def exportToThree(mesh, fName):
	f = open(fName + ".js", "w")
	verts = mesh[0]
	lastVert = len(verts) - 1
	f.write("var MeshVerts = [\n")
	for i in range(lastVert):
		f.write("	[{:.6f}, {:.6f}, {:.6f}],\n".format(verts[i][0], verts[i][1], verts[i][2]))
	f.write("	[{:.6f}, {:.6f}, {:.6f}]\n".format(verts[lastVert][0], verts[lastVert][1], verts[lastVert][2]))
	f.write("];\n")

	normals = mesh[1]
	lastNormal = len(normals) - 1
	f.write("var MeshNormals = [\n")
	for i in range(lastNormal):
		f.write("	[{:.6f}, {:.6f}, {:.6f}],\n".format(normals[i][0], normals[i][1], normals[i][2]))
	f.write("	[{:.6f}, {:.6f}, {:.6f}]\n".format(normals[lastNormal][0], normals[lastNormal][1], normals[lastNormal][2]))
	f.write("];\n")

	uvs = mesh[2]
	lastuv = len(uvs) - 1
	f.write("var MeshUvs = [\n")
	for i in range(lastuv):
		f.write("	[{:.6f}, {:.6f}],\n".format(uvs[i][0], uvs[i][1]))
	f.write("	[{:.6f}, {:.6f}]\n".format(uvs[lastuv][0], uvs[lastuv][1]))
	f.write("];\n")

	indexes = mesh[3]
	lastIndex = len(indexes) - 1
	f.write("var MeshIndices = [\n")
	for i in range(lastIndex):
		f.write("	[{0}, {1}, {2}],\n".format(indexes[i][0], indexes[i][1], indexes[i][2]))
	f.write("	[{0}, {1}, {2}]\n".format(indexes[lastIndex][0], indexes[lastIndex][1], indexes[lastIndex][2]))
	f.write("];\n")

	f.close()

def saveMesh(mesh, fName):
	if ANALYZE_ONLY:
		print("({}, \"{}\"),".format(mesh, fName.replace('\\', '/')))
		return
	#exportMeshToObj(mesh, fName)
	#exportMeshToRaw(mesh, fName)
	exportToThree(mesh, fName)
	None

logFile = open("nvx.log", 'w')

def convertFile(name):
	if VERBOSITY > 0 and not ANALYZE_ONLY:
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

	except NameError as e:
		error = "Error in file `{0}`: {1}".format(name, e)
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
