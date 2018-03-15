''' The interface for the login and dedicated
	server creation.
'''
import pygame, threading

import asset.api.SenPy as senpai
ahoge = senpai.remote["ahoge"]
kouhai = senpai.remote["kouhai"]
imouto = senpai.remote["imouto"]
kuudere = senpai.remote["kuudere"]

# Image
img_bg = pygame.image.load("asset/img/start_bg.png")
img_btn = [
	pygame.image.load("asset/img/start_btn.png"),
	pygame.image.load("asset/img/start_btn_hover.png"),
	pygame.image.load("asset/img/start_btn_down.png")
]

# Font
body = kuudere.get("calibri", 14, False)


list_btn = []
list_txt = []
hold = None

def draw():
	imouto.screen.blit(
		img_bg,
		(0, 0)
	)

	for frame, surface in list_btn:
		rect = frame.properties["rect"]

		imouto.screen.blit(
			surface,
			(rect.x - 10, rect.y - 10)
		)

	for frame, surface in list_txt:
		rect = frame.properties["rect"]

		imouto.screen.blit(
			surface,
			(rect.x + 2, rect.y + 2)
		)

def mousebuttonup(event):
	global hold

	if hold:
		v = hold
		hold = None

		v()

imouto.on("mousebuttonup", mousebuttonup)

def btn(x, y, text, callback):
	frame = kouhai.Frame({
		"rect": (x, y, 180, 30)
	})
	surface = pygame.Surface(
		(200, 50),
		pygame.SRCALPHA
	)
	text = body.render(
		text,
		True,
		(255, 255, 255)
	)
	offset = 100 - text.get_rect().width/2
	state = 0

	list_btn.append((frame, surface))

	def update():
		global hold
		nonlocal state, update, callback
		v = state == 2 and hold != update

		if v:
			state = 1

		surface.fill((0, 0, 0, 0))
		surface.blit(
			img_btn[state],
			(0, 0)
		)
		surface.blit(
			text,
			(offset, 19)
		)

		draw()

		if v:
			callback()

	def mouseenter():
		global hold
		nonlocal state, update

		if hold == update:
			state = 2
		else:
			state = 1

		update()

	frame.on("mouseenter", mouseenter)

	def mouseleave():
		global hold
		nonlocal state, update

		state = 0

		update()

	frame.on("mouseleave", mouseleave)

	def mousebuttondown(event):
		global hold
		nonlocal state, update

		state = 2
		hold = update

		update()

	frame.on("mousebuttondown", mousebuttondown)

	update()

def txt(x, y, placeholder, text=""):
	textbox = kouhai.TextBox({
		"rect": (x, y, 180, 30),
		"text": text
	})
	surface = pygame.Surface(
		(200, 50),
		pygame.SRCALPHA
	)

	list_txt.append((textbox, surface))

	def keyinput(event):
		surface.fill((0, 0, 0, 0))

		text = textbox.properties["text"]
		d = len(text) > 0

		kuudere.draw(
			surface,
			body,
			(5, 5, 170, 20),
			d and text or placeholder,
			1,
			d and (191, 191, 191) or (127, 127, 127),
			align=(0, 0.5)
		)

		draw()

	keyinput(None)
	textbox.on("keyinput", keyinput)

def login():
	name = list_txt[0][0].properties["text"]

	# Not only space, more than 0 characters, no '\'.
	if not name.isspace() and len(name) > 0 and "\\" not in name:
		for frame, _ in list_btn:
			frame.destroy()

		for frame, _ in list_txt:
			frame.destroy()

		import asset.ext.interface_main as main

		main.set_name(name)

btn(310, 255, "Login", login)

def server():
	ip = list_txt[1][0].properties["text"]
	port = list_txt[2][0].properties["text"]

	try:
		# Check address syntax.
		port = int(port)

		if len([int(x) for x in ip.split(".")[:4]]) != 4:
			return
	except:
		return

	for frame, _ in list_btn:
		frame.destroy()

	for frame, _ in list_txt:
		frame.destroy()

	import asset.ext.interface_server as main

	main.set_server((
		list_txt[1][0].properties["text"],
		int(list_txt[2][0].properties["text"])
	))

btn(310, 405, "Start Dedicated Server", server)

txt(310, 210, "Name")
txt(310, 320, "IPv4 Address", "127.0.0.1")
txt(310, 360, "Port", "6000")

threading.Timer(1, draw).start()