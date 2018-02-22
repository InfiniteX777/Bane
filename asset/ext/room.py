''' Room creation.

	.set_server(server)
		Sets the server.

	.Room(room, name="Untitled Room")
		Creates a room with the given room id and name.

		.broadcast(data)
			Broadcasts the data to all the addresses in the room.

		.chat(data)
			Adds text to the room's surface. Does not broadcast.

		.get(i)
			If i is an address, will return the name assigned to the
			address. If i is an integer, will return both the
			address and its assigned name.

		.has(address)
			Checks if the address is in the room.

		.add(address, name)
			Attempts to add the address and its assigned name in the
			room. Does not update the address' assigned name if
			re-added.

		.rem(address)
			Removes the address if it's inside the room.

		.update()
			Updates the room, specifically the player surface.
'''
import asset.ext.socket_encoder as socket_encoder
import pygame

import asset.api.SenPy as senpai
kuudere = senpai.remote["kuudere"]

# Font
body = kuudere.get("calibri", 18, False)
body_line = body.get_linesize() + 10

server = None

def set_server(v):
	global server
	server = v

class Room:
	def __init__(self, room, name="Untitled Room"):
		global server, body, body_line
		players = {}
		chats = []

		def broadcast(data):
			for addr in players:
				if addr != server.addr:
					server.send(data, addr)

		def chat(data):
			chats.append(data)

			i = 0
			res, y, _ = kuudere.wrap(
				body,
				(380, 0),
				body_line,
				data,
				1,
				(191, 191, 191)
			)

			if not self.chat_surface:
				self.chat_surface = pygame.Surface(
					(380, y),
					pygame.SRCALPHA
				)
			else:
				surface_rect = self.chat_surface.get_rect()
				i = surface_rect.height

				# Update scroll
				if i - 570 <= self.chat_scroll:
					self.chat_scroll = max(0, i + y - 570)

				draft = pygame.Surface(
					(380, i + y),
					pygame.SRCALPHA
				)
				draft.blit(self.chat_surface, (0, 0))

				self.chat_surface = draft

			for image in res:
				rect = image.get_rect()
				self.chat_surface.blit(image,
					(0, i)
				)

				i += body_line

		def get(i):
			if type(i) == int:
				if i < len(players):
					addr = list(players)[i]

					return addr, players[addr]

				return None, None
			elif i in players:
				return players[i]

		def has(addr):
			v = addr in players

			return v

		def add(addr, name):
			if addr not in players:
				self.players += "_" + socket_encoder.encode(addr) + ":" + name

				players[addr] = name

		def rem(addr):
			if addr in players:
				tag = socket_encoder.encode(addr)
				n = "_" + tag + ":" + players[addr]
				i = self.players.find(n)
				self.players = self.players[:i] + self.players[i+len(n):]

				del players[addr]

		def update_player():
			self.player_surface = pygame.Surface(
				(200, len(players)*30),
				pygame.SRCALPHA
			)

			i = 0
			for addr in players:
				image = body.render(
					players[addr],
					True,
					(255, 255, 255)
				)
				rect = image.get_rect()

				self.player_surface.blit(image,
					(10, i*30 + 8)
				)

				pygame.draw.line(
					self.player_surface,
					(34, 34, 34),
					(0, i*30 + 29),
					(200, i*30 + 29)
				)

				i += 1

		self.name = name
		self.players = ""
		self.visible = 1
		self.chat_surface = None
		self.chat_scroll = 0
		self.chat_scroll_delta = 0
		self.player_surface = None
		self.player_scroll = 0
		self.player_scroll_delta = 0
		self.broadcast = broadcast
		self.chat = chat
		self.get = get
		self.has = has
		self.add = add
		self.rem = rem
		self.update = update_player