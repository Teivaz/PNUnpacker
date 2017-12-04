import os, json
from parse_n_tagutils import * 
from parse_n_classes import Classes
from parse_n_globals import GlobalFunctions
from parse_n_analyze import *

USE_DEVELOPEMENT_FOLDER = False
ANALYZE_ONLY = False

if USE_DEVELOPEMENT_FOLDER:
	PATH = "nvx/_main.n"
else:
	PATH = "../islander/islander_old/_data.npk"

def error(s):
	raise NameError(s)
	print(s)

def log(s):
	None
	#print(s)

class FuncDataCollector:
	def __init__(self, classFuncs):
		self.funcs = classFuncs

	def __getitem__(self, funcName):
		if not funcName in self.funcs.keys():
			self.funcs[funcName] = []
		func = self.funcs[funcName]
		def insert(data, size):
			func.append({
				'len': size,
				'probs': data,
			})
		return insert

	def toJSON(self, *args, **kwargs):
		return json.dumps(self.funcs, *args, **kwargs)

class ClassDataCollector:
	def __init__(self):
		self.data = {}

	def __getitem__(self, className):
		if not className in self.data.keys():
			self.data[className] = {}
		return FuncDataCollector(self.data[className])

	def toJSON(self, *args, **kwargs):
		return json.dumps(self.data, *args, **kwargs)

	def keys(self):
		return self.data.keys()

_tags = ClassDataCollector()

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
		self._p = False

	def unknownArgs(self, f):
		if True:
			global _tags
			classData = _tags[self.className]
			funData = classData[self.tag]
			f.read(2)
			argLen = self.size
			funData(estimate(f.read(argLen), argLen), argLen)
			return True, ""
		return False

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
		if self._p:
			print("{}::{}\t{}".format(self.className, self.tag, result))
		if ANALYZE_ONLY:
			log("{}::{}\t{}".format(self.className, self.tag, result))
		else:
			log("{}{}.{}::{}({});".format(depthTab(), self.object, self.className, self.func, result))

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
			log("{}{} {};".format(depthTab()[:-1], name, result))
	else:
		tagSize = peekShortI(f)
		Functions = GlobalFunctions
		(tp, obj) = Stack[-1]
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
				try:
					result = readArgs(f, code)
				except NameError as e:
					raise NameError(str(e) + " At Global `{}::{}({})`".format(tp, name, code))
			else:
				result = ""
			executeFunction(name, result)
		else:
			tagAnalyzer = Tag(tag, "", tp, False, "", obj, tagSize)
			processed, result = tagAnalyzer.unknownArgs(f)
			if not processed:
				name = "#" + name
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
			log("{} {}".format(name, result))
	#log("0x{:0x}: {} {}".format(pos, name, result))

def parse(f, path):
	f.seek(0, 2)
	fileEnd = f.tell()
	f.seek(0, 0)

	if not isValid(f):
		log("File invalid {}".format(path))
		return
		#raise NameError("file invalid: {}".format(path))

	header = readString(f)

	if not ANALYZE_ONLY:
		log(header)

	try:
		while f.tell() != fileEnd:
			readTag(f, parseTag)
	except NameError as e:
		error(str(e) + ' In file `{}`'.format(path))

def convertFile(name):
	f = open(name, "rb")
	try:
		parse(f, name)
	except NameError as e:
		error("Parsing error {}".format(e))
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
	ArgAnalyzer.float(True)
	convertDir(os.path.abspath(PATH))
	#if ANALYZE_ONLY:
	#	printClasses()
	for k in _tags.keys():
		with open('src/{}.json'.format(k), 'w') as fjs:
			fjs.write(_tags[k].toJSON(indent=2))

main()
