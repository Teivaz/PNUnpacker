
import ctypes, struct, PIL
from PIL import Image

class Format_A4R4G4B4(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = (("b", ctypes.c_ubyte, 4),
                ("g", ctypes.c_ubyte, 4),
                ("r", ctypes.c_ubyte, 4),
                ("a", ctypes.c_ubyte, 4))

    def rgba(self):
        # Normalize from compressed values to full byte
        b = int(self.b * 255 / 15)
        g = int(self.g * 255 / 15)
        r = int(self.r * 255 / 15)
        a = int(self.a * 255 / 15)
        return struct.pack("BBBB", r, g, b, a)

    @staticmethod
    def sizeof():
        return ctypes.sizeof(Format_A4R4G4B4)

'''
# Seriously? https://bugs.python.org/issue29753
class Format_R5G6B5(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = (("b", ctypes.c_ubyte, 5),
                ("g", ctypes.c_ubyte, 6),
                ("r", ctypes.c_ubyte, 5))

    @staticmethod
    def sizeof():
        return ctypes.sizeof(Format_R5G6B5)
'''

class Format_R5G6B5:
    def __init__(self, b, g, r):
        self.b = b
        self.g = g
        self.r = r

    def rgba(self):
        # Normalize from compressed values to full byte
        b = int(self.b * 255 / 31)
        g = int(self.g * 255 / 63)
        r = int(self.r * 255 / 31)
        return struct.pack("BBBB", r, g, b, 255)

    @staticmethod
    def from_buffer_copy(source):
        raw, = struct.unpack("<H", source)
        b = (raw & 0b0000000000011111) >> 0
        g = (raw & 0b0000011111100000) >> 5
        r = (raw & 0b1111100000000000) >> 11
        return Format_R5G6B5(b, g, r)

    @staticmethod
    def sizeof():
        return 2


class NtxFormat:
    #X8R8G8B8 = 1
    #A8R8G8B8 = 2
    R5G6B5 = 3
    #A1R5G5B5
    A4R4G4B4 = 4
    #P8
    #G16R16
    #DXT1

    @staticmethod
    def validate_format(format):
        if format == NtxFormat.R5G6B5:
            return True
        if format == NtxFormat.A4R4G4B4:
            return True
        return False

    @staticmethod
    def pixel_reader(format):
        if format == NtxFormat.R5G6B5:
            return Format_R5G6B5
        if format == NtxFormat.A4R4G4B4:
            return Format_A4R4G4B4
        return None


class MipHeader:
    def __init__(self, stream=None):
        self.format = 0
        self.bpp = 0
        self.width = 0
        self.height = 0
        self.level = 0
        self.start_offset = 0
        self.size = 0

        if stream:
            self.from_stream(stream)

    def from_stream(self, stream):
        self.format = stream.read_uint()
        if not NtxFormat.validate_format(self.format):
            raise NameError("Unknown texture format {0}".format(self.format))
        self.bpp = stream.read_uint()
        self.width = stream.read_uint()
        self.height = stream.read_uint()
        _ = stream.read_uint()
        self.level = stream.read_uint()
        self.start_offset = stream.read_uint()
        self.size = stream.read_uint()

    def to_stream(self, stream):
        stream.write_uint(self.format)
        stream.write_uint(self.bpp)
        stream.write_uint(self.width)
        stream.write_uint(self.height)
        stream.write_uint(0)
        stream.write_uint(self.level)
        stream.write_uint(self.start_offset)
        stream.write_uint(self.size)


class MipData:
    def __init__(self, stream=None, header=None):
        self.image = None
        if stream:
            self.from_stream(stream, header)

    def from_stream(self, stream, header):
        with stream.push() as s:
            s.seek(header.start_offset)
            pixel_reader = NtxFormat.pixel_reader(header.format)
            pixels = bytearray()
            pixel_size = pixel_reader.sizeof()
            pixel_count = int(header.size / pixel_size)

            for _ in range(pixel_count):
                raw = s.read(pixel_size)
                pixel = pixel_reader.from_buffer_copy(raw)
                pixels += pixel.rgba()
        image_size = (header.width, header.height)
        self.image = PIL.Image.frombytes("RGBA", image_size, bytes(pixels)).transpose(Image.FLIP_TOP_BOTTOM)

    def save_to_file(self, path):
        self.image.save(path)

    def to_stream(self, stream):
        pass

class Texture:
    def __init__(self, stream=None):
        self.mips = []

        if stream:
            self.from_stream(stream)
    
    def from_stream(self, stream):
        if "NTX1" != stream.read_tag_name():
            raise NameError("File is not recognized as .NTX")
        
        mip_count = stream.read_uint()
        mip_headers = []

        for _ in range(mip_count):
            mip_headers.append(MipHeader(stream=stream))
        
        for mip_header in mip_headers:
            self.mips.append(MipData(stream=stream, header=mip_header))
