
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
		# Need e * d such that x ** (e * d) % modulus == x

		# Phi is the number of relative primes of modulus.
		# It has the special property that x ** phi % modulus == 1 for any x

		(e,d) = randomDiscreteInversePair(self.__phi)

		#         e * d % phi == 1
		# ====>   e * d == k * phi + 1  for some k

		#         x ** phi           % modulus == 1
		# ====>   x ** (phi * k)     % modulus == 1
		# ====>   x ** (phi * k + 1) % modulus == x
		# ====>   x ** (e * d)       % modulus == x

		return Cipher(self.__modulus,e,d)
	
	def toJson(self,includePrivate : bool = True):
		d = dict()
		d["m"] = self.__modulus
		if includePrivate:
			d["p"] = self.__phi
		return d

def asymmetric(strength : int = 0x100):
	"""
	Returns an asymmetric key generator.

	Asymmetric keys are interlocked key pairs where the original keygen is required
	to calculate one key from the other.

	Thus, they are ideal for public-key private-key cryptography.
	"""
	sa = strength // 2 + 1
	sb = strength // 2 + 2
	p = nextProbablePrime(randomBetween(leastWithBits(sa),leastWithBits(sb)), strength)
	q = nextProbablePrime(randomBetween(leastWithBits(sa),leastWithBits(sb)), strength)

	phi = lcm(p - 1,q - 1)
	return Keygen(p * q, phi)

def commutative(prime : int):
	"""
	Returns a commutative key generator, produced using the specifid prime number.

	Commutative keys are interlocked key pairs where it is easy to calculate
	one key from the other, and thus need to be kept secret.

	Their useful property is their commutativity, such that for any value x, and
	a, b keys produced by the same keygen, the following property holds:
		a.encrypt(b.encrypt(x)) == b.encrypt(a.encrypt(x))
	"""
	return Keygen(prime, prime - 1)
