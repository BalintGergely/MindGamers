import mglib.engine.numbers as numbers
import mglib.engine.padding as padding
import secrets as secrets
from typing import Iterable, Tuple, List

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

	Find a least order polynom that contains all points in the iterable, and evaluate it at location x.
	"""
	if not isinstance(points,tuple | list | set):
		points = set(points)
	
	# The interpolated polynom can be thought of as a sum of "Lagrange Polynoms".
	# Each Lagrange Polynom f has the property that f(x) = y for one (x,y) pair,
	# while f(x) = 0 for any other (x,y) pair in the set of points.
	# Find the Lagrange Polynom for all points in the set, and sum the values.

	k = 0
	for (xn,yn) in points:

		m = yn # Need f(xn) == yn so we start with it.

		for (xk,yk) in points:
			if xn != xk:
				# Need f(xk) == 0, so we multiply by (x - xk)
				m = m * (x - xk) % modulus
				# This will multiply f(xn) by (xn - xk) so we divide the
				# whole function by that value to restore the original f(xn) == yn
				# We do not ever divide by zero because of the xn != xk check.
				m = m * numbers.discreteInverse((xn - xk) / modulus,modulus) % modulus
				m = m % modulus
		
		k = (k + m) % modulus
	
	return k

class Shamir():
	"""
	The Shamir system is a way to break down a secret value into many shards, such that any specified number
	of shards are capable of reconstructing the secret.

	The system works using polynom interpolation. Say we would like to "shatter" the secret m
	into shards such that 'n' shards are possible to reconstruct the secret.

	We generate a random polynom f of order n-1 such that f(0) == m. Then we evaluate the polynom at random
	points generating (x,y) shards that are location pairs. (x,y) = (x,f(x))

	To reconstruct the secret, you take any n shards, and perform a polynom interpolation
	over them, which results in the original random polynom. Then you simply evaluate it at f(0) to recover the secret.
	"""
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