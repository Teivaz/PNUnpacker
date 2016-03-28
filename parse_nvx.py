import struct, os

''' Script settings '''
VERBOSITY = 2
USE_DEVELOPEMENT_FOLDER = True
ANALYZE_ONLY = False

if ANALYZE_ONLY:
	import numpy as np
	import matplotlib.pyplot as plt

if USE_DEVELOPEMENT_FOLDER:
	PATH = "d:/projects/islander_old/nvx/skin.nvx"
else:
	PATH = "_data.npk"


''' Format Description '''
MESH_HAS_POS = 	 0b00000001 # has xyz
MESH_HAS_NORM =  0b00000010 # has normals
MESH_HAS_COLOR = 0b00000100 # has color
MESH_HAS_UV0 =   0b00001000 # has UV0
MESH_HAS_UV1 =   0b00010000 # has UV1
MESH_HAS_UV2 =   0b00100000 # has UV2
MESH_HAS_UV3 =   0b01000000 # has UV3
MESH_HAS_LINKS=  0b10000000 # has joint indices for skinning and weights

class Mesh(object):
	Format = 0
	Positions = []
	Normals = []
	Colors = []
	UV0 = []
	UV1 = []
	UV2 = []
	UV3 = []
	WingedEdges = []
	Indices = []
	NumVerts = 0
	NumWingedEdges = 0
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

def parseVerticesFormat(f, mesh):
	if VERBOSITY > 1:
		debugString = ""
		if mesh.Format & MESH_HAS_POS:
			debugString += "        Position 3f        | "
		if mesh.Format & MESH_HAS_NORM:
			debugString += "        Normal  3f         | "
		if mesh.Format & MESH_HAS_COLOR:
			debugString += "    1? 1i     | "
		if mesh.Format & MESH_HAS_UV0:
			debugString += "  Texture UV0 2f  | "
		if mesh.Format & MESH_HAS_UV1:
			debugString += "  Texture UV1 2f  | "
		if mesh.Format & MESH_HAS_UV2:
			debugString += "  Texture UV2 2f  | "
		if mesh.Format & MESH_HAS_UV3:
			debugString += "  Texture UV3 2f  | "
		if mesh.Format & MESH_HAS_LINKS:
			debugString += "     Joints 4i         |"
			debugString += "             Joints 4f               | "
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
		if mesh.Format & MESH_HAS_COLOR:
			(v,) = struct.unpack("<I", f.read(4))
			mesh.Colors.append(v)
			if VERBOSITY > 1:
				debugString += " {:0x8} | ".format(v)
		if mesh.Format & MESH_HAS_UV0:
			v = struct.unpack("<ff", f.read(8))
			mesh.UV0.append(v)
			if VERBOSITY > 1:
				debugString += "{:8.3f} {:8.3f} | ".format(v[0], v[1])
		if mesh.Format & MESH_HAS_UV1:
			v = struct.unpack("<ff", f.read(8))
			mesh.UV1.append(v)
			if VERBOSITY > 1:
				debugString += "{:8.3f} {:8.3f} | ".format(v[0], v[1])
		if mesh.Format & MESH_HAS_UV2:
			v = struct.unpack("<ff", f.read(8))
			mesh.UV2.append(v)
			if VERBOSITY > 1:
				debugString += "{:8.3f} {:8.3f} | ".format(v[0], v[1])
		if mesh.Format & MESH_HAS_UV3:
			v = struct.unpack("<ff", f.read(8))
			mesh.UV3.append(v)
			if VERBOSITY > 1:
				debugString += "{:8.3f} {:8.3f} | ".format(v[0], v[1])
		if mesh.Format & MESH_HAS_LINKS:
			a = struct.unpack("<hhhh", f.read(8))
			v = struct.unpack("<ffff", f.read(16))
			mesh.WingedEdges.append((a, v))
			if VERBOSITY > 1:
				debugString += "{:5} {:5} {:5} {:5} | {:8.3f} {:8.3f} {:8.3f} {:8.3f} | ".format(a[0], a[1], a[2], a[3], v[0], v[1], v[2], v[3])
		if VERBOSITY > 1:
			print(debugString)

	return mesh
		
