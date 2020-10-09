# Transformice Plugins
This project allows you to easily analyze and add plugins to Transformice. It scans your network activity that is going to transformice servers and gives that information to the plugins you add.<br/><br/>

Special thanks to @antiafk for the idea and @Athesdrake for some code ([watchdog.py](tfmplugins/utils/watchdog.py), [eventbased.py](tfmplugins/utils/eventbased.py), [packet.py](tfmplugins/tfm/packet.py))

## How does it work?
As it's been pointed out, what this does is it uses a driver to scan internet packets sent to transformice servers. This driver is meant to be easily replaceable to make the project work in more platforms.<br/>
The packets obtained from this network scan are passed directly to the plugins it has. In a future, these plugins will be able to inject packets too.<br/>
The project detects different open connections and identifies them by the local address (ip + port), so you can maintain multiple connections open. It ignores any connection that is open from before this script, so **you'll have to run the script and then open the game**.

## Limitations
This project can not be used to obtain encryption keys to connect to transformice other than the connection key (CKey), version and message keys. You can not obtain the identification keys (which are used to encrypt the login packet) as you can't obtain packet keys (which are used to generate both identification and message keys) from any of the data you can obtain. This also means you can't obtain a password with this.<br/>
It also can't block packets nor inject them yet.

## Usage
The project comes with a [plugins](plugins) directory where you can put all your plugins. They must be a valid python module, which means it can be either a file or a directory.<br/>
Once all your plugins are saved there, you can start the script. If any of the plugins gets modified, it will reload it within one second.<br/>
These plugins must have a `plugin` variable which should be an object with some specific methods. Example:
```python
class Plugin:
	async def tear_down(self):
		# This method will be executed when the plugin has to be reloaded.
		pass

	async def packet_sent(self, client, conn, fingerprint, packet):
		# This method will be executed when the script detects an outbound
		# packet (that is sent to the server).
		# client is an instance of TFMClient
		# conn is an instance of TFMConnection
		# fingerprint is an int, the fingerprint of the packet
		# packet is an instance of Packet
		pass

	async def packet_received(self, client, conn, packet):
		# This method will be executed when the script detects an inbound
		# packet (that is sent to the client).
		# client is an instance of TFMClient
		# conn is an instance of TFMConnection
		# packet is an instance of Packet
		pass


plugin = Plugin()
```
You can find an example and working plugin [here](https://github.com/Tocutoeltuco/tfm-richpresence).