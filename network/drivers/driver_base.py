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