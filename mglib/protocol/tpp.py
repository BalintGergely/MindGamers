
import mglib.network.basic as basic
import mglib.engine.exponents as exponents
import mglib.engine.numbers as numbers
import mglib.engine.utils as utils
import mglib.protocol.random as random
from mglib.network.peer import Peer
from hashlib import sha256
from typing import List, Set

def obliviousSend(peer : Peer, messages : List[int], sendCount : int, security) -> None:
	"""
	Send the peer a subset of the messages.

	The receiver can privately decide which messages it will get.

	The sender will not learn any information whatsoever.
	"""
	passCount = sendCount
	basic.agreeOn(peer,"Oblivious Transfer",len(messages),passCount,basic.sender())
	cipher : exponents.Cipher = exponents.asymmetric(security).keygen()
	modulus = cipher.getModulus()
	blinds = [numbers.randomBelow(modulus) for _ in messages]

	peer.send(cipher.toJson(includePrivate = False))
	peer.send(blinds)

	vs = peer.recv([range(modulus)] * passCount)

	peer.send([[(m + cipher.decrypt((v - x) % modulus)) % modulus for (m,x) in zip(messages,blinds)] for v in vs])

def obliviousReceive(peer : Peer, messageCount : int, wantedMessages : Set[int] | int, security : int = 0) -> int:
	"""
	Receive a subset of a total number of messages from the peer.

	The receiver can privately decide which messages it will get.

	The sender will not learn any information whatsoever.
	"""
	returnAsInt = False
	if isinstance(wantedMessages,int):
		wantedMessages = [wantedMessages]
		returnAsInt = True
	else:
		wantedMessages = list(wantedMessages)
	passCount = len(wantedMessages)
	basic.agreeOn(peer, "Oblivious Transfer", messageCount, passCount, basic.receiver())

	cipher = exponents.Cipher(**peer.recv(dict))
	modulus = cipher.getModulus()
	blinds = peer.recv([range(modulus)] * messageCount)

	assert cipher.getSecurity() >= security

	keys = [numbers.randomBelow(modulus) for _ in wantedMessages]

	peer.send([(cipher.encrypt(keys[i]) + blinds[w]) % modulus for (i,w) in enumerate(wantedMessages)])

	dataMatrix = peer.recv([[range(modulus)] * messageCount] * passCount)

	data = [(dataMatrix[i][w] - keys[i]) for (i,w) in enumerate(wantedMessages)]
	
	if returnAsInt:
		return data[0]
	else:
		return data

def toBytes(elem):
	if isinstance(elem,bytes):
		return elem
	if isinstance(elem,str):
		return elem.encode()
	return str(elem).encode()

def psi(peer : Peer,
		myElements : Set[bytes],
		peerElementCount : int,
		needResult : bool,
		peerNeedsResult : bool,
		security : int):
	"""
	Determine the intersection of a local and a remote set of byte sequences stored at the peer.

	Either or both participants will learn the elements within the intersection, and nothing else.
	"""
	basic.agreeOn(peer,
		"Private set intersection",
		basic.AsymmetricAgreement(len(myElements),peerElementCount),
		basic.AsymmetricAgreement(needResult,peerNeedsResult))
	
	if not (needResult or peerNeedsResult):
		return None # Duh don't do anything then.
	
	modulus = random.sharedRandomProbablePrime(peer, security)

	cipher = exponents.commutative(modulus).keygen()

	myHashes = list(cipher.encrypt(int.from_bytes(sha256(toBytes(elem)).digest(),"big")) for elem in myElements)

	myPerm = list(utils.shufflingSwaps(len(myHashes)))

	peer.send(utils.performSwaps(list(myHashes),myPerm))
	
	peerHashes = [cipher.encrypt(k) for k in peer.recv([range(modulus)] * peerElementCount)]

	if peerNeedsResult:
		peer.send(peerHashes)
	
	if needResult:
		peerHashes = set(peerHashes)
		myHashes = utils.performSwaps(peer.recv([range(modulus)] * len(myElements)),reversed(myPerm))

		return set(elem for (elem,h) in zip(myElements,myHashes) if h in peerHashes)
	else:
		return None
