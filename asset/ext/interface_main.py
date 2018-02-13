import pygame, re, math
import asset.ext.socket_encoder as socket_encoder
import asset.ext.chat as chat

import asset.api.SenPy as senpai
ahoge = senpai.remote["ahoge"]
kouhai = senpai.remote["kouhai"]
imouto = senpai.remote["imouto"]
kuudere = senpai.remote["kuudere"]

# Server Init
server = ahoge.stream(ahoge.ip, 0)
code = socket_encoder.encode(*server.addr)
selected_room = code
room = {
	code: {
		"_chat": [],
		"_chat_scroll": 0,
		"_chat_scroll_delta": 0
	}
}
chatbox = {}
chatbox_id = 2
name = ""

chat.set_server(server, code) # Set server.

# Font
header = kuudere.get("segoe ui", 24, False, True)
body = kuudere.get("calibri", 18, False)
body_line = body.get_linesize() + 10

placeholder = "[Invite Code Here]"

def broadcast(code, data):
	global room, server

	for addr in room[code]:
		if type(addr) == tuple and addr != server.addr:
			server.send(data, addr, True)

# Server

def on_recv(data, addr):
	''' id = The scope of the chat room.
			0 = Server-Wide
			1 = 2-User
			2~= Multi-User
		code = The encoded address.
		name = The name of the user.
	'''
	global room, code, selected_room, chatbox

	if data[:6] == "REQCON": # Request Connection (Room)
		# REQCON[code]:[name]

		if addr in room[code]:
			return # Already connected.

		dat = data[6:]
		room[code][addr] = dat

		# Broadcast to all the players in the room.
		msg = "'" + dat + "' has connected."
		chat_append(code, msg)
		broadcast(code, "DATPLR0" + code + "_" + socket_encoder.encode(*addr) + ":" + dat)

		res = "DATCON" + code

		if selected_room == code:
			player_update()

		for k, v in room[code].items():
			if k[0] != "_":
				res += "_" + socket_encoder.encode(*k) + ":" + v

		server.send(res, addr, True)
	elif data[:6] == "REQPLR": # Request Player
		# Sends the player list of the given room.
		# REQPLR[id][code]
		i = data[6:]
		tag = i
		list = None

		if i[0] == "0":
			# Server Chat
			dat = data[7:]

			if dat in room:
				list = room[dat]
		else:
			# Private Chat
			if i[0] == "1":
				i = i[1:]
				tag = "1" + code

			if i in chatbox:
				list = chatbox[i].players

		if list:
			res = "DATPLR" + tag

			for k, v in list.items():
				if type(k) == tuple:
					res += "_" + socket_encoder.encode(*k) + ":" + v

			server.send(res, addr, True)
	elif data[:6] == "REQDIS": # Request Disconnect
		data = data[6:]

		if len(data) > 0:
			# Server closed.
			# REQDIS
			if data in room:
				if selected_room == data:
					selected_room = code

					room_update()
					player_update()

				del room[data]
		else:
			# Player disconnected.
			# REQDIS[code]
			dat = room[code][addr]

			del room[code][addr]

			msg = "'" + dat + "' has disconnected."
			chat_append(code, msg)
			broadcast(code, "DATDIS0" + code + "_" + socket_encoder.encode(*addr) + ":" + dat)

			if selected_room == code:
				player_update()
	elif data[:6] == "DATCON": # Data Connection
		# Collect players in the server.
		# DATCON[code]_[code1]:[name1]_[code2]:[name2]...
		code_host = None

		for v in re.split("_", data[6:]):
			if not code_host:
				code_host = v
				room[v] = {
					"_chat": [],
					"_chat_scroll": 0,
					"_chat_scroll_delta": 0
				}
			else:
				sep = v.index(":")
				room[code_host][socket_encoder.decode(v[:sep])] = v[sep+1:]

		room_update()
	elif data[:6] == "DATPLR": # Data Player
		# Informs a player is connected in a room.
		# DATPLR[id][code]_[code1]:[name1]_[code2]:[name2]...
		sep = data.index("_")
		i = data[6:sep]

		if i[0] == "0":
			# Global Room
			i = i[1:]

			if i in room:
				for v in re.split("_", data[sep+1:]):
					sep = v.index(":")
					addr = socket_encoder.decode(dat[:sep])
					dat = v[sep+1:]
					room[i][addr] = dat

					chat_append(i, "'" + dat + "' has connected.")

				if selected_room == i:
					player_update()
		else:
			# Private Room
			if i[0] == "1":
				i = i[1:]

			if i in chatbox:
				for v in re.split("_", data[sep+1:]):
					sep = v.index(":")
					chatbox[i].players[socket_encoder.decode(v[:sep])] = v[sep+1:]
	elif data[:6] == "DATDIS": # Data Disconnect
		sep = data.index("_")
		i = data[6:sep]
		dat = data[sep+1:]

		if i[0] == "0" and i[1:] in room:
			# Global Room DATPLR0[code]_[code]:[name]
			sep = dat.index(":")
			i = i[1:]
			addr = socket_encoder.decode(dat[:sep])

			if addr in room[i]:
				del room[i][addr]

			chat_append(i, "'" + dat[sep+1:] + "' has disconnected.")

			if selected_room == i:
				player_update()
		else:
			# Private Room DATPLR[chatnum]_[code]:[name]
			pass
	elif data[:6] == "DATCHT": # Data Chat
		# Sends chat data to a room.
		# DATCHT[id][code]_[text]
		# 0 = Global
		# 1 = 2-Person
		# 2~ = Multi-Person
		sep = data.index("_")
		i = data[6:sep]
		text = data[sep+1:]

		if i[0] == "0":
			# Global Chat
			i = data[7:sep]

			if i in room:
				room[i]["_chat"].append(text)
				chat_append(i, text)
		else:
			tag = i

			if i[0] == "1":
				i = i[1:]
				tag = "1" + code

			if i not in chatbox:
				chatbox[i] = chat.Chatbox(addr[0] + ":" + str(addr[1]))
				chatbox[i].tag = tag

				chatbox[i].update()
				server.send("REQPLR" + tag, addr)

			chatbox[i].append(text)

