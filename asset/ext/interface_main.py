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
import asset.ext.game as game
from tkinter import filedialog

# Hide tkinter window.
tkinter.Tk().withdraw()

import asset.api.SenPy as senpai
ahoge = senpai.remote["ahoge"]
kouhai = senpai.remote["kouhai"]
imouto = senpai.remote["imouto"]
kuudere = senpai.remote["kuudere"]

# Font
header = kuudere.get("segoe ui", 14, False)
body = kuudere.get("calibri", 13, False)
body_line = body.get_linesize()

# Image
img_bg = pygame.image.load("asset/img/bg.png")
img_bg_chatbox = pygame.image.load("asset/img/bg_chatbox.png")
img_players = pygame.image.load("asset/img/players.png")
img_rooms = pygame.image.load("asset/img/rooms.png")
img_lock = pygame.image.load("asset/img/lock.png")

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

# Set servers to the other modules.
game.server = room.server = server
game.code = code

# Set background color.
imouto.background = (63, 63, 63)

# Create an auto-connection with a specified server.
dedicated_loop = None

# A loop to ensure that the players are automatically connected
# to a server that is specifically hard-coded. This will not stop
# until the application is closed.
def _loop():
	global server, dedicated_loop
	dedi = ("127.0.0.1", 6000)

	# Catch any errors that may interrupt the loop.
	try:
		# Make sure that the application is not connected yet.
		if not server.has(dedi):
			server.connect(dedi)
	except:
		pass

	# Make sure that the application is still active.
	if not imouto.closed:
		# Start another timer with the same function.
		dedicated_loop = threading.Timer(5, _loop)
		dedicated_loop.start()

# Initiate the loop.
_loop()


# Chatbox

# 0 = None; 1 = Player Selection; 2 = Room Selection;
chatbox_option = 0

# The frame of the chatbox. Used for mouse activity detection.
chatbox_frame = kouhai.Frame({
	"rect": (10, 390, 300, 200),
	# Disable mouse activity. Chatbox is only accessible after
	# pressing the 'enter' button. This will also dictate if the
	# chatbox is enabled or not.
	"active": 0,
	"zindex": 2
})

# Create a textbox with no boundaries. This would mean that the
# textbox can only be focused with 'textbox.set_focus(1)'.
chatbox_textbox = kouhai.TextBox()

# The surface for the frame. This will handle scrolling and
# room/player selection.
chatbox_surface = pygame.Surface(
	(300, 200),
	pygame.SRCALPHA
)

# The surface for the textbox's texts. Since the textbox only updates
# when a button was pressed and requires extensive resources, a
# dedicated surface is a good idea.
chatbox_textbox_surface = pygame.Surface(
	(260, 20),
	pygame.SRCALPHA
)

# The room selection's scroll data. The surface is there as a
# placeholder, and will be replaced with a new one every update.
chatbox_room_scroll = 0
chatbox_room_scroll_delta = 0
chatbox_room_surface = pygame.Surface((1, 1))

