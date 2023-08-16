
from mglib.network.peer import Peer
import mglib.engine.numbers as numbers
import mglib.engine.shamir as shamir
import mglib.engine.rsa as rsa
import mglib.engine.commitment as commitment
import mglib.engine.utils as utils
import mglib.network.basic as basic
import mglib.protocol.random as random
import mglib.protocol.tpp as tpp
import mglib.progress as progress

from typing import Set, List

def secretChoice(peer : Peer,elementCount : int,finalCount : int,myChoices : Set[int],peerChoices : int,security : int):
	"""

	The Secret Choice protocol.

	"""
	if random.coinFlip(peer, security):
		print("Secret Choice Protocol as the Sender party")
		return secretChoiceA(peer, elementCount, finalCount, myChoices, peerChoices, security)
	else:
		print("Secret Choice Protocol as the Receiver party")
		return secretChoiceB(peer, elementCount, finalCount, myChoices, peerChoices, security)

def secretChoiceA(peer : Peer,elementCount : int,finalCount : int,myChoices : Set[int],peerChoices : int,security : int):
	
	assert finalCount < elementCount
	assert len(myChoices) + peerChoices < finalCount
	basic.agreeOn(peer, "Secret Choice", elementCount, finalCount, basic.AsymmetricAgreement(len(myChoices),peerChoices), basic.sender())

	phases = 11

	progress.progressInit(phases)
