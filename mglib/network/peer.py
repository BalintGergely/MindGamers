
import socket
import json
import re

__addressPattern = re.compile(r"\A(?:(?:\[(?=.*\])|(?!.*\]))([^\[\]:]+|[^\[\]]+)\]?)??(?:(?:\A|(?!\A):)(\d{1,5}))?\Z")

class Peer():

	def send(self,data):
		raise Exception("Not implemented")
	
	def recv(self):
		raise Exception("Not implemented")

class SocketPeer(Peer):
	def __init__(self, config : str) -> None:
		super().__init__()

		match = __addressPattern.match(config)

		host = match[1]
		port = match[2]

		isHosting = host.startswith("host")
		if isHosting:
			host = "localhost"

		(family, socketType, protocol, flags, address) = socket.getaddrinfo(host, port)[0]

		self.__socket = socket.socket(family,socketType,protocol)

		if isHosting:
			self.__socket.bind(address)
		else:
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
	
	def recv(self):
		count = int.from_bytes(bytes = self.__recvexact(4), byteorder = "big", signed = False)
		raw = self.__recvexact(count)
		return json.loads(raw.decode())