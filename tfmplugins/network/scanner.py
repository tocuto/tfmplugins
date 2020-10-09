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
	"""A simple network scanner. Handles all the IP scanners

	.. _executor: https://docs.python.org/3/library/concurrent.futures.html#executor-objects

	Parameters
	----------
	driver: :class:`network.drivers.driver_base.DriverBase`
		The driver factory used to create a scanner
	connection: :class:`network.connection.Connection`
		The connection factory used to represent a connection
	pool: Optional[executor]
		The `executor`_ to use for every driver thread. If ``None`` is passed (default),
		the pool used will be ``concurrent.futures.ThreadPoolExecutor()``

	Attributes
	----------
	scanner: :class:`network.drivers.driver_base.DriverBase`
		The driver factory used to create a scanner
	connection: :class:`network.connection.Connection`
		The connection factory used to represent a connection
	pool: executor
		The `executor`_ to use for every driver thread. If ``None`` is passed (default),
		the pool used will be ``concurrent.futures.ThreadPoolExecutor()``
	futures: List[:class:`concurrent.futures.Future`]
		A list of futures created by this scanner that are running in the pool.
	scanners: Dict[:class:`network.drivers.driver_base.DriverBase`]
		A dictionary with all the ip scanners
	running: :class:`bool`
		Whether the network scanner is running or not
	"""
	def __init__(self, driver, connection, pool=None):
		self.pool = pool or ThreadPoolExecutor()

		self.scanner = driver
		self.connection = connection

		self.futures = []
		self.scanners = {}
		self.running = True

		self.pool.submit(self._watch_pool)

	def _watch_pool(self):
		"""A loop that watches all the futures added by this instance to the pool
		If one of them throws an exception, it will be printed.
		"""
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
		"""Stops the network scanner and closes all the ip scanners.
		"""
		if not self.running:
			return

		for scanner in self.scanners.values():
			scanner.close()
		self.scanners = {}

		self.running = False

	def add(self, ip):
		"""Creates a new ip scanner (if needed) and returns it.
		:param ip: :class:`str` the ip to scan.
		:return: :class:`network.drivers.driver_base.DriverBase`
		"""
		if ip not in self.scanners:
			print("New scanner for {}".format(ip))
			scanner = self.scanner(self, ip, self.connection)
			self.futures.append(self.pool.submit(scanner.scan))

			self.scanners[ip] = scanner
		return self.scanners[ip]

	def remove(self, ip):
		"""Closes and removes an ip scanner.
		"""
		if ip not in self.scanners:
			return

		self.scanners[ip].close()
		del self.scanners[ip]