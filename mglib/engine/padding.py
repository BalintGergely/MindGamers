
def intToBytes(v : int, least : int = 0):

	assert isinstance(v,int)
	assert isinstance(least,int)
	assert 0 <= v
	
	shift = max(((v.bit_length() - 1) // 8) + 1, least) * 8

	while shift > 0:
		shift = shift - 8
		yield (v >> shift) % 0x100

def bytesToInt(d):

	total = 0

	for b in d:
		assert isinstance(b,int)
		assert 0 <= b <= 0xff
		total = (total << 8) | b
	
	return total

def simplePad(message):
	yield 113
	yield from message

def simpleUnpad(message):
	message = iter(message)
	try:
		while True:
			k = next(message)
			if k == 0:
				continue
			elif k == 113:
				break
			else:
				raise Exception("Inconsistent")
	except StopIteration:
		raise Exception("Inconsistent")
	yield from message
