''' A box for your texty goodness.
'''

def load(senpai, kouhai):
	moe = senpai.remote["moe"]
	imouto = senpai.remote["imouto"]

	class this(kouhai.Frame):
		def __init__(self, prop={}):
			super().__init__(prop)

			self.properties = dict({
				"text": "",
				"multiline": False
			}, **self.properties)

	def keyinput(event):
		if kouhai.focus and isinstance(kouhai.focus, this):
			prop = kouhai.focus.properties

			if event.key == 13 or event.key == 271: # Enter
				if prop["multiline"]:
					prop["text"] += "\n"
				#self.set_focus(False)
			elif event.key == 8: # Backspace
				prop["text"] = prop["text"][:-1]
			else:
				prop["text"] += event.unicode

			kouhai.focus.fire("keyinput", event)

	imouto.on("keyinput", keyinput)

	return this