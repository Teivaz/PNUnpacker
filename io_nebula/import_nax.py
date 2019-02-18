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
This script imports NAX format from Game Project Nomads based on Nebula Machine engine

NVX format is a set an animation.

Usage:
Execute this script from the "File->Import" menu and choose a NAX file to
open.

Notes:
Generates animation sequences.
"""

import bpy, bmesh, struct
from mathutils import Quaternion
from bpy.props import StringProperty

class NaxImporter(bpy.types.Operator):
    """Load NAX triangle mesh data"""
    bl_idname = "import_anim.nax"
    bl_label = "Import NAX"
    bl_options = {'UNDO'}

    filepath = StringProperty(subtype='FILE_PATH')
    filter_glob = StringProperty(default="*.nax", options={'HIDDEN'})

    def execute(self, context):
        read(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}



INTERP_STEP = 0
INTERP_LINEAR = 1
INTERP_QUAT = 2

REP_LOOP = 0
REP_ONCE = 1

KEY_VANILLA = 0
KEY_PACKED = 1

def ltof(float16):
    mult = 2.0 / float(0b1111111111111111)
    result = float(float16) * mult - 1.0
    return result
def readByte(f):
    (value, ) = struct.unpack("<b", f.read(1))
    return value
def readInt(f):
    (r, ) = struct.unpack("<I", f.read(4))
    return r
def readShort(f):
    (r, ) = struct.unpack("<H", f.read(2))
    return r
def readUShort(f):
    (value, ) = struct.unpack("<H", f.read(2))
    return value
def readFloat(f):
    (r, ) = struct.unpack("<f", f.read(4))
    return r
def readString(f):
    size = readShort(f)
    format = "{}s".format(size)
    (chars, ) = struct.unpack(format, f.read(size))
    return str(chars, encoding='UTF-8')
def readVoid(f):
    return ""
def readHFloat(f):
    val = readUShort(f)
    return ltof(val)

class Curve:
    Name = None
    StartKey = None
    NumKeys = None
    KeysPerSecond = None
    Interp = None
    Rep = None
    KeyType = None
    Data = None

    State = None
    Anim = None
    Channel = None
    Bone = None

    def __init__(self, f):
        self.stream = f

    def read(self):
        self.Data = []
        self.readCurveHeader()
        if self.KeyType == KEY_VANILLA:
            self.readCurveDataVanilla()
        elif self.KeyType == KEY_PACKED:
            self.readCurveDataPacked()
        else:
            raise NameError('Unknown key type {}'.format(self.KeyType))

    def readCurveHeader(self):
        footprint = readInt(self.stream)
        if footprint != 0x43484452: #CHDR
            raise NameError("Curve header does not match magic number 0x{:0x} at 0x{:0x}".format(footprint, self.stream.tell()))
        size = readInt(self.stream)
        streamStart = self.stream.tell()
        streamEnd = streamStart + size
        self.StartKey = readInt(self.stream)
        self.NumKeys = readInt(self.stream)
        self.KeysPerSecond = readFloat(self.stream)
        self.Interp = readByte(self.stream)
        self.Rep = readByte(self.stream)
        self.KeyType = readByte(self.stream)
        readByte(self.stream) # padding
        self.Name = readString(self.stream)
        nameSplit = self.Name.split('_')
        self.State = nameSplit[0]
        self.Anim = nameSplit[1]
        self.Channel = nameSplit[2]
        self.Bone = nameSplit[-1]
        IntepolationTypes = ["Step", "Linear", "Quaternion"]
        interp = IntepolationTypes[self.Interp]

    def readCurveDataVanilla(self):
        footprint = readInt(self.stream)
        if footprint != 0x43445456: #CDTV
            raise NameError("Curve data vanilla does not match magic number 0x{:0x} at 0x{:0x}".format(footprint, self.stream.tell()))
        size = readInt(self.stream)
        streamStart = self.stream.tell()
        streamEnd = streamStart + size
        while self.stream.tell() != streamEnd:
            self.Data.append((readFloat(self.stream),readFloat(self.stream),readFloat(self.stream),readFloat(self.stream)))

    def readCurveDataPacked(self):
        footprint = readInt(self.stream)
        if footprint != 0x43445450: #CDTP
            raise NameError("Curve data packed does not match magic number 0x{:0x} at 0x{:0x}".format(footprint, self.stream.tell()))
        size = readInt(self.stream)
        streamStart = self.stream.tell()
        streamEnd = streamStart + size
        while self.stream.tell() != streamEnd:
            self.Data.append((readHFloat(self.stream),readHFloat(self.stream),readHFloat(self.stream),readHFloat(self.stream)))

def readHeader(f):
    (footprint, ) = struct.unpack("<I", f.read(4))
    if footprint != 0x4e415830: #NAX0
        raise NameError("File has invalid format")
    four = readInt(f)
    numCurves = readInt(f)
    return numCurves

# anim : {bone: (channel, data)}
def convert(f):
    f.seek(0, 2)
    fileEnd = f.tell()
    f.seek(0, 0)

    Animations = {}
    numCurves = readHeader(f)
    curves = []
    for i in range(numCurves):
        curve = Curve(f)
        curve.read()
        curves.append(curve)
        animName = curve.State + '_' + curve.Anim
        if animName not in Animations:
            Animations[animName] = {}
        animation = Animations[animName]
        if curve.Bone not in animation:
            animation[curve.Bone] = (curve.Channel, curve.Data)
    return Animations
    #return curves

gLastFrame = 0
def addAnimation(ob, anim, name):
    action = bpy.data.actions.new(name)
    ob.animation_data.action = action
    global gLastFrame
    lastFrame = 0
    for b in anim.items():
        bn, state = b
        bone = ob.pose.bones[bn]
        channel, data = state
        bone.bone.use_inherit_rotation = 1
        bone.bone.use_local_location = 1
        bone.bone.use_inherit_scale = 0
        if channel == 'trans':
            for i in range(len(data)):
                d = data[i]
                bone.location = (d[0], d[1], d[2])
                bone.keyframe_insert('location', frame=gLastFrame+i)
        elif channel == 'rot':
            for i in range(len(data)):
                d = data[i]
                bone.rotation_mode = 'QUATERNION'
                (loc, rot, scale) = bone.bone.matrix.to_4x4().decompose()
                rotation = Quaternion((d[3], -d[0], -d[1], -d[2]))
                rotation = rot*rotation
                bone.rotation_quaternion = rotation
                bone.keyframe_insert('rotation_quaternion', frame=gLastFrame+i)
        lastFrame = max(lastFrame, len(data))
    #gLastFrame = lastFrame + gLastFrame

def addAnimations(filename, objName):
    filehandle = open(filename, "rb")
    anims = convert(filehandle)
    filehandle.close()

    amt = bpy.context.scene.objects['_main']
    bpy.context.scene.objects.active = amt
    bpy.ops.object.mode_set(mode='POSE')

    #print(anims.keys())
    #addAnimation(amt, anims[anims.keys()[0]])
    amt.animation_data_create()
    for k, v in anims.items():
        addAnimation(amt, v, k)


def read(filepath):
    #convert the filename to an object name
    objName = bpy.path.display_name_from_filepath(filepath)
    addAnimations(filepath, objName)
