
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


    def get_format(self):
        return int(
            (bool(self.positions) and Mesh.HAS_POS) |
            (bool(self.normals) and Mesh.HAS_NORM) |
            (bool(self.color) and Mesh.HAS_COLOR) |
            (bool(self.uv0) and Mesh.HAS_UV0) |
            (bool(self.uv1) and Mesh.HAS_UV1) |
            (bool(self.uv2) and Mesh.HAS_UV2) |
            (bool(self.uv3) and Mesh.HAS_UV3) |
            (bool(self.groups) and Mesh.HAS_BONE_GROUPS)
        )


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


    def to_stream(self, stream):
        stream.wtite_tag_name("NVX1")
        stream.write_uint(len(self.positions))
        stream.write_uint(len(self.indices))
        stream.write_uint(len(self.quads))
        stream.write_uint(self.get_format())
        data_offset = stream.tell() + 4 + 4
        stream.write_uint(data_offset)
        data_size = 0
        data_size_pos = stream.tell()
        stream.write_uint(data_size)

        self._write_vertices(stream)
        self._write_quads(stream)
        self._write_indices(stream)

        data_size = stream.tell() - data_offset
        stream.seek(data_size_pos, 0)
        stream.write_uint(data_size)


    def _read_vertices(self, format, length, stream):
        read_functions = []
        if format & Mesh.HAS_POS:
            self.positions = []
            read_functions.append(lambda: self.positions.append(Vector3(stream=stream)))
        if format & Mesh.HAS_NORM:
            self.normals = []
            read_functions.append(lambda: self.normals.append(Vector3(stream=stream)))
        if format & Mesh.HAS_COLOR:
            self.color = []
            read_functions.append(lambda: self.color.append(Color(stream=stream)))
        if format & Mesh.HAS_UV0:
            self.uv0 = []
            read_functions.append(lambda: self.uv0.append(Vector2(stream=stream)))
        if format & Mesh.HAS_UV1:
            self.uv1 = []
            read_functions.append(lambda: self.uv1.append(Vector2(stream=stream)))
        if format & Mesh.HAS_UV2:
            self.uv2 = []
            read_functions.append(lambda: self.uv2.append(Vector2(stream=stream)))
        if format & Mesh.HAS_UV3:
            self.uv3 = []
            read_functions.append(lambda: self.uv3.append(Vector2(stream=stream)))
        if format & Mesh.HAS_BONE_GROUPS:
            self.groups = []
            read_functions.append(lambda: self.groups.append(BoneGroup(stream=stream)))
        
        for _ in range(length):
            [w() for w in read_functions]


    def _write_vertices(self, stream):
        write_functions = []
        if self.positions:
            write_functions.append(lambda i: self.positions[i].to_stream(stream))
        if self.normals:
            write_functions.append(lambda i: self.normals[i].to_stream(stream))
        if self.color:
            write_functions.append(lambda i: self.color[i].to_stream(stream))
        if self.uv0:
            write_functions.append(lambda i: self.uv0[i].to_stream(stream))
        if self.uv1:
            write_functions.append(lambda i: self.uv1[i].to_stream(stream))
        if self.uv2:
            write_functions.append(lambda i: self.uv2[i].to_stream(stream))
        if self.uv3:
            write_functions.append(lambda i: self.uv3[i].to_stream(stream))
        if self.groups:
            write_functions.append(lambda i: self.groups[i].to_stream(stream))
        for i in range(len(self.positions)):
            [w(i) for w in write_functions]


    def _read_quads(self, winged_edge_count, stream):
        for _ in range(winged_edge_count):
            self.quads.append(Quad(stream=stream))


    def _write_quads(self, stream):
        for quad in self.quads:
            quad.to_stream(stream)


    def _read_indices(self, index_count, stream):
        for _ in range(index_count):
            self.indices.append(stream.read_ushort())


    def _write_indices(self, stream):
        for index in self.indices:
            stream.write_ushort(index)


    def indices_as_triangles(self):
        triangle_count = int(len(self.indices) / 3)
        result = []
        for i in range(triangle_count):
            result.append(tuple(self.indices[i*3:i*3+3]))
        return result


    def groups_as_map(self):
        groups = {}

        def assign(vertex_index, group_index, weight):
            if group_index == -1:
                return
            if not group_index in groups:
                groups[group_index] = []
            groups[group_index].append((vertex_index, weight))

        if self.groups:
            for vertex_index in range(len(self.positions)):
                group = self.groups[vertex_index]
                assign(vertex_index, group.b0 , group.w0)
                assign(vertex_index, group.b1 , group.w1)
                assign(vertex_index, group.b2 , group.w2)
                assign(vertex_index, group.b3 , group.w3)

        return groups
