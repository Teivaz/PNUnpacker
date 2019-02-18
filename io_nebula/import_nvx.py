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

class Stream:
    def __init__(self, stream):
        self.stream = stream
    
    def seek(self, *args, **kwargs):
        return self.stream.seek(*args, **kwargs)

    def read_float(self):
        (v, ) = struct.unpack("<f", self.stream.read(4))
        return v

    def write_float(self, value):
        self.stream.write(struct.pack("<f", value))
    
    def read_byte(self):
        (v, ) = struct.unpack("<B", self.stream.read(1))
        return v

    def write_byte(self, value):
        self.stream.write(struct.pack("<B", value))
    
    def read_ushort(self):
        (v, ) = struct.unpack("<H", self.stream.read(2))
        return v

    def write_ushort(self, value):
        self.stream.write(struct.pack("<H", value))
    
    def read_uint(self):
        (v, ) = struct.unpack("<I", self.stream.read(4))
        return v

    def write_uint(self, value):
        self.stream.write(struct.pack("<I", value))

class Vector3:
    def __init__(self, x=0, y=0, z=0, stream=None):
        self.x = x
        self.y = y
        self.z = z
        if stream:
            self.from_stream(stream)

    def __iter__(self):
        return iter((self.x, self.y, self.z))

    def from_stream(self, stream):
        self.x = stream.read_float()
        self.y = stream.read_float()
        self.z = stream.read_float()

    def to_stream(self, stream):
        stream.write_float(self.x)
        stream.write_float(self.y)
        stream.write_float(self.z)

class Vector2:
    def __init__(self, x=0, y=0, stream=None):
        self.x = x
        self.y = y
        if stream:
            self.from_stream(stream)

    def __iter__(self):
        return iter((self.x, self.y))

    def from_stream(self, stream):
        self.x = stream.read_float()
        self.y = stream.read_float()

    def to_stream(self, stream):
        stream.write_float(self.x)
        stream.write_float(self.y)

class Color:
    def __init__(self, r=0, g=0, b=0, a=0, stream=None):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        if stream:
            self.from_stream(stream)

    def __iter__(self):
        return iter((self.r, self.g, self.b, self.a))

    def from_stream(self, stream):
        self.r = stream.read_byte()
        self.g = stream.read_byte()
        self.b = stream.read_byte()
        self.a = stream.read_byte()

    def to_stream(self, stream):
        stream.write_byte(self.r)
        stream.write_byte(self.g)
        stream.write_byte(self.b)
        stream.write_byte(self.a)

class Quad:
    def __init__(self, a=0, b=0, c=0, d=0, stream=None):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        if stream:
            self.from_stream(stream)

    def __iter__(self):
        return iter((self.a, self.b, self.c, self.d))

    def from_stream(self, stream):
        self.a = stream.read_ushort()
        self.b = stream.read_ushort()
        self.c = stream.read_ushort()
        self.d = stream.read_ushort()

    def to_stream(self, stream):
        stream.write_ushort(self.a)
        stream.write_ushort(self.b)
        stream.write_ushort(self.c)
        stream.write_ushort(self.d)

class BoneGroup:
    def __init__(self, b0=0, b1=0, b2=0, b3=0, w0=0, w1=0, w2=0, w3=0, stream=None):
        self.b0 = b0
        self.b1 = b1
        self.b2 = b2
        self.b3 = b3
        self.w0 = w0
        self.w1 = w1
        self.w2 = w2
        self.w3 = w3
        if stream:
            self.from_stream(stream)

    def from_stream(self, stream):
        self.b0 = stream.read_ushort()
        self.b1 = stream.read_ushort()
        self.b2 = stream.read_ushort()
        self.b3 = stream.read_ushort()
        self.w0 = stream.read_float()
        self.w1 = stream.read_float()
        self.w2 = stream.read_float()
        self.w3 = stream.read_float()

    def to_stream(self, stream):
        stream.write_ushort(self.b0)
        stream.write_ushort(self.b1)
        stream.write_ushort(self.b2)
        stream.write_ushort(self.b3)
        stream.write_float(self.w0)
        stream.write_float(self.w1)
        stream.write_float(self.w2)
        stream.write_float(self.w3)


