
from hashlib import sha256
from mglib.network.peer import Peer
from typing import Iterable
import json

def agreeOn(peer : Peer,data : str | int):
	"""
	Cooperatively agree with a peer on some data.
	This is meant for data that both peers must be aware of,
	such as a public input, a public result, or the next step in a protocol.
	"""
	peer.send(data)
	other = peer.recv()
	assert other == data, f"Expected {data} but received {other}!"

def agreeToBeSender(peer : Peer):
	peer.send("Sender")
	other = peer.recv()
	assert other == "Receiver"

def agreeToBeReceiver(peer : Peer):
	peer.send("Receiver")
	other = peer.recv()
	assert other == "Sender"