def chatbox_draw():
	# Get if the chatbox is focused.
	active = chatbox_textbox.is_focused()

	# Get the currently selected room.
	v = rooms[selected_room]

	if active:
		# Draw the chatbox when it's focused.
		chatbox_surface.fill(
			(0, 0, 0, 191),
			(0, 0, 300, 200)
		)

		chatbox_surface.blit(
			header.render(
				"Room: " + rooms[selected_room].name,
				1,
				(255, 255, 255)
			),
			(4, 2)
		)

		# Draw the buttons and the room/player selection, whichever
		# was toggled.
		if chatbox_option == 1 and v.player_surface:
			chatbox_surface.blit(
				img_players,
				(262, 182),
				(15, 0, 15, 15)
			)
			chatbox_surface.blit(
				img_rooms,
				(282, 182),
				(0, 0, 15, 15)
			)
			chatbox_surface.blit(
				v.player_surface,
				(220, 20),
				(0, v.player_scroll_delta, 80, 160)
			)
		elif chatbox_option == 2:
			chatbox_surface.blit(
				img_players,
				(262, 182),
				(0, 0, 15, 15)
			)
			chatbox_surface.blit(
				img_rooms,
				(282, 182),
				(15, 0, 15, 15)
			)
			chatbox_surface.blit(
				chatbox_room_surface,
				(220, 20),
				(0, 0, 80, 160)
			)
		else:
			chatbox_surface.blit(
				img_players,
				(262, 182),
				(0, 0, 15, 15)
			)
			chatbox_surface.blit(
				img_rooms,
				(282, 182),
				(0, 0, 15, 15)
			)
	else:
		# Draw the chatbox when it's not focused.
		chatbox_surface.fill(
			(0, 0, 0, 0),
			(0, 0, 300, 180)
		)

		chatbox_surface.fill(
			(0, 0, 0, 127),
			(0, 180, 300, 20)
		)

	# Draw the currently selected room's chat.
	if v.chat_surface:
		if v.chat_scroll_delta != v.chat_scroll:
			# Slowly try to match the designated scroll value,
			# producing an easing effect.
			v.chat_scroll_delta = math.ceil((
				v.chat_scroll_delta +
				v.chat_scroll
			)/2)

		chatbox_surface.blit(v.chat_surface, (
			5,
			20 + max(0, 155 - v.chat_surface.get_rect().height)
		), (
			0,
			v.chat_scroll_delta,
			chatbox_option and active and 215 or 290,
			155
		))

	chatbox_surface.blit(
		chatbox_textbox_surface,
		(0, 180)
	)

	imouto.screen.blit(
		chatbox_surface,
		(10, 390)
	)

def chatbox_room_update():
	# Update the room selection's surface (redraw it).
	global chatbox_room_surface
	i = 0
	chatbox_room_surface = pygame.Surface(
		(80, len(rooms)*20),
		pygame.SRCALPHA
	)

	for k in rooms:
		if rooms[k].visible and len(rooms[k].players) > 0:
			img = body.render(
				rooms[k].name,
				True,
				(255, 255, 255)
			)

			if selected_room == k:
				# Draw a white line below the selected room to
				# indicate that it is currently selected.
				chatbox_room_surface.fill(
					(255, 255, 255),
					(
						5,
						i*20 + img.get_height() + 3,
						img.get_width(),
						1
					)
				)

			chatbox_room_surface.blit(
				img,
				(5, i*20 + 5)
			)

			if not rooms[k].has(server.addr):
				# Draw a 'lock' image when the room is inaccessible.
				chatbox_room_surface.blit(
					img_lock,
					(60, i*20)
				)

			i += 1

def chatbox_keydown(event):
	if (event.key == 13 or event.key == 271):
		# Enter key was pressed.
		if chatbox_frame.properties["active"]:
			# Make sure that the user is not trying to chat.
			if not chatbox_textbox.properties["text"]:
				# Disable the chatbox.
				chatbox_frame.properties["active"] = 0

				chatbox_textbox.set_focus(0)
		else:
			# Activate the chatbox!
			chatbox_frame.properties["active"] = 1

			chatbox_textbox.set_focus(1)

imouto.on("keydown", chatbox_keydown)

def chatbox_unfocused():
	if chatbox_frame.properties["active"]:
		# Always force the textbox to be focused when the chatbox
		# is active.
		chatbox_textbox.set_focus(1)

chatbox_textbox.on("unfocused", chatbox_unfocused)

