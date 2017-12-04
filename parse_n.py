import os
from tagutils import * 

USE_DEVELOPEMENT_FOLDER = False
ANALYZE_ONLY = True

if USE_DEVELOPEMENT_FOLDER:
	PATH = "nvx/_main.n"
else:
	PATH = "../islander/islander_old/_data.npk"


######################
class Tag:
	# tag - what we read from file
	# name - fuction name
	# tp - class of the object
	# known - function is in the list of functions
	# code - function arguments
	# obj - the name of the instance
	# tagSize - size of the arguments
	def __init__(self, tag, name, tp, known, code, obj, tagSize):
		self.tag = tag
		self.func = name
		self.className = tp
		self.known = known
		self.args = code
		self.object = obj
		self.size = tagSize

	def shouldRead(self):
		if not ANALYZE_ONLY:
			return True
		#return not self.known
		#return self.tag == "QXYZ"
		#return self.tag == "SATM" and self.className == "nairplane3"
		return self.tag == 'SMPR'

	def submit(self, result):
		if not self.shouldRead():
			return
		if ANALYZE_ONLY:
			print("{}::{}\t{}".format(self.className, self.tag, result))
		else:
			print("{}{}.{}::{}({});".format(depthTab(), self.object, self.className, self.func, result))




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
	for i, c in enumerate(code):
		try:
			v = Arguments[c](f)
		except:
			raise NameError("Failed parsing argument {} of type `{}`".format(i, c))
		result.append(v)
	return ", ".join(result)


Operators = {
	"_new": (op_new, "new"),
	"_sel": (op_sel, "sel"),
}