class Mesh(object):
    HAS_POS = 0b00000001 # has xyz
    HAS_NORM = 0b00000010 # has normals
    HAS_COLOR = 0b00000100 # has color
    HAS_UV0 = 0b00001000 # has UV0
    HAS_UV1 = 0b00010000 # has UV1
    HAS_UV2 = 0b00100000 # has UV2
    HAS_UV3 = 0b01000000 # has UV3
    HAS_BONE_GROUPS = 0b10000000 # has joint indices for skinning and weights

    def __init__(self, stream=None):
        self.reset()
        if stream:
            self.from_stream(stream)

    def reset(self):
        self.positions = None
        self.normals = None
        self.color = None
        self.uv0 = None
        self.uv1 = None
        self.uv2 = None
        self.uv3 = None
        self.groups = None
        self.quads = []
        self.indices = []

    def from_stream(self, stream):
        if 0x4e565831 != stream.read_uint():
            raise NameError("File is not recognized as .NVX")
        self.reset()
        vertex_count = stream.read_uint()
        index_count = stream.read_uint()
        winged_edge_count = stream.read_uint()
        format = stream.read_uint()
        data_offset = stream.read_uint()
        data_size = stream.read_uint()

        stream.seek(data_offset)
        self._read_vertices(format, vertex_count, stream)
        self._read_quads(winged_edge_count, stream)
        self._read_indices(index_count, stream)

    def _read_vertices(self, format, length, stream):
        if format & Mesh.HAS_POS:
            self.positions = []
        if format & Mesh.HAS_NORM:
            self.normals = []
        if format & Mesh.HAS_COLOR:
            self.color = []
        if format & Mesh.HAS_UV0:
            self.uv0 = []
        if format & Mesh.HAS_UV1:
            self.uv1 = []
        if format & Mesh.HAS_UV2:
            self.uv2 = []
        if format & Mesh.HAS_UV3:
            self.uv3 = []
        if format & Mesh.HAS_BONE_GROUPS:
            self.groups = []
        
        for _ in range(length):
            self._read_vertex(format, stream)

    def _read_vertex(self, format, stream):
        if format & Mesh.HAS_POS:
            self.positions.append(Vector3(stream=stream))
        if format & Mesh.HAS_NORM:
            self.normals.append(Vector3(stream=stream))
        if format & Mesh.HAS_COLOR:
            self.color.append(Color(stream=stream))
        if format & Mesh.HAS_UV0:
            self.uv0.append(Vector2(stream=stream))
        if format & Mesh.HAS_UV1:
            self.uv1.append(Vector2(stream=stream))
        if format & Mesh.HAS_UV2:
            self.uv2.append(Vector2(stream=stream))
        if format & Mesh.HAS_UV3:
            self.uv3.append(Vector2(stream=stream))
        if format & Mesh.HAS_BONE_GROUPS:
            self.groups.append(BoneGroup(stream=stream))

    def _read_quads(self, winged_edge_count, stream):
        for _ in range(winged_edge_count):
            self.quads.append(Quad(stream=stream))

    def _read_indices(self, index_count, stream):
        for _ in range(index_count):
            self.indices.append(stream.read_ushort())

    def indices_as_triangles(self):
        triangle_count = int(len(self.indices) / 3)
        result = []
        for i in range(triangle_count):
            result.append(tuple(self.indices[i*3:i*3+3]))
        return result

def as_data(array):
    return [d.data() for d in array]


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
    
    with open(filename, "rb") as f:
        stream = Stream(f)
        mesh = Mesh(stream=stream)

    mesh_b = bpy.data.meshes.new(objName)
    mesh_b.from_pydata(mesh.positions, [], mesh.indices_as_triangles())
    if mesh.normals:
        mesh_b.normals_split_custom_set_from_vertices(mesh.normals)

    if mesh.uv0:
        mesh_b.uv_textures.new("UV0")
        bm = bmesh.new()
        bm.from_mesh(m)
        uv_layer = bm.loops.layers.uv[0]
        nFaces = len(bm.faces)
        indices = mesh.indices_as_triangles()
        for fi in range(nFaces):
            index = indices[fi]
            for i in range(3):
                bm.faces[fi].loops[i][uv_layer].uv = mesh.UV0[indices[i]]
        bm.to_mesh(mesh_b)


    """

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
    """

    scn = bpy.context.scene

    for o in scn.objects:
        o.select = False
    mesh_b.update()
    mesh_b.validate()
    nobj = bpy.data.objects.new(objName, mesh_b)
    scn.objects.link(nobj)
    nobj.select = True

    if scn.objects.active is None or scn.objects.active.mode == 'OBJECT':
        scn.objects.active = nobj
    #assignGroups(mesh, nobj)
    return nobj



def read(filepath):
    #convert the filename to an object name
    objName = bpy.path.display_name_from_filepath(filepath)
    addMesh(filepath, objName)

