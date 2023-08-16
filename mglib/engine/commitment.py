
from hashlib import sha256
import base64
import secrets

def combine(a, b):
	if a == None:
		return b
	if b == None:
		return a
	if a == b:
		return a
	if isinstance(a,int):
		assert a == len(b)
		return b
	if isinstance(b,int):
		assert b == len(a)
		return a
	raise Exception("Cannot combine!")

def canonicalize(value):
	if value is None:
		return None
	elif isinstance(value,str):
		return base64.b64decode(value, validate = True)
	elif isinstance(value,bytes) or isinstance(value,int):
		return value
	else:
		raise Exception()

def decanonicalize(value):
	if value is None:
		return None
	elif isinstance(value,bytes):
		return base64.b64encode(value).decode()
	elif isinstance(value,int):
		return value
	else:
		raise Exception()

class Commitment:
	def __init__(self, s = None, p = None) -> None:
		self.__salt = canonicalize(s)
		self.__proof = canonicalize(p)
	
	def __add__(self, that : 'Commitment'):
		return Commitment(
			s = combine(self.__salt,that.__salt),
			p = combine(self.__proof,that.__proof))

	def update(self, s = None, p = None):
		self.__salt = combine(self.__salt,canonicalize(s))
		self.__proof = combine(self.__proof,canonicalize(p))
	
	def verifyHasProof(self):
		assert isinstance(self.__proof,bytes)
	
	def verify(self, value):
		"""
		Tests if this commitment is valid for the given value.
		"""
		assert isinstance(self.__proof,bytes)
		assert isinstance(self.__salt,bytes)
		assert b"\00" not in self.__salt
		h = sha256()
		if isinstance(value,str):
			value = value.encode()
		h.update(value)
		h.update(b"\00")
		h.update(self.__salt)
		assert h.digest() == self.__proof

	def phaseOne(self):
		return self.toJson(includeSalt=False, includeProof=True)

	def phaseTwo(self):
		return self.toJson(includeSalt=True, includeProof=False)
	
	def toJson(self, includeSalt : bool = True, includeProof : bool = True):
		d = dict()
		if includeSalt:
			d["s"] = decanonicalize(self.__salt)
		if includeProof:
			d["p"] = decanonicalize(self.__proof)
		return d

def commit(value, security : int) -> Commitment:
	"""
	Produces a proof of independence from the value. The commitment uniquely identifies the value.

	This is useful if we have a secret value that we eventually want to reveal to a peer,
	but not immediately, and we want to assure them that we do not change the value.

	We can generate the commitment and send it first, and it is possible to later
	verify that the value did not change since the creation of the commitment.
	"""
	h = sha256()
	if isinstance(value,str):
		value = value.encode()
	salt = secrets.token_bytes((security + 7) // 8)
	while b"\00" in salt:
		salt = salt.replace(b"\00",bytes([secrets.randbelow(0x100)]))

	h.update(value)
	h.update(b"\00")
	h.update(salt)
	return Commitment(salt,h.digest())
