''' Networking Goddess.

	TCP-based.

	A portable server+client object 'Stream' that can only connect
	with the same object, otherwise would cause complications.

	The system makes use of the 10000-byte character as a separator
	between each data to segregate the streams.

	Makes use of a pseudo-handshake system to finish name requests
	and connection integrity.

	.stream((ip, port))
		Creates a server+client object 'Stream' that works both ways.
		ALl incoming connections will use the server's address.

		Functions
			.on(channel, callback)
				Creates a listener on the given channel.
				Returns a 'Listener' object.

				listener.disconnect()
					Disconnects the listener.

					Example;
						def connect(addr):
							print(addr)

						listener = stream.on("connected", connect)
						listener.disconnect()

				Example;
					def connect(addr):
						print(addr)

					stream.on("connected", connect)

			.send(data)
				Sends a stream of data. Automatically converts
				the data to a binary string.

				Example;
					stream.send("hello")

			.close()
				Closes the stream.

		Events
			"connected", (address)
				Fires when a client has connected to your server.
				The address is the client's server address (note
				that the client uses a new address to connect to
				you, which is not their server.)

			"success", (address)
				Fires when you have successfully connected to
				a server.

			"received", (address, data)
				Fires when a data is received from the clients.
				The data is automatically decoded to a regular
				string.

			"timeout", (address)
				Fires when a connection attempt has timed-out, which
				is done after 5 seconds of not receiving confirmation.
				The address is the one that you are trying to
				connect to.

			"failed", (address)
				Fires when a connection is explicitly disconnected
				before the pseudo-handshake system. This happens
				when a similar connection is already established.
				The address is the one that you are trying to connect
				to.

			"disconnected", (address)
				Fires when the client has disconnected. The address
				is the one that you are trying to connect to.

			"closed", ()
				Fires when the server is closed (stream.close()
				was called).

	.close_all()
		Closes all streams (calls the stream.close() on each stream).
'''

import socket, time, threading, re, math

cache = {}
timeout = 5
eos = chr(10000).encode("utf-8") # End of stream.