# Phase 1: Setup

	dhPrime = random.sharedRandomProbablePrime(peer, security)

	dhCipher = rsa.commutative(dhPrime).keygen()

	shamirModulus = numbers.randomPrime(security // 2 - 1)

	assert shamirModulus * shamirModulus < dhPrime

	shamirContext = shamir.Shamir(shamirModulus, finalCount)

	peer.send(shamirContext.toJson())

	proofOfResult = numbers.randomBelow(shamirContext.getModulus())

	shards = [((a * shamirModulus) + b) for (a,b) in shamirContext.shatter(proofOfResult, elementCount)]

	progress.progressTick(1,phases)
# Phase 2: Lock in the shard map

	shardCommitment = commitment.commit(" ".join(hex(k) for k in shards), security)

	peer.send(shardCommitment.phaseOne())

	progress.progressTick(2,phases)
# Phase 3: Send encrypted shards

	shardIndices = utils.shuffle(list(range(elementCount)))

	shardPermutation = [None for _ in shardIndices]

	for (i,v) in enumerate(shardIndices):
		shardPermutation[v] = i

	peer.send([dhCipher.encrypt(shards[i]) for i in shardIndices])

	progress.progressTick(3,phases)
# Phase 4: Send a subset of permutation mappings
	
	tpp.obliviousSend(peer,shardPermutation,peerChoices,security)

	progress.progressTick(4,phases)
# Phase 5: Receive doubly-encrypted shards

	doubleShards : List[int] = peer.recv([range(dhPrime)] * elementCount)

	progress.progressTick(5,phases)
# Phase 6: Receive a subset of permutation mappings

	bucket = set(tpp.obliviousReceive(peer,elementCount,[shardPermutation[c] for c in myChoices],security))
	
	assert len(bucket) == len(myChoices)

	bucket.update(range(0,finalCount - len(myChoices)))

	while len(bucket) < finalCount:
		bucket.add(numbers.randomBelow(elementCount))
	
	bucket = utils.shuffle(list(bucket))

	progress.progressTick(6,phases)
# Phase 7: Send single-encrypted result

	peer.send([dhCipher.decrypt(doubleShards[k]) for k in bucket])

	progress.progressTick(7,phases)
# Phase 8: Receive commitment of final result

	finalShardsCommitment = commitment.Commitment(**peer.recv(dict))
	finalShardsCommitment.verifyHasProof()

	progress.progressTick(8,phases)
# Phase 9: Determine if result is valid by our requirements

	psiWishSet = set([proofOfResult])

	for k in myChoices:
		psiWishSet.add(shards[k])

	psiResult = tpp.psi(peer,psiWishSet,finalCount + 1,True,False,security)

	assert len(psiResult) == len(psiWishSet)

	progress.progressTick(9,phases)
# Phase 10: Send shard mapping to the peer and allow them to verify it

	peer.send(shards)
	peer.send(shardCommitment.phaseTwo())

	progress.progressTick(10,phases)
# Phase 11: Receive final list of shards from the peer and verify it

	finalShards = peer.recv([range(dhPrime)] * finalCount)
	finalShardsCommitment.update(**peer.recv(dict))
	finalShardsCommitment.verify(" ".join(hex(k) for k in finalShards))

	progress.progressTick(11,phases)
	progress.progressEnd()
	return set(shards.index(shard) for shard in finalShards)

def secretChoiceB(peer : Peer,elementCount : int,finalCount : int,myChoices : Set[int],peerChoices : int,security : int):
	basic.agreeOn(peer, "Secret Choice", elementCount, finalCount, basic.AsymmetricAgreement(len(myChoices),peerChoices), basic.receiver())

	phases = 11

	progress.progressInit(phases)
# Phase 1: Setup

	dhPrime = random.sharedRandomProbablePrime(peer, security)

	dhCipher = rsa.commutative(dhPrime).keygen()

	shamirContext = shamir.Shamir(**peer.recv(dict))

	shamirModulus = shamirContext.getModulus()

	randomChoices = finalCount - len(myChoices) - peerChoices

	progress.progressTick(1,phases)
# Phase 2: Receive peer's lock in

	shardCommitment = commitment.Commitment(**peer.recv(dict))
	shardCommitment.verifyHasProof()

	progress.progressTick(2,phases)
# Phase 3: Receive encrypted shards

	encryptedShards = peer.recv([range(dhPrime)] * elementCount)

	progress.progressTick(3,phases)
# Phase 4: Receive a subset of permutation mappings

	myIndices = list(set(tpp.obliviousReceive(peer, elementCount, myChoices, security)))

	assert len(myIndices) == len(myChoices)
	
	randomIndices = [k for k in range(0,elementCount) if k not in myIndices]

	utils.shuffle(randomIndices)

	shardIndices = myIndices + randomIndices[:randomChoices]

	utils.shuffle(shardIndices)

	shardIndices.extend(randomIndices[randomChoices:])

	shardPermutation = [None for _ in shardIndices]

	for (i,v) in enumerate(shardIndices):
		shardPermutation[v] = i

	progress.progressTick(4,phases)
# Phase 5: Send doubly-encrypted shards

	peer.send([dhCipher.encrypt(encryptedShards[k]) for k in shardIndices])

	progress.progressTick(5,phases)
# Phase 6: Send a subset of permutation mappings

	tpp.obliviousSend(peer, shardPermutation, peerChoices, security)

	progress.progressTick(6,phases)
# Phase 7: Receive single-encrypted result

	encryptedShards = peer.recv([range(dhPrime)] * finalCount)

	finalShards = [dhCipher.decrypt(s) for s in encryptedShards]
	
	proofOfResult = shamirContext.recover((s // shamirModulus,s % shamirModulus) for s in finalShards)

	utils.shuffle(finalShards)

	progress.progressTick(7,phases)
# Phase 8: Lock in the encrypted result

	finalShardsCommitment = commitment.commit(" ".join(hex(k) for k in finalShards), security)
	peer.send(finalShardsCommitment.phaseOne())

	progress.progressTick(8,phases)
# Phase 9: Allow the peer to examine a subset of the result

	psiSet = set(finalShards)
	psiSet.add(proofOfResult)

	tpp.psi(peer, psiSet, peerChoices+1, False, True, security)

	progress.progressTick(9,phases)
# Phase 10: Receive shard mapping from the peer, and verify it

	shards : List = peer.recv([range(dhPrime)] * elementCount)
	assert len(shards) == elementCount
	assert all(isinstance(k,int) for k in shards)

	shardCommitment.update(**peer.recv(dict))
	shardCommitment.verify(" ".join(hex(k) for k in shards))

	finalItems = set(shards.index(shard) for shard in finalShards)

	assert all(m in finalItems for m in myChoices)

	progress.progressTick(10,phases)
# Phase 11: Send the encrypted result and allow the peer to verify it

	peer.send(finalShards)
	peer.send(finalShardsCommitment.phaseTwo())

	progress.progressTick(11,phases)
	progress.progressEnd()
	return finalItems

