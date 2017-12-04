import struct, re

def probInt(val):
	return 0.1 # TODO: estimate how adequate this int is

def probFloat(val):
	return 0.1 # TODO: estimate how adequate this int is

class Probs:
	def __init__(self):
		self.data = []
	def __getitem__(self, i):
		if len(self.data) <= i:
			self.data.insert(i, [])
		def insert(v):
			if v and v[1] > 0:
				self.data[i].append({
					't': v[0],
					'p': v[1],
					'v': v[2],
					's': v[3],
				})
		return insert

def estimateBool(bytes, size):
	(val,) = struct.unpack('b', bytes[0:1])
	if val == 1 or val == 0:
		return ('b', 0.1, val, 1)

def estimateInt(bytes, size):
	if size < 4:
		return
	(val,) = struct.unpack('<i', bytes[0:4])
	prob = probInt(val)
	return ('i', prob, val, 4)

def estimateFloat(bytes, size):
	if size < 4:
		return
	(val,) = struct.unpack('<f', bytes[0:4])
	prob = probFloat(val)
	return ('f', prob, val, 4)

TestString = re.compile(r'^[a-zA-Z0-9/\\_\-\.:]*$')
def estimateString(bytes, size):
	maxProb = 8.0
	if size < 2:
		return
	(strLen,) = struct.unpack('<H', bytes[0:2])
	maxStrLen = size - 2
	if strLen > maxStrLen:
		return
	prob = 1
	if strLen == 0:
		return ('s', prob/maxProb, '', strLen+2)
	if strLen == maxStrLen:
		prob += 2

	estBytes = bytes[2:2+strLen]
	try:
		estString = estBytes.decode('ascii')
	except:
		try:
			val = estBytes.decode('ascii', errors='replace')
			return ('s', prob/maxProb, val, strLen+2)
		except:
			return
	prob += 3
	match = TestString.search(estString)
	if match:
		prob +=2

	return ('s', prob/maxProb, estString, strLen+2)

EstimateFuncs = [
	estimateInt,
	estimateFloat,
	estimateString,
	estimateBool,
]

#(type, prob, value, size)
def estimate(bytes, size):
	probs = Probs()
	for i in range(size):
		add = probs[i]
		byteSlice = bytes[i:]
		for est in EstimateFuncs:
			p = est(byteSlice, size-i)
			add(p)
	return probs.data