def load(senpai):
	moe = senpai.remote["moe"]

	class Stream:
		def __init__(self, sock, buffer=1024):
			# Init
			status = 1
			self.on, fire = moe()
			clients = {}
			queue = []

			self.addr = sock.getsockname()

			# Server Loop

			def recv(conn, addr, reply):
				def callback():
					nonlocal reply

					if reply:
						reply = -1
						conn.close()

				threading.Timer(timeout, callback).start()

				data = b""
				while status and reply > -1:
					try:
						i = conn.recv(1)

						if not i:
							# Received an empty data.
							# Connection closed.
							conn.close()
							break # Stop the loop.

						data += i

						if eos in data:
							# Received a newline character.
							# End of stream.
							data = data[:-3]

							if reply:
								# Handshake first.
								if reply == 2:
									# Server-side.
									data = data.decode("utf-8")
									i = data.index(":")
									addr = (data[:i], int(data[i+1:]))

									if addr in clients:
										conn.close()
										break # Already connected

									clients[addr] = {
										"conn": conn,
										"data": {},
										"header": None,
										"lo": [],
										"hi": 0
									}

									threading.Thread(
										target=fire,
										args=("connected", addr)
									).start()
									print(
										"ahoge.py > Connection",
										"\nTarget:", addr,
										"\nEcho:", data,
										"\n"
									)
								else:
									# Client-side.
									conn.send((
										self.addr[0] + ":" +
										str(self.addr[1])
									).encode("utf-8") + eos)

									threading.Thread(
										target=fire,
										args=("success", addr)
									).start()
									print(
										"ahoge.py > Success",
										"\nTarget:", addr,
										"\n"
									)

								reply = 0
								data = b""
							else:
								# Data received.
								print(
									"ahoge.py > Receiving",
									"\nTarget:", addr,
									"\nPayload:", len(data)
								)

								if clients[addr]["header"]:
									# Receiving data.
									print("Type: Data\n")

									header = clients[addr]["header"]
									segment = clients[addr]["data"][header[0]]
									segment[int(header[2])] = data

									if len(segment) >= int(header[1]):
										data = b"".join(segment[i] for i in range(int(header[1])))

										fire("received", addr, data)

									clients[addr]["header"] = None
								else:
									# Receiving header.
									print("Type: Header\n")

									data = data.decode("utf-8")
									data = data.split("\\")
									clients[addr]["header"] = data

									if data[0] not in clients[addr]["data"]:
										clients[addr]["data"][data[0]] = {}

								data = b""
					except:
						break

				if reply == -1:
					print(
						"ahoge.py > Timeout",
						"\nTarget:", addr,
						"\n"
					)
					fire("timeout", addr)
				elif reply:
					print(
						"ahoge.py > Failed",
						"\nTarget:", addr,
						"\n"
					)
					fire("failed", addr)
				else:
					del clients[addr]

					print(
						"ahoge.py > Disconnection",
						"\nTarget:", addr,
						"\n"
					)
					fire("disconnected", addr)

				conn.close()

			def accept():
				while status:
					try:
						conn, addr = sock.accept()

						threading.Thread(
							target=recv,
							args=(conn, addr, 2)
						).start()

						conn.send(eos) # Send confirmation.
					except:
						break

				print("ahoge.py > Closed\n")
				fire("closed")

			threading.Thread(target=accept).start()

			# Receiver Loop

			def connect(addr):
				print(
					"ahoge.py > Connecting...",
					"\nTarget:", addr
				)
				if addr in clients or addr == self.addr:
					print("Status: Exists\n")
					return True

				print("Status: Connecting\n")

				try:
					conn = socket.socket(
						socket.AF_INET,
						socket.SOCK_STREAM
					)
					clients[addr] = {
						"conn": conn,
						"data": {},
						"header": None,
						"lo": [],
						"hi": 0
					}

					threading.Thread(
						target=conn.connect,
						args=(addr, )
					).start()
					threading.Thread(
						target=recv,
						args=(conn, addr, 1)
					).start()

					return True
				except:
					return False

			def disconnect(addr):
				if addr in clients:
					clients[addr]["conn"].close()

			def session(data, addr, id):
				conn = clients[addr]["conn"]

				# Setup buffer. Make space for the 'eos'.
				buffer = self.buffer - len(eos)

				# Get how many segments.
				i = len(data)//buffer + (len(data)%buffer and 1)

				# Create the header.
				header = str(id).encode("utf-8") + b"\\" + str(i).encode("utf-8") + b"\\"

				print(
					"ahoge.py > Session",
					"\nTarget:", addr,
					"\nBuffer:", buffer,
					"\nHeader:", header,
					"\nPayload:", len(data)
				)

				for n in range(i):
					# Send the header. id\index\total(eos)
					conn.send(header + str(n).encode("utf-8") + eos)

					# Send the segment.
					conn.send(data[:buffer] + eos)

					# Reduce the payload.
					data = data[buffer:]
					print("Payload:", len(data))

				print("Payload: EOS\n")

				if id == clients[addr]["hi"] - 1:
					clients[addr]["hi"] -= 1
				else:
					clients[addr]["lo"].append(id)

			def send(data, addr=None):
				if not addr:
					for addr in clients:
						send(data, addr)

					return True

				if addr in clients:
					conn = clients[addr]["conn"]
					data = type(data) != bytes and data.encode("utf-8") or data
					id = clients[addr]["hi"]

					# Find the next suitable ID for other sessions.
					if len(clients[addr]["lo"]):
						# If there are still available IDs previously.
						id = clients[addr]["lo"][0]
						clients[addr]["lo"].pop(0)
					else:
						# If there are no available IDs previously.
						clients[addr]["hi"] += 1

					threading.Thread(
						target=session,
						args=(data, addr, id)
					).start()

				return False

			def close():
				nonlocal status
				status = 0

				for addr in clients.copy():
					clients[addr]["conn"].close()

				sock.close()

			self.buffer = buffer
			self.send = send
			self.connect = connect
			self.disconnect = disconnect
			self.close = close

	class this:
		ip = socket.gethostbyname(socket.gethostname())

		def stream(addr):
			global cache

			if addr not in cache or addr[1] == 0:
				sock = socket.socket(
					socket.AF_INET,
					socket.SOCK_STREAM
				)

				sock.bind(addr)
				sock.listen(5)

				addr = sock.getsockname()
				cache[addr] = Stream(sock)

			return cache[addr]

		def close_all():
			global cache

			# Create a copy since closing streams also updates the list.
			list = cache.copy()

			# Close everything.
			for addr in list:
				cache[addr].close()

			# Make a fresh list.
			cache = {}

	this.Stream = Stream

	return this