''' Variables
		addr = The address.
			('127.0.0.1', 6000)

		code = An address encoded by the socket_encoder.
			('127.0.0.1', 6000) = 32yvqix8dc0

		id = A unique number given to a room.
			0 = 2-User Room
			1~= Multi-User Room

		room = A combination of a unique ID number and a code.
			id = 1; addr = ('127.0.0.1', 6000) = 32yvqix8dc0
			132yvqix8dc0

		name = The given name by the client when connecting.
			This is given the client itself.

	Room Protocol
		global = Global Room
		0[code] = 2-User Room
		[1 to ...][code] = Multi-User Room

	Data Protocol
		0[room]\[text]
			A chat message to be added in a room. Does nothing
			if the room doesn't exist.

		1[room]\[addr1]\[name1]\[addr2]\[name2]...
			A list of players to be added to a room. This will also
			creates a room if it doesn't exist.

		2[room]\[addr1]\[name1]\[addr2]\[name2]...
			A list of players to be removed from a room. Does nothing
			if the room doesn't exist.

		3[room1]\[name1]\[room2]\[name2]...
			A request to create a room with the specified id and name.

		4[room]\[password]
			A request to join a private room. [name] is the
			requester's name.

		5[name]\[file]
			A file transfered. The name also includes the
			extension.
'''
import pygame, re, math, tkinter, os, threading, time
import asset.ext.socket_encoder as socket_encoder
import asset.ext.room as room
from tkinter import filedialog

# Hide tkinter window.
tkinter.Tk().withdraw()

import asset.api.SenPy as senpai
ahoge = senpai.remote["ahoge"]
kouhai = senpai.remote["kouhai"]
imouto = senpai.remote["imouto"]
kuudere = senpai.remote["kuudere"]

# Server Init
server = ahoge.stream((ahoge.ip, 0))
code = socket_encoder.encode(server.addr)
code2 = socket_encoder.encode(server.addr, 0)
selected_room = "global"
rooms = {
	"global": room.Room("global", "Global")
}
room_id = 1
name = ""

# Set server.
room.set_server(server)

# Font
header = kuudere.get("segoe ui", 24, False, True)
body = kuudere.get("calibri", 18, False)
body_line = body.get_linesize() + 10

# Image
img_bg = pygame.image.load("asset/img/bg.png")
img_highlight = pygame.image.load("asset/img/highlight.png")
img_lock = pygame.image.load("asset/img/lock.png")

placeholder = "[Invite Code Here]"


# Create an auto-connection with a specified server.

def _loop():
	global server
	dedi = ("127.0.0.1", 6000)

	while not imouto.closed:
		try:
			if not server.has(dedi):
				server.connect(dedi)
		except:
			pass

		time.sleep(5)

threading.Thread(
	target = _loop
).start()

# Update

def draw():
	imouto.screen.blit(img_bg, (0, 0))

	imouto.screen.blit(
		surface_info,
		(0, 0)
	)

	imouto.screen.blit(
		chat_surface,
		(210, 570)
	)

	if room_surface:
		imouto.screen.blit(
			room_surface,
			(0, 270)
		)

	v = rooms[selected_room]

	if v.player_surface:
		imouto.screen.blit(
			v.player_surface,
			(600, 0)
		)

	if v.chat_surface:
		if v.chat_scroll_delta != v.chat_scroll:
			v.chat_scroll_delta = math.ceil((
				v.chat_scroll_delta +
				v.chat_scroll
			)/2)

		imouto.screen.blit(
			v.chat_surface,
			(210,
			10 + max(0, 570 - v.chat_surface.get_rect().height)),
			(0, v.chat_scroll_delta, 380, 560)
		)


# Server

def success(addr):
	# Successfully connected to a server.
	global name, rooms, code2

	server.send("1global" + rooms["global"].players, addr)

	if room.cache:
		cache = room.cache[1:]
		server.send("3" + cache, addr)

		i = 0
		for v in cache.split("\\"):
			i = (i+1)%2

			if i:
				server.send(
					"1" + v + "\\" + code2 + "\\" + name,
					addr
				)

