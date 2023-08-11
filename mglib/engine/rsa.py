
import mglib.engine.padding as padding
import mglib.engine.numbers as numbers

class RSACipher:
	def __init__(self, m, e, d = None):
		self.__modulus : int = m
		self.__public : int = e
		self.__private : int = d
	
	def getModulus(self):
		return self.__modulus
	
	def getSecurity(self):
		return self.__modulus.bit_length()
	
	def powPublic(self, m : int):
		assert 1 < m <= self.__modulus
		return pow(m,self.__public,self.__modulus)

	def powPrivate(self, m : int):
		assert 1 < m <= self.__modulus
		return pow(m,self.__private,self.__modulus)
	
	def encrypt(self, message):
		m = padding.bytesToInt(padding.simplePad(message))
		assert m < self.__modulus, "Message too long!"
		return pow(m,self.__public,self.__modulus)

	def decrypt(self, cipher):
		m = pow(cipher,self.__private,self.__modulus)
		return padding.simpleUnpad(padding.intToBytes(m))

	def toJson(self, includePrivate : bool = True):
		d = dict()
		d["m"] = self.__modulus
		d["e"] = self.__public
		if includePrivate:
			d["d"] = self.__private
		return d

def keygen(strength : int = 0x100):
	p = numbers.nextProbablePrime(numbers.randomBelow(1 << ((strength + 1) // 2)), strength)
	q = numbers.nextProbablePrime(numbers.randomBelow(1 << ((strength + 1) // 2)), strength)

	phi = numbers.lcm(p - 1,q - 1)
	return RSAGenerator(p * q, phi)

def commutative(prime : int):
	return RSAGenerator(prime, prime - 1)

class RSAGenerator:
	def __init__(self, m, p) -> None:
		self.__modulus = m
		self.__phi = p
	
	def keygen(self):
		while True:
			e = numbers.randomBetween(65537, self.__phi - 65537)
			if numbers.gcd(e,self.__phi) == 1:
				break
		
		d = numbers.discreteInverse(e,self.__phi) % self.__phi
		return RSACipher(self.__modulus,e,d)
	
	def toJson(self,includePrivate : bool = True):
		d = dict()
		d["m"] = self.__modulus
		if includePrivate:
			d["p"] = self.__phi
		return d
