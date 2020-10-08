from tfm.packet import Packet
from pypresence import AioPresence


class TFMPresence:
	discord = None

	async def check_discord(self):
		if self.discord is None:
			self.discord = AioPresence("763125602932097054")
			await self.discord.connect()

			await self.discord.update(
				large_image = "tfm-icon",
				details = "In login screen."
			)

	async def tear_down(self):
		if self.discord is not None:
			# AioPresence.close closes asyncio's event_loop,
			# we don't want that!
			self.discord.send_data(2, {"v": 1, "client_id": self.discord.client_id})
			self.discord.sock_writer.close()

	async def packet_sent(self, client, conn, fp, packet):
		await self.check_discord()

	async def packet_received(self, client, conn, packet):
		await self.check_discord()

		CCC = packet.readCode()

		if CCC == (1, 1): # old protocol
			oldCCC, *data = packet.readString().split(b"\x01")

			if oldCCC == b"\x1a\x12": # 26, 18 (ban)
				await self.discord.update(
					large_image = "tfm-icon",
					details = "Being naughty!"
				)

		elif CCC == (5, 21): # joined room
			packet.readBool() # is the room official?
			name = packet.readUTF()

			if name.startswith("*"):
				community = "int"
			else:
				community = name[:2]
				name = name[3:]

			if name.startswith("[Editeur]"):
				details = "Creating a map"
			elif name.startswith("[Totem]"):
				details = "Editing their totem"
			elif "\x03" in name:
				details = "In a tribehouse"
			else:
				details = "Playing in room {}".format(name)

			await self.discord.update(
				large_image = "tfm-icon",
				large_text = "Playing Transformice !",

				small_image = "commu-{}".format(community),
				small_text = "{} community".format(community.upper()),

				details = details
			)

		elif CCC == (29, 20):
			txt_id = packet.read32()

			if txt_id == 2147483647:
				data = packet.readUTF().split("\x00")
				if data.pop(0) == "\x01":
					# default status
					return

				options = {
					"state": data[0],
					"details": data[1],
					"start": int(data[2]) if data[2] else "",
					"end": int(data[3]) if data[3] else "",
					"large_image": data[4],
					"large_text": data[5],
					"small_image": data[6],
					"small_text": data[7],
					"party_size": [int(data[8] or "-1"), int(data[9] or "-1")]
				}

				if options["party_size"][0] < 0 or options["party_size"][1] < 0:
					del options["party_size"]

				for key, value in options.copy().items():
					if value == "":
						del options[key]

				await self.discord.update(**options)


plugin = TFMPresence()