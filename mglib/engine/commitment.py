
from hashlib import sha256
import base64
import secrets

def ensureEqual(a, b):
	if a == None:
		return b
	if b == None:
		return a
	assert a == b, "Inconsistent!"
	return a

def maybeToBytes(value):
	if value is None:
		return None
	elif isinstance(value,str):
		return base64.b64decode(value, validate = True)
	elif isinstance(value,bytes):
		return value
	else:
		raise Exception("Bytes or b64 encoded bytes expected!")

class Commitment:
	def __init__(self, s, p) -> None:
		self.__salt = maybeToBytes(s)
		self.__proof = maybeToBytes(p)
	
	def __add__(self, that : 'Commitment'):
		return Commitment(
			s = ensureEqual(self.__salt,that.__salt),
			p = ensureEqual(self.__proof,that.__proof))
	
	def getProof(self) -> bytes:
		return self.__proof
	
	def getSalt(self) -> bytes:
		return self.__salt

	def verify(self, value):
		"""
		Returns True if verification succeeds. False otherwise.
		"""
		assert self.__proof is not None
		assert self.__salt is not None, "Needs salt!"
		h = sha256()
		if isinstance(value,str):
			h.update(value.encode())
		elif isinstance(value,bytes):
			h.update(value)
		else:
			raise Exception("Needs a value!")
		h.update(self.__salt)
		return h.digest() == self.__proof
	
	def toJson(self, includeSalt : bool = False):
		d = dict()
		if includeSalt:
			d["s"] = base64.b64encode(self.__salt).decode()
		d["p"] = base64.b64encode(self.__proof).decode()
		return d

def commit(value : str) -> Commitment:
	h = sha256()
	h.update(value.encode())
	salt = secrets.token_bytes(16)
	h.update(salt)
	return Commitment(salt,h.digest())
