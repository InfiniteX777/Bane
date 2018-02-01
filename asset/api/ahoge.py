import socket
import _thread as thread

# Globals

cache_stream = []
cache_client = {
	"all": [] # Listener for all connections.
}
ip = socket.gethostbyname(socket.gethostname())


# Client

''' Start a stream between you and the target
	address.
'''
class stream:
	# -1 = closed; 0 = pending; 1 = connected
	status = 0
	listener = []

	def __init__(self, ip, port, buffer=1024):
		try:
			self.ip = ip
			self.port = port
			self.buffer = buffer
			self.sock = socket.socket(
				socket.AF_INET,
				socket.SOCK_STREAM
			)

			# Connect the socket to the target.
			self.sock.connect((ip, port))
			cache_stream.append(self)

			# Set status to 'connected'.
			self.status = 1

			# Start thread.
			thread.start_new_thread(self._recv_loop, ())
		except:
			# Failed.
			self.status = -1

	# Send data to the other address.
	def send(self, data):
		try:
			self.sock.send(data.encode('utf-8'))
		except:
			self.status = -1

	''' Create a listener for the stream. Returns
		a function that will disconnect the listener
		when fired.
	'''
	def on_recv(self, callback):
		self.listener.append(callback)

		def disconnect():
			self.listener.remove(callback)

		return disconnect

	# Close the stream.
	def close(self):
		self.sock.close()
		cache_stream.remove(self)
		self.status = -1

	# Receive data from the target.
	def _recv_loop(self):
		while self.status == 1:
			try:
				data = self.sock.recv(self.buffer).decode("utf-8")
				for callback in self.listener:
					callback(data)
			except:
				self.status = -1

# Closes all existing streams.
def close_all():
	global cache_stream

	for v in cache_stream:
		v.close()

	cache_stream = []


# Server

server = None

# Sends to all connected streams.
def broadcast(data):
	for addr in cache_client:
		if addr != "all":
			cache_client[addr]["sock"].send(data.encode("utf-8"))

''' Creates a listener that will fire when data is
	received from the specified addresses. If there
	are no given addresses, it will fire whenever
	a data is received from anyone.

	callback(sock, addr, data)

	Example;
		server_recv(
			callback,
			(192.168.1.1, 1024),
			(100.100.1.1, 5005),
			...
		)
'''
def on_recv(callback, *tuple):
	if len(tuple) > 0:
		for v in tuple:
			if v in cache_client:
				cache_client[v]["listener"].append(callback)
	else:
		# Append to 'all'.
		cache_client["all"].append(callback)

# Intercepts data being sent from each streams.
def _server_intercept(sock, addr):
	while addr in cache_client:
		try:
			client = cache_client[addr]
			data = sock.recv(client["buffer"]).decode("utf-8")

			# Send to all listeners associated.
			for callback in cache_client["all"]:
				callback(sock, addr, data)

			for callback in client["listener"]:
				callback(sock, addr, data)
		except:
			cache_client.pop(addr)

''' A loop for server transmission. Will stop if server
	is closed.
'''
def _server_loop():
	while server:
		# Wait for any incoming connections.
		sock, addr = server.accept()

		# Cache the connection.
		cache_client[addr] = {
			"sock": sock,
			"buffer": 1024,
			"listener": []
		}

		# Start a thread for the connection.
		thread.start_new_thread(
			_server_intercept,
			(sock, addr)
		)

# Starts your server.
def server_start(ip, port):
	global server

	server = socket.socket(
		socket.AF_INET,
		socket.SOCK_STREAM
	)

	server.bind((ip, port))
	server.listen(5)

	thread.start_new_thread(_server_loop, ())