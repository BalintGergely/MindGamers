
from hashlib import sha256
from mglib.network.peer import Peer
from typing import Iterable
import json

class AsymmetricAgreement:
	def __init__(self, send, recv) -> None:
		self.send = send
		self.recv = recv

def agreeOn(peers : Peer | Iterable[Peer],*data):
	"""
	Cooperatively agree with a peer on some data.
	This is meant for data that both peers must be aware of,
	such as a public input, a public result, or the next step in a protocol.
	"""
	if isinstance(peers,Peer):
		peers = [peers]
	for d in data:
		e = None
		if isinstance(d,AsymmetricAgreement):
			e = d.send
		else:
			e = d
		for p in peers:
			p.send(e)
	for d in data:
		e = None
		if isinstance(d,AsymmetricAgreement):
			e = d.recv
		else:
			e = d
		for p in peers:
			o = p.recv()
			assert o == e, f"Expected {e} but received {o}"

def sender():
	"""
	Indicate that we intend to be the sending party in an asymmetric protocol.
	"""
	return AsymmetricAgreement("Sender","Receiver")

def receiver():
	"""
	Indicate that we intend to be the receiving party in an asymmetric protocol.
	"""
	return AsymmetricAgreement("Receiver","Sender")