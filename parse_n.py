import struct, os

USE_DEVELOPEMENT_FOLDER = True
ANALYZE_ONLY = False
TARGET_TAG = "BGCN"

if USE_DEVELOPEMENT_FOLDER:
	PATH = "../nvx/_main.n"
else:
	PATH = "_data.npk"

def peek(f, length=1):
    pos = f.tell()
    data = f.read(length) # Might try/except this line, and finally: f.seek(pos)
    f.seek(pos)
    return data


######################
def isValid(f):
	(footprint, ) = struct.unpack("<I", f.read(4))
	return footprint == 0x4e4f4230 #NOB0
def readShortI(f):
	(size, ) = struct.unpack("<H", f.read(2))
	return size
def peekShortI(f):
	(size, ) = struct.unpack("<h", peek(f,2))
	return size
def readInt(f):
	(value, ) = struct.unpack("<i", f.read(4))
	return "{}".format(value)
def readBool(f):
	(value, ) = struct.unpack("<?", f.read(1))
	return "{}".format(value)

def readFloat(f):
	(value, ) = struct.unpack("<f", f.read(4))
	return "{}".format(value)

def readString(f):
	size = readShortI(f)
	format = "{}s".format(size)
	(string,) = struct.unpack(format, f.read(size))
	return string.decode("utf-8")

def readVoid(f):
	return ""

def readNBytes(f, size):
	format = "{}b".format(size)
	data = struct.unpack(format, f.read(size))
	return "{}".format(data)

def readBytes(f):
	(size, ) = struct.unpack("<h", f.read(2))
	#strSize = peekShortI(f)
	#if strSize+2 == size:
	#	return readString(f)
	format = "{}b".format(size)
	data = struct.unpack(format, f.read(size))
	return "{}".format(data)


Arguments = {
	"s": readString,
	"o": readString,
	"f": readFloat,
	"i": readInt,
	"v": readVoid,
	"b": readBool,
}

######################
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
	return ", ".join(result)


Operators = {
	"_new": (op_new, "new"),
	"_sel": (op_sel, "sel"),
}


