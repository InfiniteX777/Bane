''' This game interface can't be this cute.

	clock
		The game's clock. Can be used to monitor
		FPS and delay between frames.

	fps
		The maximum FPS. 0 will remove limit.

	size
		Size of the screen, represented by a
		tuple with 2 values.

	width
		Width of the screen.

	height
		Height of the screen.

	flag
		The screen's flags. See pygame.Display
		for more details.

	background
		The background color of the screen.
		Alpha color does not work. Setting to
		'None' will stop 'clearing' the screen
		on every .update().

	rect
		The size of the screen in 'Rect' object.

	.start(fps, size, flag)
		Starts the game. This should be initiated
		first before doing anything.

	.resize(x, y)
		Resizes the screen.

	.update()
		Updates the screen. Should be called in
		a constant loop.
'''

import sys, pygame, time, importlib

event_index = {
	pygame.QUIT: "quit",
	pygame.ACTIVEEVENT: "activeevent",
	pygame.KEYDOWN: "keydown",
	pygame.KEYUP: "keyup",
	pygame.MOUSEMOTION: "mousemotion",
	pygame.MOUSEBUTTONUP: "mousebuttonup",
	pygame.MOUSEBUTTONDOWN: "mousebuttondown",
	pygame.JOYAXISMOTION: "joyaxismotion",
	pygame.JOYHATMOTION: "joyhatmotion",
	pygame.JOYBUTTONUP: "joybuttonup",
	pygame.JOYBUTTONDOWN: "joybuttondown",
	pygame.VIDEORESIZE: "videoresize",
	pygame.VIDEOEXPOSE: "videoexpose",
	pygame.USEREVENT: "userevent"
}

# Key input repetition.
key, key_delay = None, None
closed = False

def load(senpai):
	# import
	moe = senpai.remote["moe"]

	class this:
		clock = pygame.time.Clock()
		fps = 0
		size = width, height = 320, 240
		flag = 0
		background = 0, 0 ,0
		screen = None
		rect = None

		on, fire = moe()

		def start(fps, size, flag):
			this.fps = fps
			this.size = this.width, this.height = size
			this.flag = flag
			this.screen = pygame.display.set_mode(
				this.size, this.flag
			)
			this.rect = this.screen.get_rect()

		def resize(x, y):
			this.size = this.width, this.height = x, y

			this.screen = pygame.display.set_mode(
				(x, y),
				this.flag
			)

			this.rect = this.screen.get_rect()

		''' Make senpai look for listeners and make him
			notice them at the right moment.
		'''
		def update():
			# change scope
			global key, key_delay, closed

			this.clock.tick(this.fps)

			dt = this.clock.get_time()/1000

			if key_delay:
				if key_delay <= 0:
					this.fire("keyinput", key)
				else:
					key_delay -= dt

			for event in pygame.event.get():
				this.fire(event_index[event.type], event)

				if event.type == pygame.QUIT:
					# bye bye :(
					sys.exit()
				elif event.type == pygame.VIDEORESIZE:
					this.resize(*event.dict['size'])
					this.fire("resize", event)
				elif event.type == pygame.KEYDOWN:
					if len(event.unicode) > 0:
						key = event
						key_delay = 0.3

						this.fire("keyinput", key)
				elif event.type == pygame.KEYUP:
					if key and key.key == event.key:
						key, key_delay = None, None

			if this.background:
				this.screen.fill(this.background)

			# cast a bright light here!
			this.fire("update", dt)

			# draw canvas
			pygame.display.flip()

	return this