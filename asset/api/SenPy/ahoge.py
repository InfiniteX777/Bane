''' Allows communication through the network.

	.ip
		Your IP.

	.stream(
		ip[String],
		port[Number],
		buffer[Number]=1024
	)
		Creates and returns a 'stream_obj' that
		connects to another address. Will return
		an existing 'stream_obj' if there is
		already one.

	stream_obj
		A stream.

		.status=0
			Current status of the stream.
			-1 = Disconnected
			0 = Pending
			1 = Connected

		.send(data[bString])
			Sends data to the other end of the
			stream.

		.on_recv(callback[Function(
			data[bString]
		)])
			Creates a listener that fires
			whenever data is received from the
			other end. Returns a function that
			when called will disconnect the
			listener.

		.close()
			Closes the stream.

	.close_all()
		Closes all existing streams.

	.broadcast(data[bString])
		Sends data to all existing streams.

	.on_recv(
		callback[Function(
			sock[socket],
			addr[(ip[String], port[Number])],
			data[bString]
		)],
		*tuple[
			(ip[String], port[Number])
		]
	)
		Creates a listener that fires whenever
		data is received from the given
		addresses. If there are no provided
		addresses, it will fire from any
		data received.

	.server_start(
		ip[String],
		port[Number]
	)
		Starts the server and binds to the given
		address.
'''

import socket
import _thread as thread

# Globals

cache_stream = {}
cache_client = {
	"all": [] # Listener for all connections.
}

# Private

class Stream:
	def __init__(self, ip, port, buffer=1024):
		# Init
		self.listener = []

		self.buffer = buffer
		self.sock = socket.socket(
			socket.AF_INET,
			socket.SOCK_DGRAM
		)

		# Setup socket.
		self.sock.bind((ip, port))
		# Get the socket's name.
		self.addr = self.sock.getsockname()
		# Set status.
		self.status = 1

		cache_stream[self.addr] = self

		# Start thread.
		thread.start_new_thread(self._recv_loop, ())

	def send(self, data, addr, persist=False):
		persist = persist and -1 or 1

		while persist != 0:
			try:
				self.sock.sendto(
					data.encode('utf-8'),
					addr
				)

				persist = 0
			except:
				print(persist)
				persist -= 1

	def on_recv(self, callback):
		self.listener.append(callback)

		def disconnect():
			self.listener.remove(callback)

		return disconnect

	def close(self):
		self.status = -1
		cache_stream.pop(self.addr, None)
		self.sock.close()

	# Receive data from the target.
	def _recv_loop(self):
		while self.status == 1:
			try:
				data, addr = self.sock.recvfrom(self.buffer)
				data = data.decode("utf-8")
				list = self.listener.copy()

				for callback in list:
					try:
						callback(data, addr)
					except:
						self.listener.remove(callback)
			except:
				pass

class this:
	ip = socket.gethostbyname(socket.gethostname())

	def stream(ip, port, buffer=1024):
		if (ip, port) in cache_stream:
			# Return the existing stream.
			return cache_stream[(ip, port)]
		else:
			# Create a new stream.
			return Stream(ip, port, buffer)

	def close_all():
		global cache_stream

		# Create a copy since closing streams also updates the dict.
		list = cache_stream.copy()

		# Close everything.
		for addr in list:
			cache_stream[addr].close()

		# Make a fresh list.
		cache_stream = {}

def load(senpai):

	return this