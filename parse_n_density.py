import json, math

EXP = 1
TYPE = 'f'
EXCEL = 0

class RangeLinear:
	def __init__(self, step = 1):
		self.step = step

	#def range(self, idx):
	#	return (idx * (self.step-1), (idx * self.step))

	def idx(self, value):
		idx = value / self.step
		idx = math.floor(idx)
		return int(idx)

class RangeExp:
	def __init__(self, step = 1.02):
		self.step = step

	#def range(self, idx):
	#	return (math.exp(self.step, idx-1), math.exp(self.step, idx))

	def idx(self, value):
		idx = math.log(abs(value), self.step)
		#if math.isnan(idx):
		#	raise NameError('Value `{}` produced NaN'.format(value))
		idx = math.floor(idx)
		return int(idx)

class Density:
	def __init__(self, range = RangeLinear(1)):
		self.range = range
		self.data = {}
		self.idxMin = None
		self.idxMax = None
		self.pMax = 0

	def inc(self, idx, count = 1):
		if not idx in self.data.keys():
			self.data[idx] = count
		else:
			c = self.data[idx]
			c += count
			self.data[idx] = c
			self.pMax = max(self.pMax, c)

	def push(self, v):
		if v == 0:
			return
		idx = self.range.idx(v)
		if self.idxMin == None:
			self.idxMin = idx
			self.idxMax = idx
		else:
			self.idxMin = min(self.idxMin, idx)
			self.idxMax = max(self.idxMax, idx)
		self.inc(idx)

	def array(self, a):
		for f in a:
			self.push(f)
		for k in self.data.keys():
			v = float(self.data[k])
			v = v / self.pMax
			self.data[k] = v

	def toJSON(self):
		return json.dumps(self.data)

	def __repr__(self):
		r = []
		for k, v in self.data.iteritems():
			r.append('{}\t{}'.format(k, v))
		return '\n'.join(r)

	def __repr__1(self):
		n = self.idxMax - self.idxMin + 1
		data = []
		for i in range(n):
			idx = self.idxMin + i
			val = 0
			if idx in self.data.keys():
				val = self.data[idx]
			data.append('{}'.format(val))
		return '\n'.join(data)

def main(tp, exp, excel):
	fileNames = {
		'i': 'data/ints.json',
		'f': 'data/floats.json',
	}

	data = []
	with open(fileNames[tp]) as f:
		data = json.loads(f.read())

	range = RangeLinear()
	if exp:
		range = RangeExp()

	d = Density(range)
	d.array(data)

	if excel:
		print(d)
	else:
		name = 'data/density_{}.json'.format(tp)
		with open(name, 'w') as f:
			f.write(d.toJSON())

if __name__ == '__main__':
	main(TYPE, EXP, EXCEL)

def saveDensity(type, exp):
	main(type, exp, False)