Classes = {
	'nchnsplitter': {
		'SKEY': ('ifs', 'setkey'),
		'SRPT': ('s', 'setreptype'),
		'SSCL': ('f', 'setscale'),
		'SCHN': ('s', 'setchannel'),
		'BKEY': ('i', 'beginkeys'),
		'EKEY': ('v', 'endkeys'),

		#'BGKS': ('ii', 'beginkeys'),
		#'ENKS': ('v', 'endkeys'),

		#'SK1F': ('iff', 'setkey1f'),
		#'CNCT': ('s', 'connect'),
	},
	'nmeshnode': {
		'SKEY': ('iffffff', 'setkey'),
		'SFLN': ('s', 'setfilename'),
		'SRDO': ('b', '_SRDO'),
		'SCSD': ('b', '_SCSD'),
	},
	'nparticlesystem': {
		'SLFT': ('f', 'setlifetime'),
		'SFRQ': ('f', 'setfreq'),
		'SSPD': ('f', 'setspeed'),
		'SACC': ('fff', 'setaccel'),
		'SICN': ('f', 'setinnercone'),
		'SOCN': ('f', 'setoutercone'),
		'SSPN': ('f', 'setspin'),
		'SSPA': ('f', 'setspinaccel'),
		#'SSTR' :
		'SEMT': ('s', 'setemmiter'),
	},
	'njointanim': {
		'BGJN': ('i', 'beginjoints'),
		'EDJN': ('v', 'endjoints'),
		'ADJN': ('isifffffff', 'addjoint'),
		'BGST': ('i', 'beginstates'),
		'ADST': ('is', 'addstate'),
		'BGSA': ('ii', 'beginstateanims'),
		'ADSA': ('iis', 'addstateanim'),
		'EDSA': ('i', 'endstateanims'),
		'EDST': ('v', 'endstates'),
		'BGHP': ('i', 'beginhardpoints'),
		'ADHP': ('iis', 'addhardpoint'),
		'EDHP': ('v', 'endhardpoints'),
	},
	'nipol': {
		'SK1F': ('iff', 'setkeys1f'),
		'SK2F': ('ifff', 'setkeys2f'),
		'SK3F': ('iffff', 'setkeys3f'),
		'SK4F': ('ifffff', 'setkeys4f'),
		'SRPT': ('s', 'setreptype'),
		'SCHN': ('s', 'setchannel'),
		'CNCT': ('s', 'connect'),
		'SSCL': ('f', 'setscale'),
		'BGKS': ('ii', 'beginkeys'),
		'ENKS': ('v', 'endkeys'),
		#'SIPT': 
	},
	'nchnmodulator': {
		'BGIN': ('i', 'begin'),
		'SET_': ('iss', 'set'),
		'END_': ('v', 'end'),
	},
	'nhousemenu': {
		'SMRD': ('f', '_SMRD'),
		'STAD': ('f', '_STAD'),
		'SISP': ('f', '_SISP'),
		'SIDS': ('f', '_SIDS'),
	},
	'ncloud': {
		'BCDS': ('if', '_BCDS'),
		'SLNF': ('f', '_SLNF'),
		'ECDS': ('v', 'enableclouds'),
	},
	'nmissileengine3': {
		'SIDL': ('f', '_SIDL'),
		'SGVF': ('f', '_SGVF'),
		'SMXS': ('f', '_SMXS'),
		'SAGL': ('f', '_SAGL'),
	},
	'nmeshcluster2': {
		'SSMS': ('s', '_SSMS'),
		'SCTS': ('b', '_SCTS'),
		'SRTJ': ('s', '_SRTJ'),
		'SRDO': ('b', '_SRDO'),
	},
	'ncurvearraynode': { #nipol
		'BGCN': ('i', 'beginconnects'),
		'EDCN': ('v', 'endconnects'),
		'SCHN': ('s', 'setchannel'),
		'SRPT': ('s', 'setreptype'),
		'SSCL': ('f', 'setscale'),
		'SFLN': ('s', 'setfilename'),
		#EDBD
		#SBC2
		#BGBD
		#BGCB
		#SCBD
		#EBCB
		#SCC2
	},
	'nweighttree': {
		'ANOD': ('sss', 'addnode'),
		'ALEF': ('s', 'addleaf'),
	},
	'ncharacternode': { # njointanim, nchsplitter, nmeshnode
		'EDSA': ('i', 'endstateanims'),
		'BGHP': ('i', 'beginhardpoints'),
		'BGSA': ('ii', 'beginstateanims'),
		'BGJN': ('i', 'beginjoints'),
		'SSKM': ('s', '_SSKM'),
		'SRPT': ('s', 'setreptype'),
		'EDHP': ('v', 'endhardpoints'),
		'ADSA': ('iis', 'addstateanim'),
		'SRDO': ('b', '_SRDO'),
		'EDJN': ('v', 'endjoints'),
		'ADJN': ('isifffffff', 'addjoint'),
		'SCHN': ('s', 'setchannel'),
		'SSCL': ('f', 'setscale'),
		'ADHP': ('iis', 'addhardpoint'),
		'SSTC': ('s', '_SSTC'),
		'EDST': ('v', 'endstates'),
		'SANF': ('s', '_SANF'),
		'BGST': ('i', 'beginstates'),
		'SCSS': ('b', '_SCSS'),
		'ADST': ('is', 'addstate'),
	},
	'nanimsequence': {
		'ADTK': ('ffff', '_ADTK'),
		#ADQK
		#STIT
		#SVRL
		#ADVK
		#ADAK
		#ADRK
	},
	'nmeshemitter': { # nparticlesystem
		'SACC': ('fff', 'setaccel'),
		'SOCN': ('f', 'setoutercone'),
		'SCHN': ('s', 'setchannel'),
		'SRPT': ('s', 'setreptype'),
		'SICN': ('f', 'setinnercone'),
		'SSCL': ('f', 'setscale'),
		'SSPD': ('f', 'setspeed'),
		'STMS': ('fff', '_STMS'),
		'SMSN': ('s', '_SMSN'),
		'SFRQ': ('f', 'setfreq'),
		'SLFT': ('f', 'setlifetime'),
	}
}

