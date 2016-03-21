import struct, os

''' Script settings '''
VERBOSITY = 1
USE_DEVELOPEMENT_FOLDER = False
ANALYZE_ONLY = False


if USE_DEVELOPEMENT_FOLDER:
	PATH = "123"
else:
	PATH = "../_data.npk"


''' Format Description '''
MESH_HAS_POS = 	0b00000001 # 3 floats	Position
MESH_HAS_NORM = 0b00000010 # 3 floats	Normal
MESH_HAS_1_1I = 0b00000100 # 1 int 		?
MESH_HAS_UV =   0b00001000 # 2 floats	Texture UV coordinates
MESH_HAS_2_2F = 0b00010000 # 2 floats	?
MESH_HAS_3_2F = 0b00100000 # 2 floats	?
MESH_HAS_4_2F = 0b01000000 # 2 floats	?
MESH_HAS_LINKS= 0b10000000 # 4 short 4 float

FORMAT_UNKNOWN_1 = 1     # 0b00000001 - pos
FORMAT_UNKNOWN_5 = 5     # 0b00000101 - pos, ?
FORMAT_UNKNOWN_121 = 121 # 0b01111001 - ...
FORMAT_UNKNOWN_3 = 3     # 0b00000011 - pos, norm
FORMAT_UNKNOWN_11 = 11   # 0b00001011 - pos, norm, uv
FORMAT_UNKNOWN_27 = 27   # 0b00011011 - pos, norm, uv, ?
FORMAT_UNKNOWN_139 = 139 # 0b10001011 - pos, norm, uv, ?

FORMAT_UNKNOWN_59 = 59   # 0b00111011 - pos, norm, uv, ?, ?, ?
FORMAT_UNKNOWN_19 = 19   # 0b00010011 - pos, norm, ?
FORMAT_UNKNOWN_123 = 123 # 0b01111011 - ...

''' /Defines '''

class Mesh(object):
	Format = 0
	Positions = []
	Normals = []
	UVs = []
	Quads = []
	Triangles = []
	NumVerts = 0
	NumQuads = 0
	NumIndices = 0
	DataSize = 0


def readInt(f):
	(r, ) = struct.unpack("<I", f.read(4))
	return r
def readShort(f):
	(r, ) = struct.unpack("<H", f.read(2))
	return r
def readFloat(f):
	(r, ) = struct.unpack("<f", f.read(4))
	return r

def parseVertivesFormat(f, mesh):
	if VERBOSITY > 0:
		debugString = ""
		if mesh.Format & MESH_HAS_POS:
			debugString += "        Position 3f        | "
		if mesh.Format & MESH_HAS_NORM:
			debugString += "        Normal  3f         | "
		if mesh.Format & MESH_HAS_1_1I:
			debugString += " 1? 1i | "
		if mesh.Format & MESH_HAS_UV:
			debugString += "  Texture UV 2f   | "
		if mesh.Format & MESH_HAS_2_2F:
			debugString += "     2?  2f       | "
		if mesh.Format & MESH_HAS_3_2F:
			debugString += "     3?  2f       | "
		if mesh.Format & MESH_HAS_4_2F:
			debugString += "     4?  2f       | "
		if mesh.Format & MESH_HAS_LINKS:
			debugString += "     Links  4i         |             Links  4f               | "
		print(debugString)

	for i in range(mesh.NumVerts):
		debugString = ""
		if mesh.Format & MESH_HAS_POS:
			v = struct.unpack("<fff", f.read(12))
			mesh.Positions.append(v)
			if VERBOSITY > 1:
				debugString += "{:8.3f} {:8.3f} {:8.3f} | ".format(v[0], v[1], v[2])
		if mesh.Format & MESH_HAS_NORM:
			v = struct.unpack("<fff", f.read(12))
			mesh.Normals.append(v)
			if VERBOSITY > 1:
				debugString += "{:8.3f} {:8.3f} {:8.3f} | ".format(v[0], v[1], v[2])
		if mesh.Format & MESH_HAS_1_1I:
			v = readInt(f)
			# TODO: append to the mesh
			if VERBOSITY > 1:
				debugString += "{:6} | ".format(v)
		if mesh.Format & MESH_HAS_UV:
			v = struct.unpack("<ff", f.read(8))
			mesh.UVs.append(v)
			if VERBOSITY > 1:
				debugString += "{:8.3f} {:8.3f} | ".format(v[0], v[1])
		if mesh.Format & MESH_HAS_2_2F:
			v = struct.unpack("<ff", f.read(8))
			# TODO: append to the mesh
			if VERBOSITY > 1:
				debugString += "{:8.3f} {:8.3f} | ".format(v[0], v[1])
		if mesh.Format & MESH_HAS_3_2F:
			v = struct.unpack("<ff", f.read(8))
			# TODO: append to the mesh
			if VERBOSITY > 1:
				debugString += "{:8.3f} {:8.3f} | ".format(v[0], v[1])
		if mesh.Format & MESH_HAS_4_2F:
			v = struct.unpack("<ff", f.read(8))
			# TODO: append to the mesh
			if VERBOSITY > 1:
				debugString += "{:8.3f} {:8.3f} | ".format(v[0], v[1])
		if mesh.Format & MESH_HAS_LINKS:
			(a1, a2, a3, a4) = struct.unpack("<hhhh", f.read(8))
			v = struct.unpack("<ffff", f.read(16))
			# TODO: append to the mesh
			if VERBOSITY > 1:
				debugString += "{:5} {:5} {:5} {:5} | {:8.3f} {:8.3f} {:8.3f} {:8.3f} | ".format(a1, a2, a3, a4, v[0], v[1], v[2], v[3])
		if VERBOSITY > 1:
			print(debugString)

	return mesh
		
