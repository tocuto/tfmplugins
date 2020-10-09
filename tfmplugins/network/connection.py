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


class Connection:
	"""Represents a network connection.

	Parameters
	----------
	network: :class:`network.scanner.NetworkScanner`
		The network scanner the connection belongs to.
	local: :class:`tuple`
		The local address ("ip", port)
	remote: :class:`tuple`
		The remote address ("ip", port)

	Attributes
	----------
	network: :class:`network.scanner.NetworkScanner`
		The network scanner the connection belongs to.
	local: :class:`tuple`
		The local address ("ip", port)
	remote: :class:`tuple`
		The remote address ("ip", port)
	ignored: :class:`bool`
		Whether the connection is flagged as ignored
	closing: :class:`bool`
		Whether the connection is flagged as closing
	closing_at: :class:`int`
		The time when the connection will be considered as fully closed
	"""
	def __init__(self, network, local, remote):
		self.network = network
		self.local = local
		self.remote = remote

		self.ignored = False
		self.closing = False
		self.closed_at = 0

	def ignore(self):
		"""Flags the connection as ignored (don't do anything with its packets)
		"""
		self.ignored = True

	def close(self):
		"""Flags the connection as closing. This also flags it as ignored.
		This method should only be called when a TCP packet has the FIN flag
		set to it.
		"""
		self.ignore()

		self.closing = True
		self.closed_at = time.perf_counter() + 1.0

	def parse_packet(self, payload, outbound):
		"""Parses a packet (only called if the connection is not flagged as ignored)
		:param payload: :class:`bytes` or :class:`bytearray` the packet payload
		:param outbound: :class:`bool` whether the packet direction is outbound (True)
			or inbound (False)
		:return: :class:`bool` whether to send the packet to the other end or not
		"""
		raise NotImplementedError