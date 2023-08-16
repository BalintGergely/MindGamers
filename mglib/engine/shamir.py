import mglib.engine.numbers as numbers
import mglib.engine.padding as padding
import secrets as secrets
from typing import Iterable, Tuple

def polynom(modulus : int, coefficents : Iterable[int], x : int):
	"""
	Simple polynom evaluation.

	Needs no explanation.
	"""
	k = 1
	v = 0

	for c in coefficents:
		v = (v + k * c) % modulus
		k = (k * x) % modulus

	return v

def lagrange(modulus : int, points : Iterable[Tuple[int,int]], x : int):
	"""
	Simple polynom interpolation.

	Find a least order polynom that contains all points, and evaluate it at location x.
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

	def __recover(self,shards : Iterable[Tuple[int,int]]):
		shards = iter(shards)
		
		points = dict()
		while len(points) < self.__threshold:
			try:
				(k,v) = next(shards)
				assert (k not in points) or (points[k] == v)
				points[k] = v
			except StopIteration:
				raise Exception("Not enough shards!")
		
		return tuple(points.items())

	def shatter(self,message : int | Iterable[Tuple[int,int]],count : int = ...,verify = True):
		"""
		Shatters the secret input into the specified number of cryptographic shards.

		Alternatively if input is a sufficient collection of shards, makes more shards.
		"""

		if count is ...:
			count = self.__modulus
		
		f = None

		if isinstance(message,int):
			# Generate random polynom f of order (threshold - 1) such that f(0) = secret.
			coefficents = [message] + [numbers.randomBelow(self.__modulus) for _ in range(self.__threshold - 1)]

			f = lambda x: polynom(self.__modulus, coefficents, x)

			locations = {0}
		else:
			points = self.__recover(message)

			f = lambda x: lagrange(self.__modulus, points, x)

			locations = set(k for (k,_) in points)
			try:
				while True:
					(x,y) = next(message)
					assert not verify or f(x) == y, "Inconsistent!"
					locations.add(x)
			except StopIteration:
				pass

		# Evaluate the polynom at many distinct procedurally generated locations.

		while count > 0:
			x = numbers.randomBelow(self.__modulus)
			if x not in locations:
				locations.add(x)
				yield (x,f(x))
				count = count - 1
	
	def getModulus(self):
		return self.__modulus
	
	def recover(self,shards,verify = True):
		"""
		Recover the secret from the shards, and optionally verify their integrity.
		"""
		shards = iter(shards)
		
		points = self.__recover(shards)

		f = lambda x: lagrange(self.__modulus, points, x)

		if verify:
			try:
				while True:
					(x,y) = next(shards)
					assert f(x) == y, "Inconsistent!"
			except StopIteration:
				pass

		return f(0)

	def toJson(self):
		d = dict()
		d["m"] = self.__modulus
		d["t"] = self.__threshold
		return d