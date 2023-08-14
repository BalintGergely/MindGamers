
from mglib.engine.numbers import *
import mglib.engine.utils as utils
from mglib.network.peer import Peer
import mglib.network.basic as basic
from mglib.engine.commitment import Commitment, commit

from typing import Iterable, List

def sharedRandom(peer : Peer, limits : int | Iterable[int], security):
	"""
	Generate one or more random integers, cooperating with the specified peer.

	Both participants will learn the result, and both participants will be assured that it is random.
	"""
	returnAsInt = isinstance(limits,int)
	if returnAsInt:
		limits = [limits]
	basic.agreeOn(peer,"Shared Random Batch",limits)
	myResults = tuple(randomBelow(d) for d in limits)
	mySign = " ".join(hex(r) for r in myResults)

	myC = commit(mySign, security)
	peer.send(myC.toJson(includeSalt=False,includeProof=True))
	peerC = Commitment(**peer.recv(dict))
	peerC.verifyHasProof()
	peer.send(myResults)
	peerResults = peer.recv([range(k) for k in limits])
	assert len(peerResults) == len(limits)
	peer.send(myC.toJson(includeSalt=True,includeProof=False))
	peerSign = " ".join(hex(r) for r in peerResults)
	peerC.update(**peer.recv(dict))
	peerC.verify(peerSign)

	result = tuple((myR + peerR) % limit for (myR,peerR,limit) in zip(myResults,peerResults,limits))
	
	if returnAsInt:
		return result[0]
	else:
		return result

def sharedRandomProbablePrime(peer : Peer, security : int):
	"""
	Generate a random probable big prime number, cooperating with the specified peer.

	Both participants will learn the result, and both participants will be assured that it is random.
	"""
	basic.agreeOn(peer,"Shared Random Probable Prime")
	peer.send(security)
	peerSecurity = peer.recv(int)
	maxSecurity = max(security,peerSecurity)

	assert 8 <= maxSecurity

	number = sharedRandom(peer,leastWithBits(maxSecurity),security) | 1 << maxSecurity | 0x1

	backlog = 0

	while True:
		# Cooperative testing with proofs.
		# We use the first value where neither party can prove compositeness.
		witness = millerRabin(number, security * 2)
		peer.send(witness)
		if witness is None:
			for _ in range(backlog):
				peer.recv(int | None)
			backlog = 0
			peerWitness = peer.recv(int | None)
			if peerWitness is None:
				return number
			assert testCompositeWitness(number, peerWitness)
		else:
			# We know the number is composite. Instead of waiting for the peer's message,
			# we "remember" we have unread messages.
			backlog = backlog + 1
		number = number + 2

def sharedFisherYates(peer : Peer, elementCount, security : int):
	return sharedRandom(peer, range(2,elementCount + 1), security)

def sharedPermutation(peer : Peer, elements : List, security : int):
	count = len(elements)
	utils.performSwaps(zip(range(1,count),sharedFisherYates(peer, count, security)))