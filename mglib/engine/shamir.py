import mglib.engine.numbers as numbers
import mglib.engine.padding as padding
import secrets as secrets
from typing import Iterable

def polynom(modulus : int, coefficents : Iterable[int], x : int):
	"""
	Simple polynom evaluation.
	"""
	k = 1
	v = 0

	for c in coefficents:
		v = (v + k * c) % modulus
		k = (k * x) % modulus

	return v

def lagrange(modulus : int, points : Iterable[(int,int)], x : int):
	"""
	Simple polynom interpolation.
	"""
	if not isinstance(points,tuple | list | set):
		points = set(points)

	k = 0
	for (xn,yn) in points:

		m = yn

		for (xk,yk) in points:
			if xn != xk:
				m = m * (x - xk) % modulus
		
		for (xk,yk) in points:
			if xn != xk:
				m = m * numbers.discreteInverse((xn - xk) % modulus, modulus) % modulus
		
		k = (k + m) % modulus
	
	return k

class Shamir():
	def __init__(self, m : int, t : int) -> None:
		self.__modulus = m
		self.__threshold = t
		pass

	def shatter(self,message : bytes,count : int = ...):
		"""
		Shatters the secret input into the specified number of cryptographic shards.
		"""
		secret = padding.bytesToInt(padding.simplePad(message))
		# Generate random polynom f of order (threshold - 1) such that f(0) = secret.
		coefficents = [secret] + [numbers.randomBelow(self.__modulus) for _ in range(self.__threshold - 1)]

		locations = {0}
		# Evaluate the polynom at many distinct procedurally generated locations.
		while count is ... or len(locations) <= count:
			x = numbers.randomBelow(self.__modulus)
			if x not in locations:
				locations.add(x)
				yield (x,polynom(coefficents,self.__modulus,x))
	
	def recover(self,shards,verify = False):
		"""
		Recover the secret from the shards, and optionally verify their integrity.
		"""
		shards = iter(shards)
		points = set()
		while len(points) < self.__threshold:
			try:
				points.append(next(shards))
			except StopIteration:
				raise Exception("Not enough shards!")
		
		if verify:
			try:
				while True:
					(x,y) = next(shards)
					assert lagrange(self.__modulus, points, x) == y, "Inconsistent!"
			except StopIteration:
				pass
		
		secret = lagrange(self.__modulus, points, 0)
		return padding.simpleUnpad(padding.intToBytes(secret))

	def toJson(self):
		d = dict()
		d["m"] = self.__modulus
		d["t"] = self.__threshold
		return d