''' Kawaii game interface.
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
		# Game clock.
		clock = pygame.time.Clock()
		# 0 = No limit. FPS = 0 to 999...
		fps = 0
		# Screen size.
		size = width, height = 320, 240
		# Screen rendering options.
		flag = 0
		# Background color.
		background = 0, 0 ,0
		# Screen.
		screen = None
		# Rect.
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
			
			this.screen.fill(this.background)

			# cast a bright light here!
			this.fire("update", dt)

			# draw canvas
			pygame.display.flip()

	return this