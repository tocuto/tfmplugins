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

import os
import time
import importlib


class Watcher:
	INTERVAL = 1.0

	def __init__(self, name, filename):
		self.name = name
		self.filename = f"./plugins/{filename}"
		self.module = importlib.import_module(f"plugins.{name}")

		self.next_check = time.perf_counter() + self.INTERVAL
		self.timestamp = os.stat(self.filename).st_mtime

	def check(self):
		if time.perf_counter() >= self.next_check:
			last = self.timestamp

			self.timestamp = os.stat(self.filename).st_mtime
			self.next_check = time.perf_counter() + self.INTERVAL

			return self.timestamp != last

	async def get_plugin(self):
		if self.check():
			try:
				start = time.perf_counter()
				await self.module.plugin.tear_down()
				self.module = importlib.reload(self.module)
				taken = time.perf_counter() - start
				print(f"Reloaded module {self.name} in {taken} seconds.")
			except Exception as e:
				print(f"An error occured while reloading {self.filename}: {e}")

		return self.module.plugin


class PluginsWatcherIterator:
	def __init__(self, watchers):
		self.watchers = watchers
		self.index = 0
		self.limit = len(self.watchers)

	async def __anext__(self):
		if self.index < self.limit:
			watcher = self.watchers[self.index]
			self.index += 1
			return await watcher.get_plugin()

		else:
			raise StopAsyncIteration


class PluginsWatcher:
	def __init__(self):
		self.watchers = []

		with os.scandir("./plugins") as it:
			for entry in it:
				if entry.name == "__pycache__":
					continue

				if entry.is_file():
					if entry.name.endswith(".py"):
						self.watchers.append(Watcher(entry.name[:-3], entry.name))
				else:
					self.watchers.append(Watcher(entry.name, entry.name))

	def __aiter__(self):
		return PluginsWatcherIterator(self.watchers)