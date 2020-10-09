# Plugins
## What are they?
Plugins are python modules that live in this directory (any directory or file with .py extension is considered as a plugin) that are loaded with this script. They receive all the packets this script captures.

## How do I create one?
That's easy. You can create a .py file here or a directory that is a valid python module. They must have a `plugin` variable which is the plugin object.<br/>
Whenever a file in any plugin is modified, it gets automatically reloaded; however, when you create or delete a file, you have to reload the whole script.<br/>
Plugin example:
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