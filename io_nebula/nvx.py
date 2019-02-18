
from .types import Vector3, Vector2, Color, Quad, BoneGroup

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