server.on("success", success)
server.on("connected", success)

def disconnected(addr):
	global rooms
	i = socket_encoder.encode(addr, 0)

	for k in rooms:
		if rooms[k].has(addr):
			v = rooms[k].get(addr)
			rooms[k].chat(
				v and (
					"'" + rooms[k].get(addr) +
					"' has disconnected."
				) or (
					"Disconnected from dedicated server '" +
					str(addr) + "'."
				)
			)

		rooms[k].rem(addr)
		rooms[k].update()

	draw()

server.on("disconnected", disconnected)

def received(addr, data):
	global name, code
	i = data[:1].decode("utf-8")
	data = data[1:]

	if i != "5":
		data = data.decode("utf-8")

	if i == "0": # Data Chat
		sep = data.index("\\")
		i = data[:sep]
		text = data[sep+1:]

		if i[0] == "0":
			i = "0" + socket_encoder.encode(addr, 0)

		if i in rooms:
			rooms[i].chat(text)

			if not rooms[i].visible:
				rooms[i].visible = True

				room_update()

			draw()
	elif i == "1": # Data Player
		sep = data.index("\\")
		i = data[:sep]

		if i[0] == "0":
			i = "0" + socket_encoder.encode(addr, 0)

		if i not in rooms:
			rooms[i] = room.Room(i)

		target = None
		for v in data[sep+1:].split("\\"):
			if target:
				if not rooms["global"].has(target):
					server.connect(target)

				rooms[i].add(target, v)

				if i == "global":
					rooms[i].chat(
						v and ("Connected with '" + v + "'.") or
						(
							"Connected to dedicated server '" +
							str(addr) + "'."
						)
					)

				target = None
			elif target == None:
				v = socket_encoder.decode(v, 0)

				if rooms[i].has(v):
					target = 0
				else:
					target = v
			else:
				target = None

		rooms[i].update()
		room_update()
		draw()
	elif i == "2": # Data Disconnect
		pass
	elif i == "3": # Data Room
		# A room creation request.
		i = None
		for v in data.split("\\"):
			if i:
				if i in rooms:
					rooms[i].rename(v)
				else:
					rooms[i] = room.Room(i, v)

				i = None
			else:
				if v[0] == "0":
					v = "0" + socket_encoder.encode(addr, 0)

				i = v

		room_update()
	elif i == "4": # Data Password
		sep = data.index("\\")
		i = data[:sep]
		data = data[sep+1:]

		if i in rooms:
			if rooms[i].has(addr):
				# Update password.
				rooms[i].password = data
			elif rooms[i].password == "" or rooms[i].password == data:
				# Someone wants to join.
				id = socket_encoder.encode(addr, 0)
				v = rooms["global"].get(addr)

				# Add him.
				rooms[i].add(addr, v)
				# Give him the full player list.
				server.send(
					"1" + i + rooms[i].players,
					addr
				)
				# Tell him that the password was correct.
				server.send(
					"4" + i + "\\" + (rooms[i].password or ""),
					addr
				)
				# Tell everybody a new user joined.
				rooms[i].broadcast(
					"1" + i + "\\" + id + "\\" + v
				)
				rooms[i].broadcast(
					"0" + i + "\\'" + v + "' has joined.",
					1
				)
				rooms[i].chat("'" + v + "' has joined.")
				rooms[i].update()
	elif i == "5": # Data File
		sep = data.index(b"\\")
		i = data[:sep].decode("utf-8")
		data = data[sep+1:]

		if not os.path.exists("download"):
			os.makedirs("download")

		file = open("download\\" + i, "wb")
		file.write(data)
		file.close()

server.on("received", received)

# Info Surface (Top-left Corner)

surface_info = None

def write(v, pos=(0, 0)):
	global surface_info

	image = body.render(
		v,
		True,
		(255, 255, 255)
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
			max(rect.right + pos[0], rect1.right),
			max(rect.bottom + pos[1], rect1.bottom)
		), pygame.SRCALPHA)

		draft.blit(surface_info, (0, 0))

		surface_info = draft

	surface_info.blit(image, pos)

