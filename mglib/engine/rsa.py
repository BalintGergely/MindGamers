
import mglib.engine.padding as padding
from mglib.engine.numbers import *

class Cipher:
	def __init__(self, m, e, d = None):
		self.__modulus : int = m
		self.__public : int = e
		self.__private : int = d
	
	def getModulus(self):
		return self.__modulus
	
	def getSecurity(self):
		return self.__modulus.bit_length()
	
	def encrypt(self, m):
		return pow(m,self.__public,self.__modulus)

	def decrypt(self, c):
		return pow(c,self.__private,self.__modulus)

	def toJson(self, includePrivate : bool = True):
		d = dict()
		d["m"] = self.__modulus
		d["e"] = self.__public
		if includePrivate:
			d["d"] = self.__private
		return d

class Keygen:
	def __init__(self, m, p) -> None:
		self.__modulus = m
		self.__phi = p
	
	def keygen(self):
		(e,d) = randomDiscreteInversePair(self.__phi)
		return Cipher(self.__modulus,e,d)
	
	def toJson(self,includePrivate : bool = True):
		d = dict()
		d["m"] = self.__modulus
		if includePrivate:
			d["p"] = self.__phi
		return d

def asymmetric(strength : int = 0x100):
	sa = strength // 2 + 1
	sb = strength // 2 + 2
	p = nextProbablePrime(randomBetween(leastWithBits(sa),leastWithBits(sb)), strength)
	q = nextProbablePrime(randomBetween(leastWithBits(sa),leastWithBits(sb)), strength)

	phi = lcm(p - 1,q - 1)
	return Keygen(p * q, phi)

def commutative(prime : int):
	return Keygen(prime, prime - 1)
