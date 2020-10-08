local setDiscordStatus
do
	local RPC_TXT_ID = 2147483647
	local fields = {
		"state", "details", "start", "_end",
		"large_image", "large_text", "small_image", "small_text",
		"party_size", "party_max"
	}

	function setDiscordStatus(status, target)
		local data = {""}

		if not status then
			data[1] = "\1"
		else
			for i = 1, #fields do
				if status[fields[i]] == nil then
					data[i + 1] = ""
				else
					data[i + 1] = tostring(status[fields[i]])
				end
			end
		end

		ui.addTextArea(
			RPC_TXT_ID,
			table.concat(data, "\0"),
			target, 5, 3, 0, 0,
			0, 0, 0, true
		)
	end
end

setDiscordStatus({
	state = "Testing something",
	details = "Implementing discord RPC in tfm!",

	large_image = "tfm-icon",
	small_image = "commu-" .. tfm.get.room.community
}, "Tocutoeltuco#0000")