Classes = {
	'n3dnode': {
		'QXYZ': ('ffff', '_QXYZ'),
		'SBLB': ('b', '_SBLB'),
		'SHDT': ('b', '_SHDT'),
		'SLVW': ('b', '_SLVW'),
		'SMLD': ('f', '_SMLD'),
		'SVWS': ('b', '_SVWS'),
		'RXYZ': ('fff', 'rotate_xyz'),
		'SACT': ('b', '_SACT'),
		'SFAF': ('f', 'setfinishedafter'),
		'SSPR': ('b', '_SSPR'),
		'SXYZ': ('fff', 'scale_xyz'),
		'TXYZ': ('fff', 'translate_xyz'),
	},
	'nflipflop': {
		'SRPT': ('s', 'setreptype'),
		'SCHN': ('s', 'setchannel'),
		'SSCL': ('f', 'setscale'),
		'AKEY': ('fs', 'add_key'),
	},
	'nmeshipol': {
		'SKEY': ('ifs', 'setkey'),
		'BKEY': ('i', 'beginkeys'),
		'EKEY': ('v', 'endkeys'),
		'SCHN': ('s', 'setchannel'),
		'SRDO': ('b', '_SRDO'),
		'SRPT': ('s', 'setreptype'),
		'SSCL': ('f', 'setscale'),
		'SUCD': ('b', '_SUCD'),
		'SUCL': ('b', '_SUCL'),
	},
	'nchnsplitter': {
		'BKEY': ('i', 'beginkeys'),
		'EKEY': ('v', 'endkeys'),
		'SCHN': ('s', 'setchannel'),
		'SKEY': ('ifs', 'setkey'),
		'SRPT': ('s', 'setreptype'),
		'SSCL': ('f', 'setscale'),
	},
	'nlinknode': {
		'STGT': ('o', 'settarget'),
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
		'SIPT': ('s', '_SIPT'),
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
		'EDBD': ('v', '_EDBD'),
		'SBC2': ('iss', '_SBC2'),
		'BGBD': ('is', '_BGBD'),
		'BGCB': ('i', '_BGCB'),
		'SCBD': ('iss', '_SCBD'),
		'EBCB': ('v', '_EBCB'),
		'SCC2': ('iss', '_SCBD'),
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
		'ADQK': ('fffff', '_ADQK'),
		'STIT': ('i', '?STIT'),
		'SVRL': ('b', '_SVRL'),
		'ADVK': ('fs', '_ADVK'),
		'ADAK': ('fs', '_ADAK'),
		'ADRK': ('ffff', '_ADRK'),
	},
	'ntrailrender': {
		'SKEY': ('iffffff', 'setkey'),
		'BKEY': ('i', 'beginkeys'),
		'EKEY': ('v', 'endkeys'),
		'SCHN': ('s', 'setchannel'),
		'SEMT': ('s', 'setemmiter'),
		'SRPT': ('s', 'setreptype'),
		'SSCL': ('f', 'setscale'),
		'SSPA': ('f', 'setspinaccel'),
		'SSPN': ('f', 'setspin'),
		'SSTR': ('b', '_SSTR'),
	},
	'nspriterender': {
		'SRPT': ('s', 'setreptype'),
		'SCHN': ('s', 'setchannel'),
		'SSCL': ('f', 'setscale'),
		'SSPN': ('f', 'setspin'),
		'SSPA': ('f', 'setspinaccel'),
		'SEMT': ('s', 'setemmiter'),
		'BKEY': ('i', 'beginkeys'),
		'SKEY': ('iffffff', 'setkey'),
		'EKEY': ('v', 'endkeys'),
		'SSTR': ('b', '_SSTR'),
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
	},
	'nshadernode': {
		'SMMF': ('s', 'set_min_max_filter'),
		'SEMV': ('fff', '_SEMV'),
		'SPOP': ('i', '_SPOP'),
		'SADR': ('s', 'set_ADR'),
		'SABL': ('s', 'set_alpha_blending'),
		'SZFC': ('s', 'set_ZFC'),
		'SCMD': ('s', 'set_CMD'),
		'SCLM': ('s', 'set_CLM'),
		'SAFC': ('s', 'set_AFC'),
		'SAOP': ('is', 'set_AOP'),
		'SDIF': ('ffff', 'set_diffuse_color'),
		'SAMB': ('ffff', 'set_ambient_color'),
		'SCOT': ('iiiii', '_SCOT'),
		'SLEN': ('b', 'set_LEN'),
		'SAEN': ('b', 'set_AEN'),
		'SZEN': ('b', 'set_ZEN'),
		'SFEN': ('b', 'set_FEN'),
		'SATE': ('b', 'set_ATE'),
		'SENT': ('b', '_SENT'),
		'SMLB': ('i', '_SMLB'),
		'SNST': ('i', '_SNST'),
		'BGTU': ('i', '_BGTU'),
		'SARF': ('f', '_SARF'),
		'SRPR': ('i', '_SRPR'),
		'EDTU': ('v', 'enable_DTU'),
		'STCS': ('s', 'set_TCS'),
		'TXYZ': ('fff', 'translate_xyz'),
		'RXYZ': ('fff', 'rotate_xyz'),
		'SXYZ': ('fff', 'scale_xyz'),
	},
	'nairplane3': {
		'SATM': ('f', '_SATM'),
		'SDTM': ('f', '_SDTM'),
		'SISP': ('f', '_SISP'),
		'SMPI': ('f', '_SMPI'),	
		'SMPT': ('f', '_SMPT'),
		'SMRL': ('f', '_SMRL'),
		'SMRT': ('f', '_SMRT'),
		'SXSP': ('f', '_SXSP'),
		'SXYR': ('f', '_SXYR'),
		'SYAT': ('f', '_SYAT'),
	},
	'nbuildartefact': {
		'SBEN': ('f', '_SBEN'),
		'SBPR': ('s', '_SBPR'),
		'SBTM': ('f', '_SBTM'),
		'SBRP': ('iff', '?SBRP'),
		'SMPR': ('i', '_SMPR'),
		'SSID': ('i', '_SSID'),
	},
	######################################

		#'BGKS': ('ii', 'beginkeys'),
		#'ENKS': ('v', 'endkeys'),

		#'SK1F': ('iff', 'setkey1f'),
		#'CNCT': ('s', 'connect'),
	'nairship3':{},
	'nartefactstorage':{},
	'nartefacttransformer':{},
	'nattack':{},
	'navoidcollision':{},
	'nbombard':{},
	'nbomber':{},
	'nbuildflak':{},
	'nbuildtradeartefact':{},
	'nbuildvehicle':{},
	'ncharaudio':{},
	'nchnreader':{},
	'ncinedummy':{},
	'nclouddesc':{},
	'ncloudrender':{},
	'nclouds':{},
	'ncollectartefact':{},
	'ncollectore':{},
	'ncollhandle2':{},
	'nconsumption':{},
	'ncontainer':{},
	'ncritter2':{},
	'ncrittercollhandle':{},
	'ncritterdamage':{},
	'ncritterengine2':{},
	'nenergycollector':{},
	'nexplosion':{},
	'nfactory':{},
	'nfiremachinegun':{},
	'nfiremissile':{},
	'nflak':{},
	'nflakengine2':{},
	'nfognode':{},
	'nfreesteer':{},
	'ngarage':{},
	'ngrassrender':{},
	'nheal':{},
	'nhouse':{},
	'nhypermixer2':{},
	'nipolapproachgarage':{},
	'nislanddrive':{},
	'njoint2':{},
	'nleafrender':{},
	'nlenseflare':{},
	'nlightnode':{},
	'nlistenernode':{},
	'nmaennel':{},
	'nmaennelengine3':{},
	'nmaennelwalk2':{},
	'nmeshipol':{},
	'nmeshmixer':{},
	'nmeshsway':{},
	'nmgrender':{},
	'nmissile':{},
	'nmissilecollcheck':{},
	'nmissileengine2':{},
	'nmixer':{},
	'nmnlcollhandle2':{},
	'nmodartefact':{},
	'nnavpoint':{},
	'nnavpointsteer':{},
	'nore':{},
	'npawnshop':{},
	'nplacehouse':{},
	'nplacespellaction':{},
	'npointemitter':{},
	'npowersupply':{},
	'nreplenish':{},
	'nsammler':{},
	'nshadowcontrol':{},
	'nsilo':{},
	'nsoundnode':{},
	'nspawnpoint':{},
	'nsquadronwatchtarget':{},
	'nstandardmenu':{},
	'nstatewatch':{},
	'nstaticmeshemitter':{},
	'nstation':{},
	'nstationengine3':{},
	'nstoragemenu':{},
	'nsubtitle':{},
	'nswimmingengine':{},
	'nswingengine':{},
	'ntestpossess':{},
	'ntexarraynode':{},
	'nthreshnode':{},
	'ntrademenu':{},
	'ntransformmenu':{},
	'ntriggerobject':{},
	'nunloadore':{},
	'nvehicle':{},
	'nvehicleemitter':{},
	'nviewerdata':{},
	'nvisual':{},
	'nwalkcollhandle2':{},
	'nwatchtarget':{},
	'nweatherdesc':{},

}

