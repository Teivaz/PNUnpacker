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

from contextlib import contextmanager
from .stream import InputStream, OutputStream
from .types import Vector3
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
        object_name = bpy.path.display_name_from_filepath(self.filepath)
        load_mesh(self.filepath, object_name)
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
    filepath = StringProperty(subtype="FILE_PATH")

    use_selection = BoolProperty(
            name="Selection Only",
            description="Export selected objects only",
            default=False,
            )

    def execute(self, context):
        file_path = bpy.path.ensure_ext(self.filepath, ".nvx")
        scene = context.scene
        objects = (ob for ob in scene.objects if ob.is_visible(scene) and ob.select and ob.type in ("MESH"))
        if objects:
            save_mesh(file_path, next(objects))
        return {"FINISHED"}

    def invoke(self, context, event):
        if not self.filepath:
            self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".nvx")
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {'RUNNING_MODAL'}


@contextmanager
def triangulated_mesh(obj):
    bl_mesh = bmesh.new()
    bl_mesh.from_mesh(obj.data)
    bmesh.ops.triangulate(bl_mesh, faces=bl_mesh.faces[:], quad_method=0, ngon_method=0)
    mesh = bpy.data.meshes.new(obj.name+"_triangulated")
    bl_mesh.to_mesh(mesh)
    bl_mesh.free()
    yield mesh
    bpy.data.meshes.remove(mesh)


def save_mesh(filename, bl_object):
    mesh = Mesh()

    has_custom_normals = bl_object.data.has_custom_normals

    with triangulated_mesh(bl_object) as bl_mesh:
        bl_mesh = bl_object.data
        total_vertices = len(bl_mesh.vertices)
        mesh.positions = [Vector3()] * total_vertices
        for v in bl_mesh.vertices:
            mesh.positions[v.index] = Vector3(*v.co[:])
        
        if has_custom_normals:
            mesh.normals = [Vector3()] * total_vertices
            bl_mesh.calc_normals_split()

        for l in bl_mesh.loops:
            mesh.indices.append(l.vertex_index)
            if has_custom_normals:
                mesh.normals[l.vertex_index] = Vector3(*l.normal[:])

        with open(filename, "wb") as f:
            stream = OutputStream(f)
            mesh.to_stream(stream)


def load_mesh(filename, object_name):
    with open(filename, "rb") as f:
        stream = InputStream(f)
        mesh = Mesh(stream=stream)

    bl_mesh = bpy.data.meshes.new(object_name)
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

    def add_groups(obj):
        groups = mesh.groups_as_map()
        for group, vertices in groups.items():
            vg = obj.vertex_groups.new(name=str(group))
            for (index, weight) in vertices:
                #add index to group with weight
                vg.add([index], weight, "ADD")

    bl_mesh.update()
    bl_mesh.validate()
    scn = bpy.context.scene

    for o in scn.objects:
        o.select = False
    nobj = bpy.data.objects.new(object_name, bl_mesh)
    scn.objects.link(nobj)
    nobj.select = True

    if scn.objects.active is None or scn.objects.active.mode == "OBJECT":
        scn.objects.active = nobj
    add_groups(nobj)
    return nobj

