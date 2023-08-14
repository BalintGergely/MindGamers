
import socket
import json
import re
import types
import itertools

addressPattern = re.compile(r"\A(?:(?:\[(?=.*\])|(?!.*\]))([^\[\]:]+|[^\[\]]+)\]?)??(?:(?:\A|(?!\A):)(\d{1,5}))?\Z")

def typeCheck(value,pattern):
	if pattern is ... or pattern is value: # Handles None, True, False
		return True
	if isinstance(pattern,tuple):
		return any(typeCheck(value,p) for p in pattern)
	if isinstance(pattern,type | types.UnionType):
		return isinstance(value,pattern)
	if isinstance(pattern,list):
		return isinstance(value,list) and len(pattern) == len(value) and all(typeCheck(v,p) for (v,p) in zip(value,pattern))
	if isinstance(pattern,dict):
		return isinstance(value,dict) and all(k in pattern and typeCheck(v,pattern[k]) for (k,v) in value.items())
	if isinstance(pattern,range) or isinstance(value,set):
		return isinstance(value,int) and value in pattern
	return False

class Peer():

	def send(self,data):
		raise Exception("Not implemented")
	
	def recv(self,t = None):
		raise Exception("Not implemented")

class SocketPeer(Peer):
	def __init__(self, config : str) -> None:
		super().__init__()

		match = addressPattern.match(config)

		host = match[1]
		port = match[2]

		isHosting = host.startswith("host")
		if isHosting:
			host = "localhost"

		(family, socketType, protocol, flags, address) = socket.getaddrinfo(host, port)[0]

		if isHosting:
			with socket.socket(family,socketType,protocol) as ss:
				ss.bind(address)
				ss.listen(1)
				self.__socket = ss.accept()[0]
		else:
			self.__socket = socket.socket(family,socketType,protocol)
			self.__socket.connect(address)
	
	def __recvexact(self, count):
		buf = bytes()
		while len(buf) < count:
			buf = buf + self.__socket.recv(count - len(buf))
		return buf
	
	def send(self,data):
		raw = json.dumps(data).encode()
		self.__socket.send(len(raw).to_bytes(length = 4, byteorder = "big",signed = False))
		self.__socket.send(raw)
	
	def recv(self,*typePattern):
		count = int.from_bytes(bytes = self.__recvexact(4), byteorder = "big", signed = False)
		raw = self.__recvexact(count)
		data = json.loads(raw.decode())
		t = tuple(typePattern)
		if len(typePattern) > 0:
			assert typeCheck(data,typePattern)
		return data

	def close(self):
		self.__socket.close()