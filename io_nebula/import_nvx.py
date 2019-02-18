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

from .stream import InputStream
from .types import Vector3, Vector2, Color, Quad, BoneGroup
import bpy, bmesh, struct
from bpy.props import StringProperty, BoolProperty

class NvxImporter(bpy.types.Operator):
    bl_idname = "import_mesh.nvx"
    bl_label = "Import NVX"
    bl_options = {'UNDO'}

    filepath = StringProperty(subtype='FILE_PATH')
    filter_glob = StringProperty(default="*.nvx", options={'HIDDEN'})

    def execute(self, context):
        objName = bpy.path.display_name_from_filepath(self.filepath)
        addMesh(self.filepath, objName)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


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
        if "NVX1" != stream.read_tag_name():
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
        stream = InputStream(f)
        mesh = Mesh(stream=stream)

    mesh_b = bpy.data.meshes.new(objName)
    mesh_b.from_pydata(mesh.positions, [], mesh.indices_as_triangles())

    
    """
    if mesh.normals:
        mesh_b.normals_split_custom_set_from_vertices(mesh.normals)

    if mesh.uv0:
        mesh_b.uv_textures.new("UV0")
        bm = bmesh.new()
        bm.from_mesh(mesh_b)
        uv_layer = bm.loops.layers.uv[0]
        nFaces = len(bm.faces)
        indices = mesh.indices_as_triangles()
        for fi in range(nFaces):
            index = indices[fi]
            for i in range(3):
                bm.faces[fi].loops[i][uv_layer].uv = mesh.UV0[indices[i]]
        bm.to_mesh(mesh_b)



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

