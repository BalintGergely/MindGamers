
import mglib.network.peer as peer
import mglib.network.basic as basic
import mglib.engine.rsa as rsa
import mglib.engine.numbers as numbers
from typing import List

def obliviousSend(peer : peer.Peer, messages : List[int], security):
	basic.agreeOn(peer,"Oblivious Transfer")
	basic.agreeToBeSender(peer)
	basic.agreeOn(peer,len(messages))
	cipher : rsa.RSACipher = rsa.keygen(security).keygen()
	modulus = cipher.getModulus()

	# Send the cipher
	peer.send(cipher.toJson(includePrivate = False))

	# Send random values
	hidden = [numbers.randomBelow(modulus) for _ in messages]

	peer.send(hidden)

	v = peer.recv()

	assert isinstance(v,int) and 0 <= v

	keys = [cipher.powPrivate(v - x) for x in hidden]

	peer.send([(m + k) % modulus for (m,k) in zip(messages,keys)])

def obliviousReceive(peer : peer.Peer, messageCount : int, wantedMessageIndex : int, security : int = 0):
	basic.agreeOn(peer, "Oblivious Transfer")
	basic.agreeToBeReceiver(peer)
	basic.agreeOn(messageCount)

	cipher = rsa.RSACipher(**peer.recv())
	modulus = cipher.getModulus()

	assert cipher.getSecurity() > security

	hidden = [peer.recv() for _ in range(messageCount)]

	k = numbers.randomBelow(modulus)

	peer.send((hidden[wantedMessageIndex] + cipher.powPublic(k)) % modulus)

	cts = peer.recv()

	return (cts[wantedMessageIndex] + k) % modulus




	
