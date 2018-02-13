import pygame

import asset.api.SenPy as senpai
ahoge = senpai.remote["ahoge"]
kouhai = senpai.remote["kouhai"]
imouto = senpai.remote["imouto"]
kuudere = senpai.remote["kuudere"]

# Image
shadow = pygame.image.load("asset/img/chatbox_shadow.png")
shadow_active = pygame.image.load("asset/img/chatbox_shadow_active.png")

# Font
header = kuudere.get("segoe ui", 16, False, True)
body = kuudere.get("calibri", 16, False)
body_line = body.get_linesize()

# Drag indicator.
drag = None
# Cache for chatboxes.
cache = {}
# Unique ID for each chatboxes.
cache_id = 1
# Text for the chatbox's textbox if empty.
placeholder = "Type here."

# The local server.
server = None
code = ""
# The local name of the user.
name = ""

# Intended to be called by interface_main.
def set_server(_server, _code):
	global server, code

	server = _server
	code = _code

# Intended to be called by interface_main.
def set_name(v):
	global name

	name = v

def mousebuttonup(event):
	global drag

	drag = None

def mousemotion(event):
	global drag

	if drag:
		drag.frame.properties["rect"] = drag.frame.properties["rect"].move(event.rel)

imouto.on("mousebuttonup", mousebuttonup)
imouto.on("mousemotion", mousemotion)

class Chatbox:
	def __init__(self, header, color=(255,255,255)):
		global code

		self.id = cache_id
		self.textbox = kouhai.TextBox({
			"rect": (0, -40, 0, 40),
			"scale_size": (1, 0),
			"scale_pos": (0, 1)
		})
		self.frame = kouhai.Frame({
			"rect": (0, 0, 300, 400),
			"child": [self.textbox],
			"zindex": 1
		})

		self.surface_text = None
		self.surface = pygame.Surface(
			(320, 420),
			pygame.SRCALPHA
		)
		self.color = color
		self.header = header
		self.surface_textbox = pygame.Surface(
			(280, 40),
			pygame.SRCALPHA
		)
		self.chat = []
		self.players = {
			server.addr: name
		}

		# Draw the placeholder.
		kuudere.draw(
			self.surface_textbox,
			body,
			(10, 0, 280, 40),
			placeholder,
			1,
			(127, 127, 127),
			align=(0, 0.5)
		)


		# Drag Functionality

		def mousebuttondown(event):
			global drag

			if self.frame.is_targeted() and event.pos[1]-self.frame.properties["rect"].y <= 24:
				drag = self

		self.frame.on("mousebuttondown", mousebuttondown)

		def keyinput(event):
			text = self.textbox.properties["text"]

			self.surface_textbox.fill((0, 0, 0, 0))

			if event.key == 13 or event.key == 271:
				self.textbox.properties["text"] = ""

				if len(text) > 0 and not text.isspace():
					text = name " : " + text

					self.broadcast("DATCHT" + self.id + code + "_" + text)
					self.chat(text)

				text = ""

			d = len(text) > 0

			kuudere.draw(
				self.surface_textbox,
				body,
				(10, 0, 280, 40),
				d and text or placeholder,
				1,
				d and (0, 0, 0) or (127, 127, 127),
				align=(0, 0.5)
			)

		self.textbox.on("keyinput", keyinput)

		cache[self.frame] = self
		cache_id += 1
	def chat(self, v):
		global body_line

		self.chat.append(v)

		image, y, _ = kuudere.wrap(
			body,
			(280, 0),
			body_line,
			v,
			1
		)

		if self.surface_text:
			rect = self.surface_text.get_rect()

			draft = pygame.Surface(
				(300, y + rect.bottom),
				pygame.SRCALPHA
			)

			draft.blit(self.surface_text,
				(0, 0)
			)

			self.surface_text = draft
			y = rect.bottom
		else:
			self.surface_text = pygame.Surface(
				(300,
				y),
				pygame.SRCALPHA
			)
			y = 0

		i = 0
		for v in image:
			self.surface_text.blit(v,
				(0, body_line*i + y)
			)

			i += 1

	def broadcast(self, text):
		global server

		for addr in self.players:
			if addr != server.addr:
				server.send(addr, text, True)

	def clear(self, v):
		self.surface_text = None

	def update(self):
		self.surface.fill(
			(0, 0, 0, 0)
		)

		# Fill
		self.surface.fill(
			(*self.color, 191),
			(10, 10, 300, 400)
		)

		# Shadow
		self.surface.blit(
			self.frame.properties["zindex"] == 2 and shadow_active or shadow,
			(0, 0)
		)

		# Header
		self.surface.blit(
			header.render(
				self.header,
				1,
				(0, 0, 0)
			),
			(36, 10)
		)

	def draw(self):
		rect = self.frame.properties["rect"]

		imouto.screen.blit(
			self.surface,
			rect.move(-10,-10)
		)

		if self.surface_text:
			imouto.screen.blit(
				self.surface_text,
				rect.move(10, 35),
				(0, 0, 280, 335)
			)

		imouto.screen.blit(
			self.surface_textbox,
			(rect.x, rect.y+360, rect.width, 40)
		)

def update(dt):
	global cache

	for frame in cache:
		cache[frame].draw()

def focused(frame):
	frame = frame.properties["parent"] or frame

	if frame in cache:
		self = cache[frame]

		frame.set_zindex(2)

		del cache[frame]
		cache[frame] = self

		self.update()

def unfocused(frame):
	frame = frame.properties["parent"] or frame

	if frame in cache:
		frame.set_zindex(1)
		cache[frame].update()

def load():
	imouto.on("update", update)
	imouto.on("focused", focused)
	imouto.on("unfocused", unfocused)