import json, os

def bestGuess(argProbs, length):
	pos = 0
	result = ''
	prob = 1.0
	while length > pos:
		argList = argProbs[pos]
		argument = max(argList, key=lambda o: o['p'])
		result += argument['t']
		pos += argument['s']
		prob *= argument['p']
	if result == '':
		return {'a':'v', 'p':1.0}
	return {'a':result, 'p':prob}

def evaluateArgs(argProbs, length):
	result = bestGuess(argProbs, length)
	if not result:
		print('best guess failed')
		return {a:'', p:0}
	return result

def genArgs(funObj):
	lengths = []
	args = []
	for sample in funObj:
		argProbs = sample['probs']
		length = sample['len']
		lengths.append(length)
		args.append(evaluateArgs(argProbs, length))
	lengths = set(lengths)
	shouldHaveString = len(lengths) > 1
	if len(lengths) == 1 and 0 in lengths:
		return 'v'
	#if (len(set(map(lambda x:x['a'], args)))) > 1:
	#	raise NameError('ambiguous call: ' + str(args))
	args = sorted(args, key=lambda x: x['p'])
	return args[0]['a']

def main():
	for root, dirs, files in os.walk('./src'):
		for file in files:
			(tp, ext) = os.path.splitext(file)
			if ext == '.json':
				filename = os.path.join(root, file)
				with open(filename) as jsonData:
					obj = json.loads(jsonData.read())
				print("}},\n'{}': {{".format(tp))
				for fun in obj.keys():
					funObj = obj[fun]
					args = genArgs(funObj)
					print("\t'{}': ('{}', '{}'),".format(fun, args, fun))

if __name__ == '__main__':
	main()
