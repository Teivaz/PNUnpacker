
class Vector3:
    def __init__(self, x=0, y=0, z=0, stream=None):
        self.x = x
        self.y = y
        self.z = z
        if stream:
            self.from_stream(stream)

    def data(self):
        return (self.x, self.y, self.z)

    def __iter__(self):
        return iter(self.data())

    def from_stream(self, stream):
        self.x = stream.read_float()
        self.y = stream.read_float()
        self.z = stream.read_float()

    def to_stream(self, stream):
        stream.write_float(self.x)
        stream.write_float(self.y)
        stream.write_float(self.z)

class Vector2:
    def __init__(self, x=0, y=0, stream=None):
        self.x = x
        self.y = y
        if stream:
            self.from_stream(stream)

    def data(self):
        return (self.x, self.y)

    def __iter__(self):
        return iter(self.data())

    def from_stream(self, stream):
        self.x = stream.read_float()
        self.y = stream.read_float()

    def to_stream(self, stream):
        stream.write_float(self.x)
        stream.write_float(self.y)

class Color:
    def __init__(self, r=0, g=0, b=0, a=0, stream=None):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        if stream:
            self.from_stream(stream)

    def __iter__(self):
        return iter((self.r, self.g, self.b, self.a))

    def from_stream(self, stream):
        self.r = stream.read_byte()
        self.g = stream.read_byte()
        self.b = stream.read_byte()
        self.a = stream.read_byte()

    def to_stream(self, stream):
        stream.write_byte(self.r)
        stream.write_byte(self.g)
        stream.write_byte(self.b)
        stream.write_byte(self.a)

class Quad:
    def __init__(self, a=0, b=0, c=0, d=0, stream=None):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        if stream:
            self.from_stream(stream)

    def __iter__(self):
        return iter((self.a, self.b, self.c, self.d))

    def from_stream(self, stream):
        self.a = stream.read_ushort()
        self.b = stream.read_ushort()
        self.c = stream.read_ushort()
        self.d = stream.read_ushort()

    def to_stream(self, stream):
        stream.write_ushort(self.a)
        stream.write_ushort(self.b)
        stream.write_ushort(self.c)
        stream.write_ushort(self.d)

class BoneGroup:
    def __init__(self, b0=0, b1=0, b2=0, b3=0, w0=0, w1=0, w2=0, w3=0, stream=None):
        self.b0 = b0
        self.b1 = b1
        self.b2 = b2
        self.b3 = b3
        self.w0 = w0
        self.w1 = w1
        self.w2 = w2
        self.w3 = w3
        if stream:
            self.from_stream(stream)

    def from_stream(self, stream):
        self.b0 = stream.read_ushort()
        self.b1 = stream.read_ushort()
        self.b2 = stream.read_ushort()
        self.b3 = stream.read_ushort()
        self.w0 = stream.read_float()
        self.w1 = stream.read_float()
        self.w2 = stream.read_float()
        self.w3 = stream.read_float()

    def to_stream(self, stream):
        stream.write_ushort(self.b0)
        stream.write_ushort(self.b1)
        stream.write_ushort(self.b2)
        stream.write_ushort(self.b3)
        stream.write_float(self.w0)
        stream.write_float(self.w1)
        stream.write_float(self.w2)
        stream.write_float(self.w3)