GlobalFunctions = {	
	'SRAD': ('f', 'setradius'),
	'STGT': ('o', 'settarget'), #object
	'SXYZ': ('fff', 'sxyz'),
	'TXYZ': ('fff', 'txyz'),
	'STXT': ('iss', 'settexture'), #TODO return bool
	'SFAF': ('f', 'setfinishedafter'),

	'SSHP': ('s', '_SSHP'),
	'SCLC': ('s', '_SCLC'),
	'SDMG': ('b', '_SDMG'),
	'SBNC': ('b', '_SBNC'),
	'SVIS': ('s', '_SVIS'),
	'SAUD': ('s', '_SAUD'),
	'STOU': ('f', '_STOU'),
	'DACC': ('v', '_DACC'),
	'AACC': ('s', '_AACC'),
	'DDEC': ('v', '_DDEC'),
	'SWAC': ('s', '_SWAC'),
	'SFIL': ('s', '_SFIL'),
	'SMMD': ('ff', '_SMMD'),
	'SPRI': ('f', '_SPRI'),
	'SUTR': ('s', '_SUTR'),
	'SSTR': ('b', '_SSTR'),
	'SACT': ('b', '_SACT'),
	'SLOP': ('b', '_SLOP'),
	'SHMA': ('f', '_SHMA'),
	'SHMR': ('f', '_SHMR'),
	'SXEY': ('f', '_SXEY'),
	'SMAS': ('f', '_SMAS'),
	'SVCL': ('s', '_SVCL'),
	'STYP': ('s', '_STYP'),
	'SCLR': ('ffff', '_SCLR'),
	'SSPR': ('b', '_SSPR'),
	'SUCD': ('b', '_SUCD'),
	'SUNM': ('b', '_SUNM'),
	'SUCL': ('b', '_SUCL'),
	'SUV0': ('b', '_SUV0'),
	'SUV1': ('b', '_SUV1'),
	'SUV2': ('b', '_SUV2'),
	'SUV3': ('b', '_SUV3'),
	'SSDM': ('b', '_SSDM'),
	'RXYZ': ('fff', '_RXYZ'),
	'SCSH': ('b', '_SCSH'),
	'M_SH': ('b', '_M_SH'),
	'SRMV': ('b', '_SRMV'),
	'SPSD': ('b', '_SPSD'),
	'STHC': ('b', '_STHC'),
	'SVBL': ('b', '_SVBL'),
	'SAFM': ('b', '_SAFM'),
	'SAFU': ('b', '_SAFU'),
	'SIQS': ('b', '_SIQS'),
	'SFCA': ('b', '_SFCA'),
	'SINS': ('b', '_SINS'),
	'ENEM': ('b', '_ENEM'),
	'SUEP': ('b', '_SUEP'),
	'SSMD': ('b', '_SSMD'),
	'SQSA': ('b', '_SQSA'),
	'STHR': ('b', '_STHR'),
	'CCML': ('v', '_CCML'),
	'SACO': ('f', '_SACO'),
	'SSTB': ('f', '_SSTB'),
	'SUTE': ('s', '_SUTE'),
	'SETF': ('f', 'setfloat'),

	'SAMV': ('b', '_SAMV'),
	'SART': ('b', '_SART'),
	'IGNB': ('b', '_IGNB'),
	'IGNS': ('b', '_IGNS'),
	'IGNF': ('b', '_IGNF'),

	'SPOS': ('fff', '_SPOS'),
	'SDIR': ('fff', '_SDIR'),
	'SEGY': ('f', '_SEGY'),
	'SCTM': ('f', '_SCTM'),
	'RTMD': ('f', '_RTMD'),
	'SPOP': ('i', '_SPOP'),
	'SAUE': ('f', '_SAUE'),
	'SMCG': ('i', '_SMCG'),
	'SCRG': ('i', '_SCRG'),
	'SRTI': ('f', '_SRTI'),
	'SHMC': ('fff', '_SHMC'),
	'SRAC': ('f', '_SRAC'),

	'SATT': ('fff', '?SATT'),
	'SARM': ('si', '?SARM'),
	'SDTP': ('s', '?SDTP'),
	'SDBR': ('s', '?SDBR'),
	'ADBR': ('sfffffff', '?ADBR')
}

