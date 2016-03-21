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


bl_info = {
    "name": "Nebula Machine mesh format (.nvx)",
    "author": "Teivaz",
    "version": (0, 1),
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
else:
    import bpy

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ExportHelper


class NvxImporter(bpy.types.Operator):
    """Load NVX triangle mesh data"""
    bl_idname = "import_mesh.nvx"
    bl_label = "Import NVX"
    bl_options = {'UNDO'}

    filepath = StringProperty(
            subtype='FILE_PATH',
            )
    filter_glob = StringProperty(default="*.nvx", options={'HIDDEN'})

    def execute(self, context):
        from . import import_nvx
        import_nvx.read(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

def menu_import(self, context):
    self.layout.operator(NvxImporter.bl_idname, text="Nebula mesh (.nvx)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_import)

def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_import)

if __name__ == "__main__":
    register()
