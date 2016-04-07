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

def readInt(f):
    (r, ) = struct.unpack("<I", f.read(4))
    return r
def readShort(f):
    (r, ) = struct.unpack("<H", f.read(2))
    return r
def readFloat(f):
    (r, ) = struct.unpack("<f", f.read(4))
    return r

class Mesh(object):
    Format = None
    Positions = None # [ (x, y, z), (x, y, z) ]
    Normals = None # [ (x, y, z), (x, y, z) ]
    Colors = None # [c, c, c]
    UV0 = None # [ (u, v), (u, v) ]
    UV1 = None # [ (u, v), (u, v) ]
    UV2 = None # [ (u, v), (u, v) ]
    UV3 = None # [ (u, v), (u, v) ]
    Groups = None # [ ( (ia, ib, ic, id), (wa, wb, wc, wd) ), ... ]
    WingedEdges = None # [ (a, b, c, d), (a, b, c, d) ]
    Indices = None # [ (a, b, c), (a, b, c) ]
    NumVerts = None
    NumWingedEdges = None
    NumIndices = None
    DataSize = None

    def __init__(self, f):
        self.Positions = [] # [ (x, y, z), (x, y, z) ]
        self.Normals = [] # [ (x, y, z), (x, y, z) ]
        self.Colors = [] # [c, c, c]
        self.UV0 = [] # [ (u, v), (u, v) ]
        self.UV1 = [] # [ (u, v), (u, v) ]
        self.UV2 = [] # [ (u, v), (u, v) ]
        self.UV3 = [] # [ (u, v), (u, v) ]
        self.Groups = [] # [ ( (ia, ib, ic, id), (wa, wb, wc, wd) ), ... ]
        self.WingedEdges = [] # [ (a, b, c, d), (a, b, c, d) ]
        self.Indices = [] # [ (a, b, c), (a, b, c) ]
        self.NumVerts = readInt(f)
        self.NumIndices = readInt(f)
        self.NumWingedEdges = readInt(f)
        self.Format = readInt(f)
        DataOffset = readInt(f)
        self.DataSize = readInt(f)
        f.seek(DataOffset)


    def parseVerticesFormat(self, f):
        for i in range(self.NumVerts):
            if self.Format & MESH_HAS_POS:
                v = struct.unpack("<fff", f.read(12))
                self.Positions.append(v)
            if self.Format & MESH_HAS_NORM:
                v = struct.unpack("<fff", f.read(12))
                self.Normals.append(v)
            if self.Format & MESH_HAS_COLOR:
                (v,) = struct.unpack("<I", f.read(4))
                self.Colors.append(v)
            if self.Format & MESH_HAS_UV0:
                v = struct.unpack("<ff", f.read(8))
                self.UV0.append(v)
            if self.Format & MESH_HAS_UV1:
                v = struct.unpack("<ff", f.read(8))
                self.UV1.append(v)
            if self.Format & MESH_HAS_UV2:
                v = struct.unpack("<ff", f.read(8))
                self.UV2.append(v)
            if self.Format & MESH_HAS_UV3:
                v = struct.unpack("<ff", f.read(8))
                self.UV3.append(v)
            if self.Format & MESH_HAS_LINKS:
                a = struct.unpack("<hhhh", f.read(8))
                v = struct.unpack("<ffff", f.read(16))
                self.Groups.append((a, v))
        
    def parseIndexArray(self, f):
        for i in range(self.NumIndices):
            tell = f.tell()
            index = readShort(f)
            self.Indices.append(index)

    def indicesToTriangles(self, f):
        indices = self.Indices
        triangles = int(self.NumIndices / 3)
        result = []
        for i in range(triangles):
            index = (indices[i*3+0], indices[i*3+1], indices[i*3+2])
            result.append(index)
        self.Indices = result

    def parseQuads(self, f):
        result = self.WingedEdges
        for i in range(self.NumWingedEdges):
            quad = struct.unpack("<HHHH", f.read(4*2))
            quad = (quad[0], quad[1], quad[2], quad[3])
            result.append(quad)
        self.WingedEdges = result

def convert(f):
    footprint = readInt(f)
    if 0x4e565831 != footprint:
        raise NameError("File is not recognized as .NVX")
    mesh = Mesh(f)
    mesh.parseVerticesFormat(f)
    mesh.parseQuads(f)
    mesh.parseIndexArray(f)
    mesh.indicesToTriangles(f)
    return mesh

def assignGroups(mesh, obj):
    if len(mesh.Groups) == 0:
        return
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
    if len(mesh.Normals) > 0:
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

