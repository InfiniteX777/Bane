''' Kawaii UI manager.

	Frame(
		rect[
			pygame.Rect,
			tuple[(Number, Number, Number, Number)]
		]=(0, 0, 100, 100),
		zindex[Number]=0
	):
		Creates a frame that reacts to your mouse.

		.on(
			channel[String],
			callback[Function(event)]
		)
			Creates a listener.

		.fire(
			channel[String],
			data[tuple]
		)
			Fires data towards the given channel.
'''

import pygame, importlib

class this:
	pass

# List of frames.
this.list = {}
# Hovered frames.
this.hover = []
# Top-most frame that contains the mouse point.
this.target = None
# Currently focused active frame (The last frame that you clicked).
this.focus = None
# Helps find the proper target.
debounce = False

def load(senpai):
	moe = senpai.remote["moe"]
	imouto = senpai.remote["imouto"]

	def get(name):
		return importlib.import_module(__package__ + "." + name).load(senpai, this)

	this.Frame = get("Frame")
	this.TextBox = get("TextBox")

	def recursive(
		list, # The parent's list.
		event, # The event tag.
		screen # The parent's rect.
	):
		global debounce

		for k, v in reversed(sorted(list.items())):
			if len(v) > 0:
				for obj in reversed(v):
					rect = obj.properties["rect"]

					# Collision test its children first.
					recursive(obj.properties["child"], event, rect)

					# Adjust relative to parent's rect.
					x, y, w, h = screen.x, screen.y, screen.width, screen.height

					rect = pygame.Rect(
						rect.x + x + w*obj.properties["scale_pos"][0],
						rect.y + y + h*obj.properties["scale_pos"][1],
						rect.width + w*obj.properties["scale_size"][0],
						rect.height + h*obj.properties["scale_size"][1]
					)

					if obj.properties["active"] and rect.collidepoint(event.pos):
						if obj not in this.hover:
							this.hover.append(obj)
							obj.fire("mouseenter")
						else:
							obj.fire("mousemotion", event)

						if not debounce:
							debounce = True
							prev = this.target
							this.target = obj

							if prev and prev != obj:
								prev.fire("untargeted")

							obj.fire("targeted")
					else:
						if this.target == obj:
							this.target = None
							obj.fire("untargeted")

						if obj in this.hover:
							this.hover.remove(obj)
							obj.fire("mouseleave")
			else:
				# Clear unused index.
				del list[k]

	def mousemotion(event):
		global debounce

		# Set debounce to False.
		debounce = False

		recursive(this.list, event, imouto.screen.get_rect())

		#print(this.target and isinstance(this.target, this.TextBox))

	def mouseup(event):
		for v in this.hover:
			v.fire("mousebuttonup", event)

	def mousedown(event):
		prev = this.focus
		this.focus = this.target

		if this.target:
			if this.target != prev:
				if prev:
					imouto.fire("unfocused", prev)
					prev.fire("unfocused")

				imouto.fire("focused", this.target)
				this.target.fire("focused")
		elif prev:
			imouto.fire("unfocused", prev)
			prev.fire("unfocused")

		for v in this.hover:
			v.fire("mousebuttondown", event)


	imouto.on("mousemotion", mousemotion)
	imouto.on("mousebuttonup", mouseup)
	imouto.on("mousebuttondown", mousedown)

	return this