def chatbox_mousebuttondown(event):
	global rooms, selected_room, chatbox_option, code2, name

	# Check if left mouse button.
	if event.button == 1:
		if event.pos[1] > 570:
			# Clicked at the bottom part of the chatbox.
			if event.pos[0] > 290:
				# Clicked the 'room selection' button.
				chatbox_option = chatbox_option != 2 and 2 or 0
			elif event.pos[0] > 270:
				# Clicked the 'player selection' button.
				chatbox_option = chatbox_option != 1 and 1 or 0
		if event.pos[0] > 230 and event.pos[1] > 410:
			# Player is attempting to select a room/player.
			i = int((event.pos[1] - 410)/20)

			if chatbox_option == 1:
				# Player selection.
				i += rooms[selected_room].player_scroll

				# Get the player with the corresponding index.
				addr2, name2 = rooms[selected_room].get(i)

				# Make sure the player is not you!
				if addr2 and addr2 != server.addr:
					i = "0" + socket_encoder.encode(addr2, 0)

					# Create a 1-on-1 chat room session.
					if i in rooms:
						# Toggle the room if it already exists.
						rooms[i].visible = not rooms[i].visible

						if selected_room == i:
							# Switch to global room.
							selected_room = "global"
							chatbox_room_update()
					else:
						rooms[i] = room.Room(i, name2)
						rooms[i].add(server.addr, name)
						rooms[i].add(addr2, name2)
						rooms[i].update()

						# Tell the other user that a room is being
						# created.
						server.send("1" + i + rooms[i].players, addr2)
						server.send(
							"30" + code2 + "\\" + name,
							addr2
						)

						selected_room = i
						chatbox_room_update()
			elif chatbox_option == 2:
				# Room selection.
				i += chatbox_room_scroll
				n = 0

				# Find the room with the corresponding index.
				for k in rooms:
					# Make sure that room is visible and contains
					# players.
					if rooms[k].visible and len(rooms[k].players) > 0:
						if i == n:
							selected_room = k
							chatbox_room_update()
							break

						n += 1
	elif rooms[selected_room].chat_surface and (event.button == 4 or event.button == 5):
		# Mouse wheel (scrolling through the chatbox).
		rect = rooms[selected_room].chat_surface.get_rect()
		delta = event.button == 5 and 1 or -1

		rooms[selected_room].chat_scroll = max(0, min(
			rooms[selected_room].chat_scroll + body_line*delta,
			rect.height - 155
		))

chatbox_frame.on("mousebuttondown", chatbox_mousebuttondown)

def chatbox_keyinput(event):
	global room_id, room, selected_room, code2, name
	text = chatbox_textbox.properties["text"]

	chatbox_surface.fill(
		(0, 0, 0, 191),
		(0, 180, 260, 20)
	)

	# Check if 'enter' key was pressed.
	d = event and (event.key == 13 or event.key == 271)

	if d:
		# Clear the text.
		chatbox_textbox.properties["text"] = ""

	v = chatbox_textbox.properties["text"]

	chatbox_textbox_surface.fill((0, 0, 0, 0))

	kuudere.draw(
		chatbox_textbox_surface,
		body,
		(5, 3, 255, 17),
		v or "Press 'Enter' key to chat.",
		1,
		v and (255, 255, 255) or (127, 127, 127),
		align=(0, 0.5)
	)

	# Check if commands were invoked.
	if not d or not text:
		return

	if text[:5] == "/help" or text[:9] == "/commands":
		# Check the commands.
		rooms[selected_room].chat("/invite [Invite Code]")
		rooms[selected_room].chat(
			"- Invite someone in the currently selected room. " +
			"If you invite someone on the 'Global' room, they " +
			"will be connected to the server. This bypasses " +
			"the room's password."
		)
	elif text[:6] == "/duel ":
		# ITS TIME TO DU-DU-DU-DU-DUEL!
		addr = socket_encoder.decode(text[6:])

		if not addr:
			return rooms[selected_room].chat(
				"The code seems to be incorrect..."
			)
		elif not rooms["global"].has(addr):
			return rooms[selected_room].chat(
				"That player isn't in the server!"
			)

		# FYT ME 1V1 IRL NUB
		server.send("9", addr)
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
					"1" + selected_room + "\\" +
					socket_encoder.encode(addr, 0) + "\\" + i
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

		if (len(text) > 0 and "\\" not in text and
			(not pw or
			 (" " not in pw and "\\" not in pw))):
			id = str(room_id) + code2
			rooms[id] = room.Room(id, text)
			rooms[id].password = pw

			rooms[id].add(server.addr, name)
			rooms[id].update()
			chatbox_room_update()

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
			i = (
				b"5" + os.path.basename(file.name).encode("utf-8") +
				b"\\" + file.read()
			)

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

chatbox_keyinput(None)
chatbox_textbox.on("keyinput", chatbox_keyinput)


# Info Surface (Top-left Corner)

surface_info = pygame.Surface(
	(140, 60),
	pygame.SRCALPHA
)

surface_info.fill((0, 0, 0, 127))
surface_info.blit(
	body.render(
		server.addr[0] + ":" + str(server.addr[1]),
		True,
		(255, 255, 255)
	),
	(5, 5)
)
surface_info.blit(
	body.render(
		"Invite: " + code,
		True,
		(255, 255, 255)
	),
	(5, 25)
)

