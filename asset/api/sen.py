import sys, pygame, time
import asset.api.ahoge as ahoge

pygame.init()

# Renderer Properties
speed = 1
tick = time.time()
size = width, height = 320, 240
option = pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE
background = 0, 0 ,0
screen = pygame.display.set_mode((320, 240), option)

# Event Handling
listener = {
	"on": {
		"update": []
	},
	"once": {}
}
timeout_list = []

''' Make senpai wait for the right moment to
	execute his attack!
'''
def timeout(callback, t, *tuple):
	con = {
		"callback": callback,
		"t": t,
		"arg": tuple,
		"fin": False
	}

	timeout_list.append(con)

	return con

# Make senpai notice that channel.
def fire(channel, *tuple):
	if channel in listener["on"]:
		for v in listener["on"][channel]:
			if v.delay > 0:
				if v.con:
					if v.con["fin"]:
						v.pop()
				else:
					v.push(timeout(v.callback, v.delay, *tuple))
			else:
				v.callback(*tuple)

	if channel in listener["once"]:
		for v in listener["once"][channel]:
			v(*tuple)

		listener["once"].pop(channel, None)

''' Create a listener that will hopefully be
	be noticed by senpai.
'''
class on:
	con = None

	def __init__(self, channel, callback, delay=0):
		self.channel, self.callback, self.delay = channel, callback, delay
		listener["on"][channel].append(self)

	# Push for an attack!
	def push(self, con):
		self.con = con

	# Stop the attack!
	def pop(self):
		self.con = None

	# Goodbye senpai :(
	def disconnect(self):
		if self.channel in listener["on"] and self in listener["on"][self.channel]:
			listener["on"][self.channel].remove(self)

''' Create a listener that will hopefully be
	be noticed by senpai, but only once :(
'''
class once:
	def __init__(self, channel, callback):
		self.channel, self.callback = channel, callback
		listener["once"][channel].append(self)

	# Goodbye senpai :(
	def disconnect(self):
		if self.channel in listener["once"] and self in listener["once"][self.channel]:
			listener["once"][self.channel].remove(self)

''' Make senpai look for listeners and make him
	notice them at the right moment.
'''
def update():
	# change scope
	global screen, tick

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			# bye bye :(

			try:
				# Neat catch for inexistent server.
				ahoge.close_all()
				ahoge.server.close()
			except:
				pass

			sys.exit()
		elif event.type == pygame.VIDEORESIZE:
			# resize

			global size, width, height
			size = width, height = event.dict['size']
			screen = pygame.display.set_mode(
				size,
				option
			)
	
	screen.fill(background)

	# update tick
	tick_d = time.time()-tick
	tick = tick+tick_d

	# cast a bright light here!
	fire("update", tick_d)

	# Start planning for the attack!
	for v in timeout_list:
		v["t"] = v["t"]-tick_d

		if v["t"] <= 0:
			v["callback"](*v["arg"])
			v["fin"] = True
			timeout_list.remove(v)

	# draw canvas
	pygame.display.flip()