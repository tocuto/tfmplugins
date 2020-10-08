import time


class Connection:
	def __init__(self, network, local, remote):
		self.network = network
		self.local = local
		self.remote = remote

		self.ignored = False
		self.closing = False
		self.closed_at = 0

	def ignore(self):
		self.ignored = True

	def close(self):
		self.ignore()

		self.closing = True
		self.closed_at = time.perf_counter() + 1.0

	def parse_packet(self, packet):
		raise NotImplementedError