Classes_A = {}
Stack = [("", "GLOBAL")]

def executeOperator(name, args):
	if name == "new":
		Stack.append((args[0], args[1]))
	elif name == "sel":
		Stack.pop()

def executeFunction(name, args):
	if len(Stack) == 0:
		Stack.append("GLOBAL")
	c = Stack[-1][0]
	if c not in Classes_A:
		Classes_A[c] = set()
	Classes_A[c].add(name)

def printClasses():
	f = open("classes.txt", "w")
	for pair in Classes_A.iteritems():
		f.write("{}\n".format(pair[0]))
		for m in pair[1]:
			f.write("    {}\n".format(m))
	f.close()

def isOperator(tag):
	return tag in Operators

def parseTag(tag, f):
	name = tag
	result = ""

	pos = f.tell()
	if isOperator(tag):
		(op, name) = Operators[tag]
		opResult = op(f)
		executeOperator(name, opResult)
		result = " ".join(opResult)
		if not ANALYZE_ONLY: 
			print("{} {};".format(name, result))
	else:
		Functions = GlobalFunctions
		(tp, obj) = Stack[-1]
		if tp in Classes:
			Functions = Classes[tp]
		shouldRead = not ANALYZE_ONLY or tag == TARGET_TAG
		if tag in Functions:
			(code, name) = Functions[tag]
			tagSize = readShortI(f)
			if shouldRead: 
				result = readArgs(f, code)
			else:
				result = ""
			executeFunction(name, result)
		elif tag in GlobalFunctions:
			(code, name) = Functions[tag]
			tagSize = readShortI(f)
			if shouldRead: 
				result = readArgs(f, code)
			else:
				result = ""
			executeFunction(name, result)
		else:
			tagSize = peekShortI(f)
			name = "#" + name
			if shouldRead: 
				result = readBytes(f)
			else:
				result = ""
			executeFunction(name, result)
		if shouldRead:
			print("{}.{}({});".format(obj, name, result))
		f.seek(pos + tagSize + 2)

	if ANALYZE_ONLY:
		return


	if False:
		if name[0] == "#" or name[0] == "?":
			print("{} {}".format(name, result))
	#print("0x{:0x}: {} {}".format(pos, name, result))

def readTag(f):
	(tag,) = struct.unpack("4s", f.read(4))
	tag = str(tag[::-1].decode("utf-8"))
	pos = f.tell()
	parseTag(tag, f)
	try:
		None
	except:
		print("exception at {} - {}".format(tag, hex(pos)))

def parse(f, path):
	f.seek(0, 2)
	fileEnd = f.tell()
	f.seek(0, 0)

	(footprint, ) = struct.unpack("<I", f.read(4))
	if footprint != 0x4e4f4230: #NOB0
		if not ANALYZE_ONLY:
			print("file invalid: {}".format(path))
		return

	header = readString(f)

	if not ANALYZE_ONLY:
		print header

	while f.tell() != fileEnd:
		readTag(f)

def convertFile(name):
	f = open(name, "rb")
	try:
		parse(f, name)
	except NameError as e:
		print("Parsing error {}".format(e))
	f.close()

def listDirsAndFiles(path):
	dirs = os.listdir(path)
	dPath = []
	fPath = []
	for d in dirs:
		fullPath = os.path.join(path, d)
		if os.path.isdir(fullPath):
			dPath.append(fullPath)
		elif os.path.splitext(fullPath)[-1] == ".n":
			fPath.append(fullPath)
	return dPath, fPath

def convertDir(path):
	if not os.path.isdir(path):
		convertFile(path)
	else:
		dNames, fNames = listDirsAndFiles(path)
		for fName in fNames:
			convertFile(fName)
		for dName in dNames:
			convertDir(dName)

def main():
	convertDir(os.path.abspath(PATH))
	#if ANALYZE_ONLY:
	#	printClasses()

main()