server.on_recv(on_recv)

# Info Surface (Top-left Corner)

surface_info = None

def write(v, pos=(0, 0)):
	global surface_info

	image = body.render(
		v,
		True,
		(0, 0, 0)
	)
	rect = image.get_rect()

	if not surface_info:
		surface_info = pygame.Surface(
			(rect.width + pos[0], rect.height + pos[1]),
			pygame.SRCALPHA
		)
	else:
		rect1 = surface_info.get_rect()
		draft = pygame.Surface((
			max(rect.width, rect1.right + pos[0]),
			max(rect.height, rect1.bottom + pos[1])
		), pygame.SRCALPHA)

		draft.blit(surface_info, (0, 0))

		surface_info = draft

	surface_info.blit(image, pos)

def set_name(v):
	global code, room, server, name

	# Set name.
	name = v
	room[code][server.addr] = v
	chat.set_name(v) # For the chatbox.

	write("Name: " + v,
		(10, 10 + body_line*2)
	)

	room_update()
	player_update()

write("Invite Code: " + socket_encoder.encode(*server.addr),
	(10, 10))
write("Socket: " + server.addr[0] + ":" + str(server.addr[1]),
	(10, 10 + body_line))


# Room System

## Player List

scroll_player = 0
scroll_player_delta = 0
frame_player = kouhai.Frame({
	"rect": (-200, 0, 300, 200),
	"scale_pos": (1, 0)
})
surface_player = None

def player_mousebuttondown(event):
	global room, selected_room, chatbox
	i = int(event.pos[1]/30) + scroll_player

	for addr, name in room[selected_room].items():
		if type(addr) == tuple:
			if i > 0:
				i -= 1
			else:
				i = socket_encoder.encode(*addr)

				if addr != server.addr and i not in chatbox:
					chatbox[i] = chat.Chatbox(addr[0] + ":" + str(addr[1]))
					chatbox[i].players[addr] = name
					chatbox[i].tag = "1" + code

					chatbox[i].update()
				break

frame_player.on("mousebuttondown", player_mousebuttondown)

def player_update():
	global room, selected_room, surface_player

	surface_player = pygame.Surface(
		(180, len(room[selected_room])*30),
		pygame.SRCALPHA
	)

	# Get all the players in the room.
	i = 0
	for k, v in room[selected_room].items():
		if k[0] != "_":
			image = body.render(
				v,
				True,
				(0, 0, 0)
			)
			image_rect = image.get_rect()

			surface_player.blit(image,
				(180 - image_rect.width,
				i*30 + 30 - image_rect.height)
			)

			i += 1


## Room List

scroll_room = 0
scroll_room_delta = 0
frame_room = kouhai.Frame({
	"rect": (0, -340, 200, 300),
	"scale_pos": (0, 1)
})
surface_room = None

def room_mousebuttondown(event):
	global room, selected_room

	i = int((imouto.rect.height - event.pos[1] - 40)/30) + scroll_room

	if i < len(room):
		n = 0
		# Find the room with the corresponding index.
		for k in room:
			if i == n:
				selected_room = k
				break

			n += 1

		room_update()
		player_update()

frame_room.on("mousebuttondown", room_mousebuttondown)

def room_update():
	global surface_room, selected_room
	i = max(10, len(room))

	surface_room = pygame.Surface(
		(180, i*30),
		pygame.SRCALPHA
	)

	for k in room:
		i -= 1
		addr = socket_encoder.decode(k)
		image = body.render(
			addr[0] + ":" + str(addr[1]),
			True,
			k == selected_room and (0, 0, 0) or (127, 127, 127)
		)

		surface_room.blit(image,
			(0, i*30 + 30 - image.get_rect().height)
		)


## Global Chat

frame_chat = kouhai.Frame({
	"rect": (-300, -340, 300, 300),
	"scale_pos": (1, 1)
})

