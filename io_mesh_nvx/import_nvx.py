# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>

"""
This script imports NVX format from Game Project Nomads based on Nebula Machine engine

NVX format is a set of vertices and faces. It can contain mesh with normals 
and UV coordinates or simple collision data with only coordinates.

Usage:
Execute this script from the "File->Import" menu and choose a NVX file to
open.

Notes:
Generates the standard verts and faces lists.
"""


import bpy, struct


VERBOSITY = 0
MESH_HAS_POS =  0b00000001 # 3 floats   Position
MESH_HAS_NORM = 0b00000010 # 3 floats   Normal
MESH_HAS_1_1I = 0b00000100 # 1 int      ?
MESH_HAS_UV =   0b00001000 # 2 floats   Texture UV coordinates
MESH_HAS_2_2F = 0b00010000 # 2 floats   ?
MESH_HAS_3_2F = 0b00100000 # 2 floats   ?
MESH_HAS_4_2F = 0b01000000 # 2 floats   ?
MESH_HAS_LINKS= 0b10000000 # 4 short 4 float

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
    if VERBOSITY > 1:
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

    FileInfo = "Format: {4} Verts: {0} Indices: {1} Quads: {5} Data: {2} Size: {3}".format(mesh.NumVerts, mesh.NumIndices, DataOffset, mesh.DataSize, Format, mesh.NumQuads)
    if VERBOSITY > 0:
        print(FileInfo)

    f.seek(DataOffset)

    mesh = parseVertivesFormat(f, mesh)
    mesh = parseQuads(f, mesh)
    mesh = parseIndexArray(f, mesh)
    mesh = indicesToTriangles(f, mesh)

    return mesh

def readMesh(filename, objName):
    filehandle = open(filename, "rb")

    mesh = convert(filehandle)
    Vertices = mesh.Positions
    Normals = mesh.Normals
    Uvs = mesh.UVs
    Indices = mesh.Triangles


    mesh = bpy.data.meshes.new(objName)
    mesh.from_pydata(Vertices, [], Indices)
    mesh.normals_split_custom_set_from_vertices(Normals)

    return mesh


def addMeshObj(mesh, objName):
    scn = bpy.context.scene

    for o in scn.objects:
        o.select = False

    mesh.update()
    mesh.validate()

    nobj = bpy.data.objects.new(objName, mesh)
    scn.objects.link(nobj)
    nobj.select = True

    if scn.objects.active is None or scn.objects.active.mode == 'OBJECT':
        scn.objects.active = nobj


def read(filepath):
    #convert the filename to an object name
    objName = bpy.path.display_name_from_filepath(filepath)
    mesh = readMesh(filepath, objName)
    addMeshObj(mesh, objName)
