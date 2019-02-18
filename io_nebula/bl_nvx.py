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
from .nvx import Mesh
import bpy, bmesh, struct
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ExportHelper

class NvxImporter(bpy.types.Operator):
    bl_idname = "import_mesh.nvx"
    bl_label = "Import NVX"
    bl_options = {"UNDO"}

    filepath = StringProperty(subtype="FILE_PATH")
    filter_glob = StringProperty(default="*.nvx", options={"HIDDEN"})

    def execute(self, context):
        objName = bpy.path.display_name_from_filepath(self.filepath)
        addMesh(self.filepath, objName)
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {"RUNNING_MODAL"}

class NvxExporter(bpy.types.Operator, ExportHelper):
    bl_idname = "export_mesh.nvx"
    bl_label = "Export mesh as NVX"
    bl_options = {"UNDO"}

    filename_ext = ".nvx"
    filter_glob = StringProperty(default="*.nvx", options={"HIDDEN"})

    use_selection = BoolProperty(
            name="Selection Only",
            description="Export selected objects only",
            default=False,
            )

    def execute(self, context):
        return {"FINISHED"}


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
            vg.add([index], weight, "ADD")


def addMesh(filename, objName):
    with open(filename, "rb") as f:
        stream = InputStream(f)
        mesh = Mesh(stream=stream)

    bl_mesh = bpy.data.meshes.new(objName)
    bl_mesh.from_pydata(mesh.positions, [], mesh.indices_as_triangles())
    
    if mesh.normals:
        bl_mesh.create_normals_split()
        normals = [n.data() for n in mesh.normals]

        for l in bl_mesh.loops:
            l.normal[:] = normals[l.vertex_index]

        bl_mesh.normals_split_custom_set_from_vertices(normals)
        bl_mesh.use_auto_smooth = True

    def add_uv(data, name):
        indices_as_triangles = mesh.indices_as_triangles()
        bl_mesh.uv_textures.new(name)
        bm = bmesh.new()
        bm.from_mesh(bl_mesh)
        uv_layer = bm.loops.layers.uv[-1]

        nFaces = len(bm.faces)
        bm.faces.ensure_lookup_table()
        for fi in range(nFaces):
            indices = indices_as_triangles[fi]
            for i in range(3):
                bm.faces[fi].loops[i][uv_layer].uv = data[indices[i]]
        bm.to_mesh(bl_mesh)

    if mesh.uv0:
        add_uv(mesh.uv0, "UV0")
    if mesh.uv1:
        add_uv(mesh.uv1, "UV1")
    if mesh.uv2:
        add_uv(mesh.uv2, "UV2")
    if mesh.uv3:
        add_uv(mesh.uv3, "UV3")

    bl_mesh.update()
    bl_mesh.validate()
    scn = bpy.context.scene

    for o in scn.objects:
        o.select = False
    nobj = bpy.data.objects.new(objName, bl_mesh)
    scn.objects.link(nobj)
    nobj.select = True

    if scn.objects.active is None or scn.objects.active.mode == "OBJECT":
        scn.objects.active = nobj
    #assignGroups(mesh, nobj)
    return nobj
