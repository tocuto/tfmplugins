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

from network import Connection
from tfm.packet import Packet
from tfm.client import TFMClient


main_ip = "51.75.130.180"
bulle_keys = {}


class TFMPacketReader:
	def __init__(self, extra):
		self.extra = extra

		self.buffer = bytearray()
		self.length = 0

	def consume_payload(self, payload):
		self.buffer.extend(payload)

		while len(self.buffer) > self.length:
			if self.length == 0:
				for i in range(5):
					byte = self.buffer.pop(0)
					self.length |= (byte & 0x7f) << (i * 7)

					if not byte & 0x80:
						break

				else:
					raise Exception("Malformed TFM packet payload")

				self.length += self.extra

			if len(self.buffer) >= self.length:
				yield Packet(self.buffer[:self.length])
				del self.buffer[:self.length]
				self.length = 0


class TFMConnection(Connection):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.outbound = self.create_reader(1)
		self.inbound = self.create_reader(0)

		self.client = None

		self.name = "main" if self.remote[0] == main_ip else "bulle"
		self.needs_handshake = True

		if self.name == "main":
			self.handshake_ccc = (28, 1)
		else:
			self.handshake_ccc = (44, 1)

	def create_reader(self, *args, **kwargs):
		return TFMPacketReader(*args, **kwargs)

	def create_client(self, *args, **kwargs):
		return TFMClient(*args, **kwargs)

	def parse_packet(self, tcp):
		reader = self.outbound if tcp.is_outbound else self.inbound

		for packet in reader.consume_payload(tcp.payload):
			if self.needs_handshake:
				# Ignore already created connections

				if tcp.is_inbound:
					self.ignore()
					break

				fp = packet.read8()
				CCC = packet.readCode()
				if CCC != self.handshake_ccc:
					self.ignore()
					break

				if self.name == "main":
					self.client = self.create_client(self)

				else:
					# link with main
					key = bytes(packet.readBytes(12))

					if key in bulle_keys:
						self.client = bulle_keys[key]
						self.client.bulle = self
						del bulle_keys[key]

					else:
						self.ignore()
						break

				packet.pos = 0
				self.needs_handshake = False

			elif tcp.is_inbound and self.name == "main":
				# Switch bulle

				CCC = packet.readCode()
				if CCC == (44, 1):
					key = bytes(packet.readBytes(12))
					bulle_keys[key] = self.client

					# listen for bulle
					self.network.add(packet.readUTF())

				packet.pos = 0

			self.client.packet_received(tcp.is_outbound, self, packet)

		return True