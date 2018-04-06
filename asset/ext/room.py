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
body = kuudere.get("calibri", 12, False)
body_line = body.get_linesize()

# The server.
server = None
# Cache responsible to log all existing rooms with at least 1 player.
cache = ""

class Room:
	def __init__(self, room, name="Untitled Room"):
		global server, body, body_line, cache
		# Players in this room.
		players = {}
		# Chat history log.
		chats = []
		# The room's unique ID.
		id = "\\" + room + "\\" + name

		# Rename the room. Should not be mistaken for the room's 'code'.
		def rename(name):
			nonlocal id, room
			global cache

			# Change name.
			self.name = name
			# Reformat ID.
			prev = id
			id = "\\" + room + "\\" + name

			if prev in cache:
				# Replace the registry in the cache.
				i = cache.index(prev)
				cache = cache[:i] + id + cache[i+len(prev):]

		# Send data to all the players in this room. 'nonserver' means
		# that if it should also send data to 'dedicated servers',
		# a proxy that is supposed to act as an anchor to keep a giant
		# chunk of data alive.
		def broadcast(data, nonserver=0):
			for addr in players:
				if addr != server.addr and (not nonserver or players[addr]):
					server.send(data, addr)

		# Write text on this room's chat log.
		def chat(data):
			chats.append(data)

			i = 0
			res, y, _ = kuudere.wrap(
				body,
				(290, 0),
				body_line,
				data,
				1,
				(255, 255, 255)
			)

			if not self.chat_surface:
				# First time to chat.
				self.chat_surface = pygame.Surface(
					(290, y),
					pygame.SRCALPHA
				)
			else:
				# Resize the chat log's image.
				surface_rect = self.chat_surface.get_rect()
				i = surface_rect.height

				# Update scroll.
				if i - 155 <= self.chat_scroll:
					self.chat_scroll = max(0, i + y - 155)

				draft = pygame.Surface(
					(290, i + y),
					pygame.SRCALPHA
				)
				draft.blit(self.chat_surface, (0, 0))

				self.chat_surface = draft

			# Draw the text into the chat log.
			for image in res:
				rect = image.get_rect()
				self.chat_surface.blit(image,
					(0, i)
				)

				i += body_line

		# If 'i' is an integer, get the corresponding player's address
		# and name based on 'i' as the index. If i is an address,
		# get the player's name based on the address.
		def get(i):
			if type(i) == int:
				if i < len(players):
					n = 0

					for addr in players:
						if players[addr]:
							if n == i:
								return addr, players[addr]

							n += 1

				return None, None
			elif i in players:
				return players[i]

		# If player is in the room. '.get()' also works as it returns
		# something if the player is in the room, but since
		# dedicated servers has an empty string as their name, it will
		# return 'False' when used in conditional statements.
		def has(addr):
			return addr in players

		# Add the player in the room with its coressponding name.
		def add(addr, name):
			global cache

			if addr not in players:
				if (room[0] != "0" and
					room != "global" and
					not len(players) and
					addr == server.addr):
					# Room finally has a player. Add it to the cache.
					cache += id

				# Add player data in a string. Used for sending data.
				# This keeps the data ready instead of always
				# iterating through the dictionary.
				self.players += (
					"\\" + socket_encoder.encode(addr, 0) +
					"\\" + name
				)

				# Add player in a dictionary. Used for fast searching.
				players[addr] = name

		# Remove player from the room.
		def rem(addr):
			global cache

			if addr in players:
				tag = socket_encoder.encode(addr, 0)
				n = "\\" + tag + "\\" + players[addr]
				# Clear player data from the string.
				i = self.players.find(n)
				self.players = (
					self.players[:i] +
					self.players[i+len(n):]
				)

				del players[addr]

				if addr == server.addr:
					# It was you who left the room.
					if id in cache:
						# Since you don't own the room anymore,
						# remove from the cache.
						i = cache.index(id)
						cache = cache[:i] + cache[i+len(id):]
				elif len(players) and list(players)[0] == server.addr:
					if room[0] != "0" and room != "global" and id not in cache:
						cache += id

		def update_player():
			self.player_surface = pygame.Surface(
				(80, len(players)*20),
				pygame.SRCALPHA
			)

			i = 0
			for addr in players:
				if players[addr]:
					image = body.render(
						players[addr],
						True,
						(255, 255, 255)
					)
					rect = image.get_rect()

					self.player_surface.blit(image,
						(5, i*20 + 5)
					)

					pygame.draw.line(
						self.player_surface,
						(34, 34, 34),
						(0, i*20 + 29),
						(80, i*20 + 29)
					)

					i += 1

		self.password = None
		self.name = name
		self.players = ""
		self.visible = 1
		self.chat_surface = None
		self.chat_scroll = 0
		self.chat_scroll_delta = 0
		self.player_surface = None
		self.player_scroll = 0
		self.player_scroll_delta = 0
		self.rename = rename
		self.broadcast = broadcast
		self.chat = chat
		self.get = get
		self.has = has
		self.add = add
		self.rem = rem
		self.update = update_player