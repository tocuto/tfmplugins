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

import traceback
import time

from concurrent.futures import ThreadPoolExecutor


class NetworkScanner:
	def __init__(self, driver, connection, pool=None):
		self.pool = pool or ThreadPoolExecutor()

		self.scanner = driver
		self.connection = connection

		self.futures = []
		self.scanners = {}
		self.running = True

		self.pool.submit(self._watch_pool)

	def _watch_pool(self):
		while self.running:
			to_remove = []

			for future in self.futures:
				if future.done():
					try:
						future.result()
					except Exception:
						traceback.print_exc()

					to_remove.append(future)

			for future in to_remove:
				self.futures.remove(future)

			time.sleep(1)

	def stop(self):
		if not self.running:
			return

		for scanner in self.scanners.values():
			scanner.close()
		self.scanners = {}

		self.running = False

	def add(self, ip):
		if ip not in self.scanners:
			print("New scanner for {}".format(ip))
			scanner = self.scanner(self, ip, self.connection)
			self.futures.append(self.pool.submit(scanner.scan))

			self.scanners[ip] = scanner
		return self.scanners[ip]

	def remove(self, ip):
		if ip not in self.scanners:
			return

		self.scanners[ip].close()
		del self.scanners[ip]