def parseIndexArray(f, mesh):
	Indices = mesh.Triangles
	for i in range(mesh.NumIndices):
		tell = f.tell()
		index = readShort(f)
		if VERBOSITY > 2:
			print("{0}: {1}".format(hex(tell), index))
		Indices.append(index)
	return mesh

def indicesToTriangles(f, mesh):
	indices = mesh.Triangles
	triangles = int(mesh.NumIndices / 3)
	result = []
	for i in range(triangles):
		index = (indices[i*3+0], indices[i*3+1], indices[i*3+2])
		result.append(index)
		if VERBOSITY > 1:
			print("{:5} {:5} {:5}".format(index[0], index[1], index[2]))
	mesh.Triangles = result
	return mesh

def indicesToTriangleStrip(f, mesh):
	indices = mesh.Triangles
	triangles = int((mesh.NumIndices-1) / 2)
	result = []
	for i in range(triangles):
		index = (indices[i*2+0], indices[i*2+1], indices[i*2+2])
		result.append(index)
		if VERBOSITY > 1:
			print("{:5} {:5} {:5}".format(index[0], index[1], index[2]))
	mesh.Triangles = result
	return mesh

def parseQuads(f, mesh):
	result = mesh.Quads
	for i in range(mesh.NumQuads):
		quad = struct.unpack("<HHHH", f.read(4*2))
		quad = (quad[0], quad[1], quad[2], quad[3])
		result.append(quad)
		if VERBOSITY > 1:
			print("{:5} {:5} {:5} {:5}".format(quad[0], quad[1], quad[2], quad[3]))
	return mesh

def convert(f):
	footprint = readInt(f)
	if 0x4e565831 != footprint:
		raise NameError("File is not recognized as .NVX")

	mesh = Mesh()

	mesh.NumVerts = readInt(f)
	mesh.NumIndices = readInt(f)
	mesh.NumQuads = readInt(f)
	Format = readInt(f)
	DataOffset = readInt(f)
	mesh.DataSize = readInt(f)

	mesh.Format = Format

	if ANALYZE_ONLY:
		return "{}, {}, {}, {}".format(Format, mesh.NumIndices, mesh.NumQuads, mesh.NumVerts)


	FileInfo = "Format: {4} Verts: {0} Indices: {1} Quads: {5} Data: {2} Size: {3}".format(mesh.NumVerts, mesh.NumIndices, DataOffset, mesh.DataSize, Format, mesh.NumQuads)
	if VERBOSITY > 0:
		print(FileInfo)

	f.seek(DataOffset)

	mesh = parseVertivesFormat(f, mesh)
	mesh = parseQuads(f, mesh)
	mesh = parseIndexArray(f, mesh)
	mesh = indicesToTriangles(f, mesh)

	return mesh

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
	for i in range(indexNum):
		f.write(strFormat.format(indexes[i][0], indexes[i][1], indexes[i][2]))

	f.close()

def exportMeshToRaw(mesh, fName):
	f = open(fName + ".raw", "w")

	verts = mesh[0]
	indexes = mesh[3]
	indexNum = len(indexes)
	strFormat = "{} {} {} {} {} {} {} {} {}\n"
	for i in range(indexNum):
		a = verts[indexes[i][0]]
		b = verts[indexes[i][1]]
		c = verts[indexes[i][2]]
		f.write(strFormat.format(a[0], a[1], a[2], b[0], b[1], b[2], c[0], c[1], c[2]))

	f.close()

def exportToThree(mesh, fName):
	f = open(fName + ".js", "w")
	verts = mesh.Positions
	lastVert = len(verts) - 1
	f.write("var MeshVerts = [\n")
	for i in range(lastVert):
		f.write("	[{:.6f}, {:.6f}, {:.6f}],\n".format(verts[i][0], verts[i][1], verts[i][2]))
	f.write("	[{:.6f}, {:.6f}, {:.6f}]\n".format(verts[lastVert][0], verts[lastVert][1], verts[lastVert][2]))
	f.write("];\n")

	normals = mesh.Normals
	lastNormal = len(normals) - 1
	f.write("var MeshNormals = [\n")
	if len(normals) > 0:
		for i in range(lastNormal):
			f.write("	[{:.6f}, {:.6f}, {:.6f}],\n".format(normals[i][0], normals[i][1], normals[i][2]))
		f.write("	[{:.6f}, {:.6f}, {:.6f}]\n".format(normals[lastNormal][0], normals[lastNormal][1], normals[lastNormal][2]))
	f.write("];\n")

	uvs = mesh.UVs
	lastuv = len(uvs) - 1
	f.write("var MeshUvs = [\n")
	if len(uvs) > 0:
		for i in range(lastuv):
			f.write("	[{:.6f}, {:.6f}],\n".format(uvs[i][0], uvs[i][1]))
		f.write("	[{:.6f}, {:.6f}]\n".format(uvs[lastuv][0], uvs[lastuv][1]))
	f.write("];\n")

	indexes = mesh.Triangles
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
	#exportToThree(mesh, fName)
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
