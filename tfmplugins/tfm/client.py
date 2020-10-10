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

import sys
import asyncio
import traceback

from tfmplugins.utils import EventBased, PluginsWatcher
from tfmplugins.tfm.packet import Packet


main_loop = asyncio.get_event_loop()


class TFMClient(EventBased):
	"""Represents a Transformice client.

	.. _event loop: https://docs.python.org/3/library/asyncio-eventloops.html

	Parameters
	----------
	main: :class:`tfm.network.TFMConnection`
		The connection to the main server.
	loop: Optional[event loop]
		The `event loop`_ to use for asynchronous operations. The default value is
		a cached version of the loop of the main thread.

	Attributes
	----------
	loop: event loop
		The `event loop`_ to use for asynchronous operations.
	main: :class:`tfm.network.TFMConnection`
		The connection to the main server.
	bulle: Optional[:class:`tfm.network.TFMConnection`]
		The connection to the bulle server.
	logged: :class:`bool`
		Whether the client has logged in or not.
	id: Optional[:class:`id`]
		The accout id of the player. 0 for souris.
	name: Optional[:class:`str`]
		The name of the account.
	pid: Optional[:class:`id`]
		The login id of the player. Unique every connection, even if it uses the same
		account. This is not 0 for souris.
	is_souris: :class:`bool`
		Whether the client has logged in as a souris.
	msg_keys: Optional[:class:`list`]
		Message keys. May be None if they haven't been calculated yet.
	"""
	watcher = PluginsWatcher()

	def __init__(self, main, loop=main_loop):
		self.loop = loop

		self.main = main
		self.bulle = None

		self.logged = False
		self.id = None
		self.name = None
		self.pid = None
		self.is_souris = False

		self.msg_keys = None
		self._msg_packet = None

		super().__init__()

	def packet_received(self, outbound, conn, packet):
		"""Dispatches the events when receiving some data.

		:param outbound: :class:`bool` whether the packet direction is outbound (True)
			or inbound (False)
		:param conn: :class:`tfm.network.TFMConnection` the connection that captured
			this packet
		:param packet: :class:`tfm.packet.Packet` the packet
		"""
		if outbound:
			fp = packet.read8()
			self.dispatch("raw_socket_outbound", conn, fp, packet)
		else:
			self.dispatch("raw_socket_inbound", conn, packet)

	async def on_trigger_plugin(self, plugin, sent, *args, **kwargs):
		"""|coro|
		Dispatches the data event on a plugin.

		:param plugin: the plugin (any class that implements packet_sent and
			packet_received coroutines)
		:param sent: :class:`bool` whether the packet is being sent (True)
			or received (False)
		:param *args: arguments to pass to the event
		:param **kwargs: keyword arguments to pass to the event
		"""
		if sent:
			method = plugin.packet_sent
		else:
			method = plugin.packet_received

		try:
			await method(self, *args, **kwargs)

		except Exception:
			message = 'Ignored exception on plugin "{0.name}" while parsing {2} packet:\n\n{1}'
			tb = traceback.format_exc()
			print(message.format(plugin, tb, "outbound" if sent else "inbound"), file=sys.stderr)

	async def on_raw_socket_outbound(self, conn, fp, packet):
		"""|coro|
		Triggered when a packet has been sent to the server.

		:param conn: :class:`tfm.network.TFMConnection` the connection that captured
			this packet
		:param fp: :class:`int` the packet fingerprint
		:param packet: :Class:`tfm.packet.Packet` the captured packet
		"""
		if self.logged:
			CCC = packet.readCode()

			if CCC == (6, 6): # chat message
				if self.msg_keys is None and len(packet.buffer) > 22:
					self._msg_packet = (fp, packet.readBytes(20))

			packet.pos = 1

		async for plugin in self.watcher:
			self.dispatch("trigger_plugin", plugin, True, conn, fp, packet.copy(copy_pos=True))

	async def on_raw_socket_inbound(self, conn, packet):
		"""|coro|
		Triggered when a packet has been received from the server.

		:param conn: :class:`tfm.network.TFMConnection` the connection that captured
			this packet
		:param packet: :Class:`tfm.packet.Packet` the captured packet
		"""
		if not self.logged:
			CCC = packet.readCode()

			if CCC == (26, 2):
				self.logged = True
				self.id = packet.read32()
				self.name = packet.readUTF()
				packet.read32() # played time
				packet.read8() # community
				self.pid = packet.read32()
				self.is_souris = self.id == 0

			packet.pos = 0

		elif self.msg_keys is None and self._msg_packet is not None:
			CCC = packet.readCode()

			if CCC == (6, 6):
				if packet.readUTF() == self.name:
					fp, ciphered = self._msg_packet
					deciphered = Packet.new(6, 6).writeBytes(packet.readBytes(20))

					deciphered.xor_cipher(ciphered, -1)
					deciphered.pos = 2

					start = (fp + 1) % 20
					last = deciphered.readBytes(20 - start)

					self._msg_packet = None
					self.msg_keys = []
					for byte in (deciphered.readBytes(start) + last):
						self.msg_keys.append(byte)

			packet.pos = 0

		async for plugin in self.watcher:
			self.dispatch("trigger_plugin", plugin, False, conn, packet.copy())