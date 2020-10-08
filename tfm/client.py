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

from utils import EventBased, PluginsWatcher


main_loop = asyncio.get_event_loop()


class TFMClient(EventBased):
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

		super().__init__()

	def packet_received(self, outbound, conn, packet):
		if outbound:
			fp = packet.read8()
			self.dispatch("raw_socket_outbound", conn, fp, packet)
		else:
			self.dispatch("raw_socket_inbound", conn, packet)

	async def on_trigger_plugin(self, plugin, sent, *args, **kwargs):
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
		async for plugin in self.watcher:
			self.dispatch("trigger_plugin", plugin, True, conn, fp, packet.copy(copy_pos=True))

	async def on_raw_socket_inbound(self, conn, packet):
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

		async for plugin in self.watcher:
			self.dispatch("trigger_plugin", plugin, False, conn, packet.copy())