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
    "version": (0, 2),
    "blender": (2, 57, 0),
    "location": "File > Import-Export > Nebula (.nvx) ",
    "description": "Import-Export Nebula",
    "warning": "",
    "wiki_url": ""
                "",
    "category": "Import-Export",
}

blender_addon = False
blender_reload = False

if "bpy" in locals():
    blender_addon = True
    blender_reload = True
else:    
    try:
        import bpy
        blender_addon = True
    except ImportError:
        blender_addon = False

if blender_reload:
    import importlib
    if "bl_nvx" in locals():
        importlib.reload(bl_nvx)
    if "import_n" in locals():
        importlib.reload(import_n)
    if "import_nax" in locals():
       importlib.reload(import_nax)

if blender_addon:
    from . import bl_nvx
    from . import import_n
    from . import import_nax

    def menu_import(self, context):
        self.layout.operator(bl_nvx.NvxImporter.bl_idname, text="Nebula mesh (.nvx)")
        self.layout.operator(import_n.NImporter.bl_idname, text="Nebula script (.n)")
        self.layout.operator(import_nax.NaxImporter.bl_idname, text="Nebula animation (.nax)")
        
    def menu_export(self, context):
        self.layout.operator(bl_nvx.NvxExporter.bl_idname, text="Nebula mesh (.nvx)")

    def register():
        bpy.utils.register_module(__name__)
        bpy.types.INFO_MT_file_import.append(menu_import)
        bpy.types.INFO_MT_file_export.append(menu_export)

    def unregister():
        bpy.utils.unregister_module(__name__)
        bpy.types.INFO_MT_file_import.remove(menu_import)
        bpy.types.INFO_MT_file_export.remove(menu_export)

