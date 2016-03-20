# Will recursively convert mip 0 to png
# in specified folder

import struct, PIL, os
from PIL import Image


PATH = "_data.npk"
VERBOSITY = 1

def readInt(f):
	(r, ) = struct.unpack("<I", f.read(4))
	return r

FORMAT_B5G6R5 = 3
FORMAT_ALPHA = 4

def checkFormat(f):
	if f == FORMAT_B5G6R5:
		return True
	if f == FORMAT_ALPHA:
		return True
	return False

def readMipHeader(f, Mips):
	Format = readInt(f)

	if not checkFormat(Format):
		raise NameError("Unknown format {0}".format(format))

	Bpp = readInt(f)
	Width = readInt(f)
	Height = readInt(f)
	_c = readInt(f)
	MipLevel = readInt(f)
	Start = readInt(f)
	Size = readInt(f)
	Mip = {}
	Mip["Width"] = Width
	Mip["Height"] = Height
	Mip["Format"] = Format
	Mip["Bpp"] = Bpp
	Mip["MipLevel"] = MipLevel
	Mip["Start"] = Start
	Mip["Size"] = Size
	Mips.append(Mip)

def readMipData(f, mip):
	start = mip["Start"]
	size = mip["Size"]
	f.seek(start)
	format = "<{0}h".format(size/2)
	mip["data"] = struct.unpack(format, f.read(size))

def readBits(short, num, offset):
	if offset > 0:
		short = short >> offset
	mask = 0xffff >> 16-num
	#print short
	result = mask & short
	result = result * (255.0 / float(mask))
	return chr(int(result))

def convertPixel(short, format):
	r = chr(255)
	g = chr(255)
	b = chr(255)
	a = chr(255)
	
	if format == FORMAT_B5G6R5:
		b = readBits(short, 5, 0)
		g = readBits(short, 6, 5)
		r = readBits(short, 5, 11)
	elif format == FORMAT_ALPHA:
		b = readBits(short, 4, 0)
		g = readBits(short, 4, 4) 
		r = readBits(short, 4, 8)
		a = readBits(short, 4, 12) # correct for 04 02

	#print("{0:10} {1} {2} {3} ".format(ord(r), ord(g), ord(b), ord(a)))

	return (r, g, b, a)
	#return (a, b, r, g)

def convertColor(arr, format):
	result = []
	for i in arr:
		(r, g, b, a) = convertPixel(i, format)
		result.extend([r, g, b, a])
	return "".join(result)

def saveMip(mip, fName):
	bytes = convertColor(mip["data"], mip["Format"])
	size = (mip["Width"], mip["Height"])
	image = PIL.Image.frombytes("RGBA", size, bytes).transpose(Image.FLIP_TOP_BOTTOM)
	image.save(fName)

def convert(f):
	footprint = readInt(f)
	if 0x4e545831 != footprint:
		raise NameError("File is not recognized as .NTX")

	Mips = []
	NumMips = readInt(f)
	for i in range(NumMips):
		readMipHeader(f, Mips)

	for i in range(NumMips):
		readMipData(f, Mips[i])

	return Mips

logFile = open("ntx.log", 'a')

def convertFile(name):
	if VERBOSITY > 0:
		print("Converting {0}".format(name))
	f = open(name, "rb")
	try:
		Mips = convert(f)
	except NameError as e:
		error = "Error in file `{0}`:\n\t{1}".format(name, e)
		print(error)
		logFile.write(error + "\n")
		f.close()
		return
	f.close()
	saveMip(Mips[0], name + ".png")


def listDirsAndFiles(path):
	dirs = os.listdir(path)
	dPath = []
	fPath = []
	for d in dirs:
		fullPath = os.path.join(path, d)
		if os.path.isdir(fullPath):
			dPath.append(fullPath)
		elif os.path.splitext(fullPath)[-1] == ".ntx":
			fPath.append(fullPath)
	return dPath, fPath


def convertDir(path):
	dNames, fNames = listDirsAndFiles(path)
	for fName in fNames:
		convertFile(fName)
	for dName in dNames:
		convertDir(dName)

def main():
	convertDir(os.path.abspath(PATH))
	logFile.close()

main()
