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
This script imports armature bones from .N format from Game Project Nomads 
based on Nebula Machine engine

N format is a binary script format that might contain bone description.

Usage:
Execute this script from the "File->Import" menu and choose a N file to
open.

Notes:
Generates the armature bones
"""


import bpy, bmesh, struct
from mathutils import Vector, Matrix, Quaternion


def readShort(f):
    (value, ) = struct.unpack("<h", f.read(2))
    return value
def readInt(f):
    (value, ) = struct.unpack("<i", f.read(4))
    return value
def readBool(f):
    (value, ) = struct.unpack("<?", f.read(1))
    return value
def readFloat(f):
    (value, ) = struct.unpack("<f", f.read(4))
    return value
def readString(f):
    size = readShort(f)
    format = "{}s".format(size)
    (chars, ) = struct.unpack(format, f.read(size))
    return str(chars, encoding='UTF-8')
def readVoid(f):
    return ""
def op_new(f):
    a0 = readString(f)
    a1 = readString(f)
    return a0, a1
def op_sel(f):
    a0 = readString(f)
    return a0
def readArgs(f, code):
    result = []
    for c in code:
        v = Arguments[c](f)
        result.append(v)
    return result
Operators = {
    "_new": (op_new, "new"),
    "_sel": (op_sel, "sel"),
}
Arguments = {
    "s": readString,
    "o": readString,
    "f": readFloat,
    "i": readInt,
    "v": readVoid,
    "b": readBool,
}
Functions = {
    "ADJN": ("isifffffff", "addjoint") #node, name, parent, xyz, quat
}
def isOperator(tag):
    return tag in Operators

Bones = []
def addBone(params):
    (index, name, parentIndex, x, y, z,  a, b, c, d) = params
    Bones.append( (index, name, parentIndex, (x, y, z), (a, b, c, d)) )

def parseTag(tag, f):
    pos = f.tell()
    if isOperator(tag):
        (op, name) = Operators[tag]
        opResult = op(f)
    else:
        tagSize = readShort(f)
        if tag in Functions:
            (code, name) = Functions[tag]
            args = readArgs(f, code)
            addBone(args)
        f.seek(pos + tagSize + 2)

def readTag(f):
    (tag, ) = struct.unpack("4s", f.read(4))
    tag = tag[::-1]
    tag = str(tag, encoding='UTF-8')
    pos = f.tell()
    parseTag(tag, f)

def parse(f):
    f.seek(0, 2)
    fileEnd = f.tell()
    f.seek(0, 0)

    (footprint, ) = struct.unpack("<I", f.read(4))
    if footprint != 0x4e4f4230: #NOB0
        return
    header = readString(f)
    while f.tell() != fileEnd:
        readTag(f)

def convertFile(name):
    global Bones
    Bones = []
    f = open(name, "rb")
    try:
        parse(f)
    except NameError as e:
        print("Parsing error {}".format(e))
    f.close()
    return Bones

def createBones(bones, name):
    direction = (0,0.1,0)
    origin = (0,0,0)
    bpy.ops.object.add(
        type='ARMATURE', 
        enter_editmode=True,
        location=origin)
    ob = bpy.context.object
    ob.show_x_ray = True
    ob.name = name
    amt = ob.data
    amt.name = name+'Amt'
    amt.show_axes = True
    bpy.ops.object.mode_set(mode='EDIT')
    for (idx, name, pidx, pos, quat) in bones:
        bone = amt.edit_bones.new(str(idx))
        bone.head = pos
        if pidx != -1:
            pname = bones[pidx][1]
            parent = amt.edit_bones[str(pidx)]
            bone.parent = parent
            bone.use_connect = False
            bone.head = Vector(pos) + parent.head
        rot = Quaternion(quat)
        bone.tail = bone.head + rot * Vector(direction)
    bpy.ops.object.mode_set(mode='OBJECT')
    return ob

def read(filepath):
    #convert the filename to an object name
    bones = convertFile(filepath)
    if len(bones) > 0:
        objName = bpy.path.display_name_from_filepath(filepath)
        createBones(bones, objName)
        print('Creating bones')
    
#read('d:/projects/islander_old/nvx/_main.n')