GlobalFunctions = {
	'SBEN': ('f', '_SBEN'),
	'SBPR': ('s', '_SBPR'),
	'SBTM': ('f', '_SBTM'),
	'SBRP': ('iff', '?SBRP'),
	'SMPR': ('i', '_SMPR'),

	'SRAD': ('f', 'setradius'),
	'STGT': ('o', 'settarget'), #object
	'SXYZ': ('fff', 'sxyz'),
	'TXYZ': ('fff', 'txyz'),
	'STXT': ('iss', 'settexture'), #TODO return bool
	'SFAF': ('f', 'setfinishedafter'),

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
			f.write("\t{}\n".format(m))
	f.close()

def isOperator(tag):
	return tag in Operators

def depthTab():
	if ANALYZE_ONLY:
		return ""
	else:
		return "\t" * (len(Stack) - 1)

def parseTag(tag, f):
	name = tag
	result = ""

	pos = f.tell()
	if isOperator(tag):
		(op, name) = Operators[tag]
		try:
			opResult = op(f)
		except NameError as e:
			raise NameError(str(e) + " Op `{}`".format(name))
		executeOperator(name, opResult)
		result = " ".join(opResult)
		if not ANALYZE_ONLY: 
			print("{}{} {};".format(depthTab()[:-1], name, result))
	else:
		Functions = GlobalFunctions
		(tp, obj) = Stack[-1]
		tailPrinter = None
		if tp in Classes:
			Functions = Classes[tp]
		if tag in Functions:
			(code, name) = Functions[tag]
			tagSize = readShortI(f)
			tagAnalyzer = Tag(tag, name, tp, True, code, obj, tagSize)
			if tagAnalyzer.shouldRead():
				try:
					result = readArgs(f, code)
				except NameError as e:
					raise NameError(str(e) + " At `{}::{}({})`".format(tp, name, code))
			else:
				result = ""
			executeFunction(name, result)
		elif tag in GlobalFunctions:
			(code, name) = GlobalFunctions[tag]
			tagSize = readShortI(f)
			tagAnalyzer = Tag(tag, name, tp, False, code, obj, tagSize)
			if tagAnalyzer.shouldRead(): 
				result = readArgs(f, code)
			else:
				result = ""
			executeFunction(name, result)
		else:
			tagSize = peekShortI(f)
			name = "#" + name
			tagAnalyzer = Tag(tag, "", tp, False, "", obj, tagSize)
			if tagAnalyzer.shouldRead(): 
				result = readBytes(f)
			else:
				result = ""
			executeFunction(name, result)
		tagAnalyzer.submit(result)
		f.seek(pos + tagSize + 2)

	if ANALYZE_ONLY:
		return


	if False:
		if name[0] == "#" or name[0] == "?":
			print("{} {}".format(name, result))
	#print("0x{:0x}: {} {}".format(pos, name, result))

def parse(f, path):
	f.seek(0, 2)
	fileEnd = f.tell()
	f.seek(0, 0)

	if not isValid(f):
		raise NameError("file invalid: {}".format(path))

	header = readString(f)

	if not ANALYZE_ONLY:
		print(header)

	try:
		while f.tell() != fileEnd:
			readTag(f, parseTag)
	except NameError as e:
		print(str(e) + ' In file `{}`'.format(path))

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
