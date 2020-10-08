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