def parseIndexArray(f, mesh):
	Indices = mesh.Indices
	for i in range(mesh.NumIndices):
		tell = f.tell()
		index = readShort(f)
		if VERBOSITY > 2:
			print("{0}: {1}".format(hex(tell), index))
		Indices.append(index)
	return mesh

def indicesToTriangles(f, mesh):
	indices = mesh.Indices
	triangles = int(mesh.NumIndices / 3)
	result = []
	for i in range(triangles):
		index = (indices[i*3+0], indices[i*3+1], indices[i*3+2])
		result.append(index)
		if VERBOSITY > 1:
			print("{:5} {:5} {:5}".format(index[0], index[1], index[2]))
	mesh.Indices = result
	return mesh

def indicesToTriangleStrip(f, mesh):
	indices = mesh.Indices
	triangles = int((mesh.NumIndices-1) / 2)
	result = []
	for i in range(triangles):
		index = (indices[i*2+0], indices[i*2+1], indices[i*2+2])
		result.append(index)
		if VERBOSITY > 1:
			print("{:5} {:5} {:5}".format(index[0], index[1], index[2]))
	mesh.Indices = result
	return mesh

def parseQuads(f, mesh):
	result = mesh.WingedEdges
	for i in range(mesh.NumWingedEdges):
		quad = struct.unpack("<HHHH", f.read(4*2))
		quad = (quad[0], quad[1], quad[2], quad[3])
		result.append(quad)
		if VERBOSITY > 1:
			print("{:5} {:5} {:5} {:5}".format(quad[0], quad[1], quad[2], quad[3]))
	mesh.WingedEdges = result
	return mesh

def convert(f):
	footprint = readInt(f)
	if 0x4e565831 != footprint:
		raise NameError("File is not recognized as .NVX")
	mesh = Mesh()
	mesh.NumVerts = readInt(f)
	mesh.NumIndices = readInt(f)
	mesh.NumWingedEdges = readInt(f)
	Format = readInt(f)
	DataOffset = readInt(f)
	mesh.DataSize = readInt(f)
	mesh.Format = Format
	f.seek(DataOffset)
	if ANALYZE_ONLY:
		if Format & MESH_HAS_COLOR > 0:
			mesh = parseVerticesFormat(f, mesh)
			return (True, mesh.I)
			return (True, np.histogram(mesh.I, bins=range(2048))[0])
			#return "{}".format()
		return (False, )

	FileInfo = "Format: {4} Verts: {0} Indices: {1} Quads: {5} Data: {2} Size: {3}".format(mesh.NumVerts, mesh.NumIndices, DataOffset, mesh.DataSize, Format, mesh.NumWingedEdges)
	if VERBOSITY > 0:
		print(FileInfo)
	mesh = parseVerticesFormat(f, mesh)
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

analyzedData = []

def saveMesh(mesh, fName):
	if ANALYZE_ONLY:
		if mesh[0]:
			global analyzedData
			analyzedData += mesh[1]
			#print y[0], y
			#raise NameError()
			#print("({}, \"{}\"),".format(mesh, fName.replace('\\', '/')))
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
		mesh = convert(f)
	except NameError as e:
		error = "Error in file `{0}`:\n\t{1}".format(name, e)
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
	if not os.path.isdir(path):
		return convertFile(path)
	dNames, fNames = listDirsAndFiles(path)
	for fName in fNames:
		convertFile(fName)
	for dName in dNames:
		convertDir(dName)

def main():
	convertDir(os.path.abspath(PATH))
	logFile.close()

	if ANALYZE_ONLY:
		bins= np.concatenate(([0], np.power(2, range(16))))
		print len(analyzedData)
		print bins
		a = np.histogram(analyzedData, bins=bins)
		y = a[0]
		x = a[1]
		x = (x[1:] + x[:-1]) / 2
		plt.plot(x, y, 'o')
		plt.xscale('log')
		plt.yscale('log')
		#data = np.concatenate((spread, center, flier_high, flier_low), 0)
		#plt.plot(analyzedData[0], analyzedData[1], 'ro')

		#plt.boxplot(analyzedData)
		plt.show()
main()
