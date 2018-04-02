import pygame, threading

import asset.api.SenPy as senpai
ahoge = senpai.remote["ahoge"]
imouto = senpai.remote["imouto"]

import asset.ext.socket_encoder as socket_encoder

server, code, code2 = None, None, None
rooms = {
	"global": ["Global", ""]
}

def get(room, code=0):
	i = 1
	n = 0

	if "\\" not in room[i:]:
		return

	if code:
		if code not in room:
			return

		i = room.index(code)

	n = room.find("\\", room.index("\\", i) + 1)

	if n == -1:
		n = None

	return room[i-1:n]

def success(addr):
	global rooms

	server.send("1global" + rooms["global"][1], addr)

	for k in rooms.copy():
		if k != "global" and k[0] != "0":
			server.send("3" + k + "\\" + rooms[k][0], addr)

			v = get(rooms[k][1])

			if v:
				server.send("1" + k + get(rooms[k][1]), addr)

def disconnected(addr):
	global rooms
	code = socket_encoder.encode(addr, 0)

	for k in rooms.copy():
		v = get(rooms[k][1], code)
		if v:
			i = rooms[k][1].index(v)
			rooms[k][1] = rooms[k][1][:i] + rooms[k][1][i+len(v):]

			if k != "global" and not rooms[k][1]:
				del rooms[k]

def received(addr, data):
	global rooms
	data = data.decode("utf-8")

	i = data[:1]
	data = data[1:]

	if i == "1": # Data Player
		sep = data.index("\\")
		i = data[:sep]

		if i not in rooms:
			rooms[i] = ["Untitled Room", ""]

		target = None
		for v in data[sep+1:].split("\\"):
			if target:
				if target not in rooms["global"][1]:
					server.connect(socket_encoder.decode(target, 0))

				rooms[i][1] += "\\" + target + "\\" + v
				target = None
			elif target == None:
				if "\\" + v in rooms[i][1]:
					target = 0
				else:
					target = v
			else:
				target = None
	elif i == "2": # Data Disconnect
		pass
	elif i == "3": # Data Room
		# A room creation request.
		i = None
		for v in data.split("\\"):
			if i:
				if i in rooms:
					rooms[i][0] = v
				else:
					rooms[i] = [v, ""]

				i = None
			else:
				i = v

def set_server(addr):
	global server, code, code2
	server = ahoge.stream(addr)
	code = socket_encoder.encode(server.addr)
	code2 = socket_encoder.encode(server.addr, 0)
	rooms["global"][1] += "\\" + code2 + "\\"

	server.on("success", success)
	server.on("connected", success)
	server.on("disconnected", disconnected)
	server.on("received", received)

	print("SERVER INIT", addr, code, code2)

imouto.screen.fill((0, 0, 0, 0))

def quit(event):
	ahoge.close_all()

imouto.on("quit", quit)