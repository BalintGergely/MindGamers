
import secrets

def randomBelow(limit : int):
	"""
	A random integer between 0 (inclusive) and the limit (exclusive).
	"""
	bl = limit.bit_length()
	if bl > 60:
		while True:
			k = secrets.randbits(bl)
			if k < limit:
				return k
	return secrets.randbelow(limit)

def randomBetween(startInclusive : int,endExclusive : int):
	"""
	A random integer between the two arguments.
	"""
	return randomBelow(endExclusive - startInclusive) + startInclusive

def millerRabin(p: int,passes = 1):
	"""
	Performs the specified number of random Miller Rabin tests on p.
	If p fails a test, the witness value for that test is returned.
	If p passes all tests, None is returned.

	Prime numbers always pass all tests. All composite numbers have a chance to fail a test.
	The more tests the better, but take longer.
	"""
	k = p - 1
	d = k
	s = 0

	while (d & 1) == 0:
		d = d >> 1
		s = s + 1
	
	for _ in range(passes):
		a = randomBetween(2,p)
		
		z = pow(a,d,p)

		if z == 1:
			continue

		r = 0

		while z != k:
			r = r + 1
			if r == s:
				return a
			z = pow(z,2,p)

	return None

def verifyMillerRabin(p : int, witness: int):
	"""
	Verifies that p is composite according to the witness value.
	Returns True if the verification succeeds. False otherwise.
	"""
	if not (2 <= witness < p):
		return False

	k = p - 1
	d = k
	s = 0

	while (d & 1) == 0:
		d = d >> 1
		s = s + 1
	
	a = witness
	
	z = pow(a,d,p)

	if z == 1:
		return False

	r = 0

	while z != k:
		r = r + 1
		if r == s:
			return True
		z = pow(z,2,p)
	
	return False

def isProbablePrime(v : int, passes : int):
	"""
	Returns True if the first argument is probably a prime, False if it is definitely composite.

	Higher number of passes results in fewer false positives, but longer runtime.
	"""
	# Trivial case
	if v < 2:
		return False
	
	# 2 is a prime
	if v == 2:
		return True
	
	# An important check
	if (v & 1 == 0):
		return False
	
	# For numbers below 100000 just check for divisors.
	if v < 100000:
		return (v & 1 == 1) and all(v % t != 0 for t in range(3,v,2))
	
	# Otherwise perform the specified number of Miller Rabin tests.
	return millerRabin(v, passes) == None

def nextProbablePrime(v : int, p : int):
	v = v + 1

	if v == 2:
		return v

	if (v & 1) == 0:
		v = v + 1

	while not isProbablePrime(v,p):
		v = v + 2
	
	return v

def gcd(a : int, b : int):
	"""
	Greatest Common Divisor
	"""
	while True:
		if a == 0:
			return b
		c = b % a
		b = a
		a = c

def lcm(a : int, b : int):
	"""
	Least Common Multiple
	"""
	return a * b // gcd(a,b)

def discreteInverse(r0,r1):
	"""
	Discrete inverse of r0 modulo r1.
	"""
	s0 = 1
	s1 = 0
	while r1 != 0:

		s2 = s0 - (r0 // r1) * s1
		s0 = s1
		s1 = s2

		r2 = r0 % r1
		r0 = r1
		r1 = r2
	
	if r0 == 1:
		return s0
	else:
		return None