textbox_chat = kouhai.TextBox({
	"rect": (-300, -40, 300, 40),
	"scale_pos": (1, 1)
})

surface_chat = pygame.Surface(
	(280, 40),
	pygame.SRCALPHA
)

def chat_append(code, text):
	global room, body, body_line
	i = 0
	res, y, _ = kuudere.wrap(
		body,
		(280, 0),
		body_line,
		text,
		1
	)

	if "_chat_surface" not in room[code]:
		room[code]["_chat_surface"] = pygame.Surface(
			(300, y),
			pygame.SRCALPHA
		)
	else:
		# Extend surface.
		surface = room[code]["_chat_surface"]
		surface_rect = surface.get_rect()
		i = surface_rect.height

		# Update scroll
		if i - 300 <= room[code]["_chat_scroll"]:
			room[code]["_chat_scroll"] = max(0, i + y - 300)

		draft = pygame.Surface(
			(280, i + y),
			pygame.SRCALPHA
		)
		room[code]["_chat_surface"] = draft

		draft.blit(surface, (0, 0))

	for image in res:
		rect = image.get_rect()
		room[code]["_chat_surface"].blit(image,
			(0, i)
		)

		i += body_line

def chat_mousebuttondown(event):
	if "_chat_surface" in room[selected_room] and (event.button == 4 or event.button == 5):
		rect = room[selected_room]["_chat_surface"].get_rect()
		delta = event.button == 5 and 1 or -1

		room[selected_room]["_chat_scroll"] = max(0, min(
			room[selected_room]["_chat_scroll"] + body_line*delta,
			rect.height - 300
		))

frame_chat.on("mousebuttondown", chat_mousebuttondown)

def chat_keyinput(event):
	global room, selected_room, code, name
	text = textbox_chat.properties["text"]

	surface_chat.fill((0, 0, 0, 0))

	if event and (event.key == 13 or event.key == 271):
		textbox_chat.properties["text"] = ""
		text = name + " : " + text

		room[selected_room]["_chat"].append(text)
		chat_append(selected_room, text)

		# Broadcast the chat to everyone in the room.
		broadcast(selected_room, "DATCHT0" + selected_room + "_" + text)

		text = ""

	d = len(text) > 0

	kuudere.draw(
		surface_chat,
		body,
		(0, 0, 280, 40),
		d and text or "[Chat Here]",
		1,
		d and (0, 0, 0) or (127, 127, 127),
		align=(1, 0.5)
	)

chat_keyinput(None)
textbox_chat.on("keyinput", chat_keyinput)


## Invite Textbox

textbox_invite = kouhai.TextBox({
	"rect": (0, -40, 200, 40),
	"scale_pos": (0, 1)
})

surface_invite = pygame.Surface(
	(180, 40),
	pygame.SRCALPHA
)

def invite_keyinput(event):
	global textbox_invite

	text = textbox_invite.properties["text"]

	surface_invite.fill((0, 0, 0, 0))

	if event and (event.key == 13 or event.key == 271):
		textbox_invite.properties["text"] = ""

		if text not in room:
			addr = socket_encoder.decode(text)

			if addr:
				# Request to join server.
				server.send("REQCON" + name, addr)

		text = ""
	d = len(text) > 0

	kuudere.draw(
		surface_invite,
		body,
		(0, 0, 180, 40),
		d and text or placeholder,
		1,
		d and (0, 0, 0) or (127, 127, 127),
		align=(0, 0.5)
	)

invite_keyinput(None)
textbox_invite.on("keyinput", invite_keyinput)


# Quit

def quit(event):
	global code

	# Tell everybody server is closed.
	broadcast(code, "REQDIS" + code)

	for addr in room:
		if addr != code:
			# Tell servers you are disconnecting.
			server.send("REQDIS", socket_encoder.decode(addr))

	ahoge.close_all()

imouto.on("quit", quit)

# Add to update list.

def update(event):
	imouto.screen.blit(
		surface_info,
		(0, 0)
	)

	imouto.screen.blit(
		surface_invite,
		(10, imouto.rect.height-40)
	)

	imouto.screen.blit(
		surface_chat,
		(imouto.rect.width - 290, imouto.rect.height - 40)
	)

	if surface_room:
		imouto.screen.blit(
			surface_room,
			(10, imouto.rect.height-340)
		)

	if surface_player:
		imouto.screen.blit(
			surface_player,
			(imouto.rect.width - 190, 0)
		)

	if "_chat_surface" in room[selected_room]:
		if room[selected_room]["_chat_scroll_delta"] != room[selected_room]["_chat_scroll"]:
			room[selected_room]["_chat_scroll_delta"] = math.ceil((
				room[selected_room]["_chat_scroll_delta"] +
				room[selected_room]["_chat_scroll"]
			)/2)

		imouto.screen.blit(
			room[selected_room]["_chat_surface"],
			(imouto.rect.width - 290, imouto.rect.height - 340),
			(0, room[selected_room]["_chat_scroll_delta"], 280, 300)
		)

imouto.on("update", update)

# Make listeners for the chat interface.
chat.load()