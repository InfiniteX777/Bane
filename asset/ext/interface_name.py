import pygame

import asset.api.SenPy as senpai
ahoge = senpai.remote["ahoge"]
kouhai = senpai.remote["kouhai"]
imouto = senpai.remote["imouto"]
kuudere = senpai.remote["kuudere"]

body = kuudere.get("calibri", 24, False)
placeholder = "What's your name?"

textbox = kouhai.TextBox({
	"scale_size": (1, 1)
})
textbox.set_focus(True)

surface = pygame.Surface(
	(imouto.rect.width, imouto.rect.height),
	pygame.SRCALPHA
)

def keyinput(event):
	surface.fill((0, 0, 0, 0))

	if event and (event.key == 13 or event.key == 271):
		name = textbox.properties["text"]

		if not name.isspace():
			textbox.destroy()
			keyinput_listener.disconnect()
			update_listener.disconnect()
			resize_listener.disconnect()

			import asset.ext.interface_main as main

			main.set_name(name)


	text = textbox.properties["text"]
	d = len(text) > 0

	kuudere.draw(
		surface,
		body,
		(0, 0, imouto.rect.width, imouto.rect.height),
		d and text or placeholder,
		1,
		d and (0, 0, 0) or (127, 127, 127),
		align=(0.5, 0.5)
	)

keyinput(None)
keyinput_listener = textbox.on("keyinput", keyinput)

def update(event):
	imouto.screen.blit(
		surface,
		(0, 0)
	)

def resize(event):
	global surface

	surface = pygame.Surface(
		(imouto.rect.width, imouto.rect.height),
		pygame.SRCALPHA
	)
	keyinput(None)

update_listener = imouto.on("update", update)
resize_listener = imouto.on("resize", resize)