def set_name(v):
	global code, room, server, name

	# Set name.
	name = v
	rooms["global"].add(server.addr, v)
	rooms["global"].update()

	write("Name: " + v,
		(10, 8 + 60)
	)

	room_update()

write(
	"Invite: " + code,
	(10, 8 + 30)
)
write(
	server.addr[0] + ":" + str(server.addr[1]),
	(10, 8)
)


# Room System

## Player List

player_frame = kouhai.Frame({
	"rect": (600, 0, 200, 600)
})

def player_mousebuttondown(event):
	global rooms, selected_room, chatbox, code2, name
	i = int(event.pos[1]/30) + rooms[selected_room].player_scroll

	addr2, name2 = rooms[selected_room].get(i)

	if addr2 and addr2 != server.addr:
		i = "0" + socket_encoder.encode(addr2, 0)

		if i in rooms:
			rooms[i].visible = not rooms[i].visible
		else:
			rooms[i] = room.Room(i, name2)
			rooms[i].add(server.addr, name)
			rooms[i].add(addr2, name2)
			rooms[i].update()

			server.send("1" + i + rooms[i].players, addr2)
			server.send(
				"30" + code2 + "\\" + name,
				addr2
			)

		selected_room = i
		room_update()

player_frame.on("mousebuttondown", player_mousebuttondown)

## Room List

room_scroll = 0
room_scroll_delta = 0
room_frame = kouhai.Frame({
	"rect": (0, 270, 200, 330)
})
room_surface = None

def room_mousebuttondown(event):
	global rooms, selected_room

	i = int((event.pos[1] - 270)/30) + room_scroll

	if i < len(rooms):
		n = 0
		# Find the room with the corresponding index.
		for k in rooms:
			if rooms[k].visible and len(rooms[k].players) > 0:
				if i == n:
					selected_room = k
					room_update()
					break

				n += 1

room_frame.on("mousebuttondown", room_mousebuttondown)

def room_update():
	global rooms, room_surface, selected_room

	room_surface = pygame.Surface(
		(200, len(rooms)*30 + 5),
		pygame.SRCALPHA
	)

	i = 0
	for k in rooms:
		if rooms[k].visible and len(rooms[k].players) > 0:
			if selected_room == k:
				room_surface.blit(
					img_highlight,
					(-5, i*30 - 5)
				)

			room_surface.blit(
				body.render(
					rooms[k].name,
					True,
					(255, 255, 255)
				),
				(10, i*30 + 8)
			)

			if not rooms[k].has(server.addr):
				room_surface.blit(
					img_lock,
					(175, i*30 + 5)
				)

			i += 1

	draw()


## Chatbox

chat_frame = kouhai.Frame({
	"rect": (200, 0, 400, 570)
})

chat_textbox = kouhai.TextBox({
	"rect": (200, 570, 400, 30)
})

chat_surface = pygame.Surface(
	(380, 30),
	pygame.SRCALPHA
)

def chat_mousebuttondown(event):
	if rooms[selected_room].chat_surface and (event.button == 4 or event.button == 5):
		rect = rooms[selected_room].chat_surface.get_rect()
		delta = event.button == 5 and 1 or -1

		rooms[selected_room].chat_scroll = max(0, min(
			rooms[selected_room].chat_scroll + body_line*delta,
			rect.height - 570
		))

		draw()

chat_frame.on("mousebuttondown", chat_mousebuttondown)

