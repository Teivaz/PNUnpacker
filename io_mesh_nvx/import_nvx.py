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


import bpy, bmesh, struct

''' Format Description '''
MESH_HAS_POS =   0b00000001 # has xyz
MESH_HAS_NORM =  0b00000010 # has normals
MESH_HAS_COLOR = 0b00000100 # has color
MESH_HAS_UV0 =   0b00001000 # has UV0
MESH_HAS_UV1 =   0b00010000 # has UV1
MESH_HAS_UV2 =   0b00100000 # has UV2
MESH_HAS_UV3 =   0b01000000 # has UV3
MESH_HAS_LINKS=  0b10000000 # has joint indices for skinning and weights

class Mesh(object):
    Format = 0
    Positions = [] # [ (x, y, z), (x, y, z) ]
    Normals = [] # [ (x, y, z), (x, y, z) ]
    Colors = [] # [c, c, c]
    UV0 = [] # [ (u, v), (u, v) ]
    UV1 = [] # [ (u, v), (u, v) ]
    UV2 = [] # [ (u, v), (u, v) ]
    UV3 = [] # [ (u, v), (u, v) ]
    Groups = [] # [ ( (ia, ib, ic, id), (wa, wb, wc, wd) ), ... ]
    WingedEdges = [] # [ (a, b, c, d), (a, b, c, d) ]
    Indices = [] # [ (a, b, c), (a, b, c) ]
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
    for i in range(mesh.NumVerts):
        if mesh.Format & MESH_HAS_POS:
            v = struct.unpack("<fff", f.read(12))
            mesh.Positions.append(v)
        if mesh.Format & MESH_HAS_NORM:
            v = struct.unpack("<fff", f.read(12))
            mesh.Normals.append(v)
        if mesh.Format & MESH_HAS_COLOR:
            (v,) = struct.unpack("<I", f.read(4))
            mesh.Colors.append(v)
        if mesh.Format & MESH_HAS_UV0:
            v = struct.unpack("<ff", f.read(8))
            mesh.UV0.append(v)
        if mesh.Format & MESH_HAS_UV1:
            v = struct.unpack("<ff", f.read(8))
            mesh.UV1.append(v)
        if mesh.Format & MESH_HAS_UV2:
            v = struct.unpack("<ff", f.read(8))
            mesh.UV2.append(v)
        if mesh.Format & MESH_HAS_UV3:
            v = struct.unpack("<ff", f.read(8))
            mesh.UV3.append(v)
        if mesh.Format & MESH_HAS_LINKS:
            a = struct.unpack("<hhhh", f.read(8))
            v = struct.unpack("<ffff", f.read(16))
            mesh.Groups.append((a, v))
    return mesh
        
def parseIndexArray(f, mesh):
    Indices = mesh.Indices
    for i in range(mesh.NumIndices):
        tell = f.tell()
        index = readShort(f)
        Indices.append(index)
    return mesh

def indicesToTriangles(f, mesh):
    indices = mesh.Indices
    triangles = int(mesh.NumIndices / 3)
    result = []
    for i in range(triangles):
        index = (indices[i*3+0], indices[i*3+1], indices[i*3+2])
        result.append(index)
    mesh.Indices = result
    return mesh

def indicesToTriangleStrip(f, mesh):
    indices = mesh.Indices
    triangles = int((mesh.NumIndices-1) / 2)
    result = []
    for i in range(triangles):
        index = (indices[i*2+0], indices[i*2+1], indices[i*2+2])
        result.append(index)
    mesh.Indices = result
    return mesh

def parseQuads(f, mesh):
    result = mesh.WingedEdges
    for i in range(mesh.NumWingedEdges):
        quad = struct.unpack("<HHHH", f.read(4*2))
        quad = (quad[0], quad[1], quad[2], quad[3])
        result.append(quad)
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
    mesh = parseVerticesFormat(f, mesh)
    mesh = parseQuads(f, mesh)
    mesh = parseIndexArray(f, mesh)
    mesh = indicesToTriangles(f, mesh)
    return mesh

def assignGroups(mesh, obj):
    linkGroups = {}
    for i in range(mesh.NumVerts):
        (groups, weights) = mesh.Groups[i]
        for l in range(4):
            group = groups[l]
            if group == -1:
                break
            if group not in linkGroups:
                linkGroups[group] = []
            linkGroups[group].append((i, weights[l]))
    for group, vertices in linkGroups.items():
        vg = obj.vertex_groups.new(name=str(group))
        for (index, weight) in vertices:
            #add index to group with weight
            vg.add([index], weight, 'ADD')


def addMesh(filename, objName):
    filehandle = open(filename, "rb")
    mesh = convert(filehandle)
    filehandle.close()
    m = bpy.data.meshes.new(objName)
    m.from_pydata(mesh.Positions, [], mesh.Indices)
    m.normals_split_custom_set_from_vertices(mesh.Normals)

    hasUV = len(mesh.UV0) > 0
    if hasUV:
        m.uv_textures.new("UV0")
        bm = bmesh.new()
        bm.from_mesh(m)
        uv_layer = bm.loops.layers.uv[0]

        nFaces = len(bm.faces)
        bm.faces.ensure_lookup_table()
        for fi in range(nFaces):
            indices = mesh.Indices[fi]
            for i in range(3):
                bm.faces[fi].loops[i][uv_layer].uv = mesh.UV0[indices[i]]
        bm.to_mesh(m)

    scn = bpy.context.scene

    for o in scn.objects:
        o.select = False
    m.update()
    m.validate()
    nobj = bpy.data.objects.new(objName, m)
    scn.objects.link(nobj)
    nobj.select = True

    if scn.objects.active is None or scn.objects.active.mode == 'OBJECT':
        scn.objects.active = nobj
    assignGroups(mesh, nobj)
    return nobj



def read(filepath):
    #convert the filename to an object name
    objName = bpy.path.display_name_from_filepath(filepath)
    addMesh(filepath, objName)

