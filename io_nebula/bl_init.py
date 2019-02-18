
bl_info = {
    "name": "Nebula Machine mesh format (.nvx)",
    "author": "Teivaz",
    "version": (0, 2),
    "blender": (2, 57, 0),
    "location": "File > Import-Export > Nebula (.nvx) ",
    "description": "Import-Export Nebula",
    "warning": "",
    "wiki_url": ""
                "",
    "category": "Import-Export",
}

if "bpy" in locals():
    import importlib
    if "import_nvx" in locals():
        importlib.reload(import_nvx)
    if "import_n" in locals():
        importlib.reload(import_n)
    if "import_nax" in locals():
        importlib.reload(import_nax)
else:
    import bpy

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ExportHelper

class NvxImporter(bpy.types.Operator):
    """Load NVX triangle mesh data"""
    bl_idname = "import_mesh.nvx"
    bl_label = "Import NVX"
    bl_options = {'UNDO'}

    filepath = StringProperty(subtype='FILE_PATH')
    filter_glob = StringProperty(default="*.nvx", options={'HIDDEN'})

    def execute(self, context):
        from . import import_nvx
        import_nvx.read(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

class NImporter(bpy.types.Operator):
    """Load N bones data"""
    bl_idname = "import_script.n"
    bl_label = "Import N"
    bl_options = {'UNDO'}

    filepath = StringProperty(subtype='FILE_PATH')
    filter_glob = StringProperty(default="*.n", options={'HIDDEN'})

    def execute(self, context):
        from . import import_n
        import_n.read(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

class NaxImporter(bpy.types.Operator):
    """Load NAX triangle mesh data"""
    bl_idname = "import_anim.nax"
    bl_label = "Import NAX"
    bl_options = {'UNDO'}

    filepath = StringProperty(subtype='FILE_PATH')
    filter_glob = StringProperty(default="*.nax", options={'HIDDEN'})

    def execute(self, context):
        from . import import_nax
        import_nax.read(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

def menu_import(self, context):
    self.layout.operator(NvxImporter.bl_idname, text="Nebula mesh (.nvx)")
    self.layout.operator(NImporter.bl_idname, text="Nebula script (.n)")
    self.layout.operator(NaxImporter.bl_idname, text="Nebula mesh (.nax)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_import)

def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_import)