def chat_keyinput(event):
	global room_id, room, selected_room, code2, name
	text = chat_textbox.properties["text"]

	chat_surface.fill((0, 0, 0, 0))

	if event and (event.key == 13 or event.key == 271) and len(text) > 0:
		chat_textbox.properties["text"] = ""

		if text[:5] == "/help" or text[:9] == "/commands":
			# Check the commands.
			rooms[selected_room].chat("/invite [Invite Code]")
			rooms[selected_room].chat(
				"- Invite someone in the currently selected room. " +
				"If you invite someone on the 'Global' room, they " +
				"will be connected to the server. This bypasses " +
				"the room's password."
			)
		elif text[:8] == "/invite ":
			# Invite someone in the currently selected room.
			# If 'Global' room is selected, invites the
			# user to the dynamic server. This also bypasses
			# passwords.
			addr = socket_encoder.decode(text[8:])

			if addr:
				if selected_room == "global":
					server.connect(addr)
				else:
					if selected_room[0] == "0":
						return rooms[selected_room].chat(
							"You can't invite someone here!"
						)

					if not rooms["global"].has(addr):
						return rooms[selected_room].chat(
							"That person isn't in the server :("
						)

					if not rooms["global"].get(addr):
						return rooms[selected_room].chat(
							"You can't invite dedicated servers!"
						)

					if not rooms[selected_room].has(server.addr):
						return rooms[selected_room].chat(
							"You don't have access to this room!"
						)

					i = rooms["global"].get(addr)

					# Add him.
					rooms[selected_room].add(addr, i)
					rooms[selected_room].update()

					# Send him the player list and room name.
					server.send(
						"3" + selected_room + "\\" +
						rooms[selected_room].name,
						addr
					)
					server.send(
						"1" + selected_room +
						rooms[selected_room].players,
						addr
					)

					# Tell everybody a new guy joined.
					rooms[selected_room].broadcast(
						"1" + selected_room + "\\" + i
					)
					rooms[selected_room].broadcast(
						"0" + selected_room + "\\'" + name +
						"' has invited '" + i + "'.",
						1
					)
			else:
				rooms[selected_room].chat(
					"There seems to be something wrong " +
					"with your invite code..."
				)
		elif text[:5] == "/join":
			# Send a request to join a public room.
			if not rooms[selected_room].has(server.addr):
				rooms[selected_room].broadcast(
					"4" + selected_room + "\\" + text[6:],
					1
				)
			else:
				rooms[selected_room].chat(
					"You're already in this room!"
				)
		elif text[:6] == "/host ":
			# Host a room. Everybody can see this room but
			# cannot see the chat. They have to join the room
			# with the right password to see it. Providing no
			# password will not allow anyone to join unless
			# invited.
			text = text[6:]
			pw = None

			if " " in text:
				# A password was provided.
				sep = text.index(" ")
				pw = text[sep+1:] or None
				text = text[:sep]

			if len(text) > 0 and "\\" not in text and (not pw or (" " not in pw and "\\" not in pw)):
				id = str(room_id) + code2
				rooms[id] = room.Room(id, text)
				rooms[id].password = pw

				rooms[id].add(server.addr, name)
				rooms[id].update()
				room_update()

				# Broadcast the room id and the player.
				rooms["global"].broadcast("3" + id + "\\" + text)
				rooms["global"].broadcast(
					"1" + id + "\\" +
					code2 + "\\" + name
				)

				room_id += 1
		elif text[:5] == "/send":
			# Make the user select a file.
			file = filedialog.askopenfile()

			if file:
				# Get the path.
				i = file.name

				# Close that file.
				file.close()

				# Read it again, but in binary.
				file = open(i, "rb")
				i = b"5" + os.path.basename(file.name).encode("utf-8") + b"\\" + file.read()

				# Close it.
				file.close()

				# Send a broadcast across the room.
				rooms[selected_room].broadcast(i, 1)
		elif rooms[selected_room].has(server.addr):
			# Chat in your selected room.
			text = name + " : " + text

			rooms[selected_room].chat(text)
			rooms[selected_room].broadcast(
				"0" + selected_room + "\\" + text,
				1
			)

		text = ""

	d = len(text) > 0

	kuudere.draw(
		chat_surface,
		body,
		(0, 0, 380, 30),
		d and text or "[Chat Here]",
		1,
		d and (191, 191, 191) or (127, 127, 127),
		align=(0, 0.5)
	)
	draw()

chat_keyinput(None)
chat_textbox.on("keyinput", chat_keyinput)


# Quit

def quit(event):
	ahoge.close_all()

imouto.on("quit", quit)

draw()