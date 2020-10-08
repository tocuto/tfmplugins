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
	def __init__(self, network, ip, connection):
		self.network = network
		self.ip = ip
		self.connection = connection

		self.connections = {}

	def create_connection(self, network, local, remote):
		conn = self.connection(network, local, remote)
		self.connections[local] = conn
		return conn

	def get_connection(self, packet):
		source = (packet.src_addr, packet.src_port)
		dest = (packet.dst_addr, packet.dst_port)

		if packet.is_outbound:
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
		raise NotImplementedError

	def close(self):
		raise NotImplementedError