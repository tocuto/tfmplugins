import errno
import socket

from pydivert import WinDivert
from network.drivers.driver_base import DriverBase


class WinDivertDriver(DriverBase):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.w = WinDivert(
			"ip.DstAddr == {0} || ip.SrcAddr == {0}".format(self.ip)
		)

	def scan(self):
		try:
			with self.w:
				for packet in self.w:
					conn = self.get_connection(packet)

					if packet.tcp.fin:
						conn.close()

					elif conn.ignored:
						self.w.send(packet)
						continue

					elif packet.payload:
						if not conn.parse_packet(packet):
							continue

					self.w.send(packet)

		except OSError as e:
			if e.errno == errno.EACCES: # Missing privileges
				raise Exception("Run me with admin privileges!") from e
			elif e.errno == errno.EBADF: # Invalid driver (closed)
				return
			raise

		finally:
			for conn in self.connections.values():
				conn.close()

			self.close()

	def close(self):
		if self.w.is_open:
			try:
				self.w.close()
			except Exception:
				pass

			# If the thread is stuck waiting for a packet, this will
			# make it detect a new packet, so it will end. This is
			# sent using UDP to make it quicker.
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			sock.sendto(b"\x00", (self.ip, 6666))