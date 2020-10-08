import asyncio

from network import NetworkScanner
from network.drivers.windivert import WinDivertDriver
from tfm import TFMConnection, main_ip


if __name__ == '__main__':
	network = NetworkScanner(WinDivertDriver, TFMConnection)
	network.add(main_ip)
	print("Network scanner running.")

	try:
		asyncio.get_event_loop().run_forever()
	except KeyboardInterrupt:
		network.stop()
		print("\rBye bye!")