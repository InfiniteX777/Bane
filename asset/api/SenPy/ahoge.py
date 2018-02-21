''' Networking Goddess.

	TCP-based.

	A portable server+client object 'Stream' that can only connect
	with the same object, otherwise would cause complications.

	The system makes use of the newline character '\n' as a separator
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

import socket, time, threading, re

cache = {}
buffer = 1024
timeout = 5

def load(senpai):
	moe = senpai.remote["moe"]

	class Stream:
		def __init__(self, sock):
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

				while status and reply > -1:
					try:
						data = conn.recv(buffer).decode("utf-8")[:-1]
						print("received", data, len(data))

						for data in re.split("\n", data):
							if len(data) == 0:
								conn.close()

								break # Stop the loop.
							elif reply:
								if reply == 2:
									i = data.index(":")
									addr = (data[:i], int(data[i+1:]))

									if addr in clients:
										conn.close()

										break # Already connected.

									clients[addr] = conn

									fire("connected", addr)
									print("connected", addr, data)
								else:
									conn.send((
										self.addr[0] + ":" +
										str(self.addr[1]) + "\n"
									).encode("utf-8"))

									fire("success", addr)
									print("success", addr)

								reply = 0
							else:
								fire("received", addr, data)
					except:
						break

				if reply == -1:
					print("timeout", addr)
					fire("timeout", addr)
				elif reply:
					print("failed", addr)
					fire("failed", addr)
				else:
					del clients[addr]

					print("disconnected", addr)
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

						conn.send(b' \n') # Send confirmation.
					except:
						break

				print("closed")
				fire("closed")

			threading.Thread(target=accept).start()

			# Receiver Loop

			def connect(addr):
				if addr in clients or addr == self.addr:
					print("connection to", addr, "already exists.")
					return True

				print("connecting to", addr)

				try:
					conn = socket.socket(
						socket.AF_INET,
						socket.SOCK_STREAM
					)
					clients[addr] = conn

					conn.connect(addr)
					threading.Thread(
						target=recv,
						args=(conn, addr, 1)
					).start()

					return True
				except:
					return False

			def disconnect(addr):
				if addr in clients:
					clients[addr].close()

			def send(data, addr=None):
				if not addr:
					for addr in clients:
						send(data, addr)

					return True

				if addr in clients:
					conn = clients[addr]
					data = type(data) != bytes and data.encode("utf-8") or data
					data += b'\n'

					print("send", data)
					conn.send(data)

				return False

			def close():
				nonlocal status
				status = 0

				for addr in clients.copy():
					clients[addr].close()

				sock.close()

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