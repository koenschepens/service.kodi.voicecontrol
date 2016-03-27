# ssl_version corrections are done
#
# ##############################################################################
# Copyright 2015 SoundHound, Incorporated.  All rights reserved.
##############################################################################
import httplib
import socket
import ssl
import struct


class HTPMessage:
	HTP_TYPE_BINARY		= 0
	HTP_TYPE_JSON		= 1
	HTP_TYPE_XML		= 2

	def __init__(self, type, data):
		self.type = type
		self.data = data

import functools
import ssl

old_init = ssl.SSLSocket.__init__

@functools.wraps(old_init)
def ubuntu_openssl_bug_965371(self, *args, **kwargs):
    kwargs['ssl_version'] = ssl.PROTOCOL_TLSv1
    old_init(self, *args, **kwargs)

ssl.SSLSocket.__init__ = ubuntu_openssl_bug_965371

class HTPConnection:
	def __init__(self, hostname, port):
		## SSL connection
		self.rawConn = socket.socket(socket.AF_INET)
		self.rawConn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
		self.conn = ssl.wrap_socket(self.rawConn)
		self.conn.connect((hostname, port))

	def SendMessage(self, msg):
		self.conn.sendall(struct.pack('!I', len(msg.data)))
		self.conn.sendall(struct.pack('!H', msg.type))
		self.conn.sendall(msg.data)


	def ReadMessage(self):
		header = self._readExactBytes(6)

		# got the header, unpack it
		msgLen = struct.unpack('!I', header[:4])[0]
		msgType = struct.unpack('!H', header[4:])[0]

		if msgLen > 10000000:
			raise Exception("HTP message too large")

		return HTPMessage(msgType, self._readExactBytes(msgLen))


	def _readExactBytes(self, nbytes):
		buffer = ''
		while nbytes > 0:
			data = self.conn.recv(nbytes)
			if data:
				buffer += data
				nbytes -= len(data)
			else:
				raise Exception("no data in _readExactBytes")
		return buffer


	def Close(self):
		self.conn.close()
