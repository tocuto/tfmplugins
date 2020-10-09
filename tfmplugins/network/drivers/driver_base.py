"""
MIT License

Copyright (c) 2020 Iván Gabriel (Tocutoeltuco)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import time

from abc import ABC


class DriverBase(ABC):
	"""Base implementation of a driver (ip scanner).
	Scans a single IP for different connections and identifies them by local ip and port.

	Parameters
	----------
	network: :class:`network.scanner.NetworkScanner`
		The network scanner this driver belongs to to
	ip: :class:`str`
		The ip to scan
	connection: :class:`network.connection.Connection`
		The connection factory used to represent a connection

	Attributes
	----------
	network: :class:`network.scanner.NetworkScanner`
		The network scanner this driver belongs to to
	ip: :class:`str`
		The ip to scan
	connection: :class:`network.connection.Connection`
		The connection factory used to represent a connection
	connections: Dict[:class:`network.connection.Connection`]
		The connection list
	"""
	def __init__(self, network, ip, connection):
		self.network = network
		self.ip = ip
		self.connection = connection

		self.connections = {}

	def create_connection(self, network, local, remote):
		"""Uses the connection factory to create and store a new connection
		:param network: :class:`network.scanner.NetworkScanner` the network scanner the connection
			belongs to.
		:param local: :class:`tuple` the local address ("ip", port)
		:param remote: :class:`tuple` the remote address ("ip", port)
		:return: :class:`network.connection.Connection`
		"""
		conn = self.connection(network, local, remote)
		self.connections[local] = conn
		return conn

	def get_connection(self, source, dest, outbound):
		"""Gets the connection that belongs to the specific source, destination and direction of
		the packet.
		:param source: :class:`tuple` the source address ("ip", port)
		:param dest: :class:`tuple` the dest address ("ip", port)
		:param outbound: :class:`bool` whether the packet direction is outbound (True) or
			inbound (False)
		:return: :class:`network.connection.Connection`
		"""
		if outbound:
			local = source
			remote = dest
		else:
			local = dest
			remote = source

		if local not in self.connections:
			return self.create_connection(self.network, local, remote)

		conn = self.connections[local]
		if conn.closing and time.perf_counter() >= conn.closed_at:
			del self.connections[local]
			return self.create_connection(self.network, local, remote)

		return conn

	def scan(self):
		"""A loop that scans the ip until the scanner is closed.
		"""
		raise NotImplementedError

	def close(self):
		"""Closes the scanner.
		"""
		raise NotImplementedError