def set_name(v):
	global code, room, server, name

	# Set name.
	name = v
	rooms["global"].add(server.addr, v)
	rooms["global"].update()

	surface_info.blit(
		body.render(
			"Name: " + v,
			True,
			(255, 255, 255)
		),
		(5, 45)
	)

	chatbox_room_update()


# Listeners

# Connected to a user.
def success(addr):
	global name, rooms, code2

	# Tell him who you are connected with.
	server.send("1global" + rooms["global"].players, addr)

	# See if there are custom rooms that you can tell him.
	if room.cache:
		# Get rid of the 'ghost byte'. It's only for aesthetics.
		cache = room.cache[1:]

		# Send him what custom rooms you know.
		server.send("3" + cache, addr)

		i = 0
		# Get each of the room's names. This is different from
		# the room's 'code', where the 'name' is not a unique ID.
		for v in cache.split("\\"):
			# Format the data.
			i = (i+1)%2

			if i:
				# Give him your ID to tell him that you own these
				# rooms. He'll need to know at least 1 person
				# so someone can verify the password.
				server.send(
					"1" + v + "\\" + code2 + "\\" + name,
					addr
				)

server.on("success", success)
server.on("connected", success)

# A user disconnected from you. This doesn't necessarily mean that
# he disconnected from the other users. Each user has an independent
# connection between users.
def disconnected(addr):
	global rooms
	i = socket_encoder.encode(addr, 0)

	# Check if you are in a game with him.
	if game.active and game.opponent == addr:
		# LUL RAGE QUIT NUB
		game.received(addr, 8, "1")

	# Disconnect him to all of the rooms that he is in.
	for k in rooms:
		if rooms[k].has(addr):
			# Get his name.
			v = rooms[k].get(addr)

			# Post a chat text.
			rooms[k].chat(v and (
				"'" + rooms[k].get(addr) +
				"' has disconnected."
			) or (
				"Disconnected from dedicated server '" +
				str(addr) + "'."
			))

		# Get rid of him.
		rooms[k].rem(addr)
		# Redraw the room's image.
		rooms[k].update()

server.on("disconnected", disconnected)

# Data received. See the topmost portion of this module for more info.
def received(addr, data):
	global name, code

	try:
		# Try to transform the first byte into an integer.
		i = int(data[:1].decode("utf-8"))
		data = data[1:]
	except:
		# First byte isn't an integer. Protocol is not followed
		# properly. Do not continue.
		return

	if i != 5:
		# Files should remain in byte-string for easier translation.
		data = data.decode("utf-8")

	if i > 5 and (game.opponent == addr or i == 9):
		# Protocol related to the game. Let 'game.py' handle it.
		return game.received(addr, i, data)

	if i == 0: # Data Chat
		sep = data.index("\\")
		i = data[:sep]
		text = data[sep+1:]

		if i[0] == "0":
			i = "0" + socket_encoder.encode(addr, 0)

		if i in rooms:
			rooms[i].chat(text)

			if not rooms[i].visible:
				rooms[i].visible = True

				chatbox_room_update()
	elif i == 1: # Data Player
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
		chatbox_room_update()
	elif i == 2: # Data Disconnect
		pass
	elif i == 3: # Data Room
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

		chatbox_room_update()
	elif i == 4: # Data Password
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
	elif i == 5: # Data File
		sep = data.index(b"\\")
		i = data[:sep].decode("utf-8")
		data = data[sep+1:]

		if not os.path.exists("download"):
			os.makedirs("download")

		file = open("download\\" + i, "wb")
		file.write(data)
		file.close()

server.on("received", received)


# Update

def update(dt):
	global surface_info

	imouto.screen.blit(
		img_bg,
		(95, 0),
		(0, 140, 610, 140)
	)
	imouto.screen.blit(
		img_bg,
		(95, 460),
		(0, 0, 610, 140)
	)
	game.draw()
	chatbox_draw()
	imouto.screen.blit(
		surface_info,
		(10, 10)
	)

imouto.on("update", update)


# Quit

def quit(event):
	global dedicated_loop

	ahoge.close_all()
	dedicated_loop.cancel()

imouto.on("quit", quit)