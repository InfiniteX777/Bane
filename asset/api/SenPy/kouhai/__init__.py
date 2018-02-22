''' Senpai will never notice you.

	list
		A list of frames created.

	hover
		A list of currently 'hovered' frames.

	target
		Currently targeted frame by the mouse.

	focus
		Currently focused frame.

	Frame(rect, zindex=0):
		Creates a frame that reacts to your mouse. These are
		focus-able and only 1 can be focused at a time. Focus is
		attained when clicking on a frame, while clicking on nothing
		will set the focus to 'None'. The top-most frame (highest
		z-index, recently created, 'child-est') will be prioritized.

		properties={ The properties of the frame.
			rect,
				The rectangle of the frame.

			zindex,
				The layer of the frame on the ideal z-axis.

			scale_pos,
				The scalar position of the frame relative to
				the size of the screen.

			scale_size,
				The scalar size of the frame relative to
				the size of the screen.

			active,
				If the frame is clickable. Cannot be hovered and
				focused if False.

			parent,
				The parent of the frame. This adapts the scales
				to the parent's size.

			child
				List of the frame's children.
		}

		.append(v)
			Adds the frame as its child.

		.remove(v)
			Removes the frame from its children if it is.

		.set_zindex(v)
			Sets the layer of the frame. Will become the 'recently
			created' frame on that layer.

		.set_rect(rect)
			Sets the rectangle of the frame.

		.set_active(v)
			Sets if the frame is active.

		.set_focus(flag)
			If True, sets as the currently focused flag and
			calls the event. If False, removes focus if it is being
			focused and calls the event.

		.is_hovered()
			If the mouse is inside the frame's rectangle. This
			also returns True even if there is a frame 'above' it.

		.is_targeted()
			If the mouse is inside the frame's rectangle, while
			being the top-most frame. There can only be 1 targeted
			frame.

		.is_focused()
			If the frame is being focused. A frame can be focused
			by clicking on it. There can only be 1 focused frame,
			and can be different from the targeted frame.

		.is_descendant(v)
			Checks if the frame is a child, or a 'younger generation'
			of this frame.

		.destroy()
			Removes all event handlers. This must be called to
			explicitly remove the object completely.

		.on(channel, callback)
			Creates a listener.

		.fire(channel, data)
			Fires data towards the given channel.

		"mouseenter", ()
			Called when the mouse enters the rectangle.

		"mouseleave", ()
			Called when the mouse leaves the rectangle.

		"focused", ()
			Called when the frame is focused.

		"unfocused", ()
			Called when the frame is unfocused.

		"targeted", ()
			Called when the frame is targeted.

		"untargeted", ()
			Called when the frame is untargeted.

		"mousemotion", (event)
			Called when the mouse is moving inside the rectangle.

		"mousebuttonup", (event)
			Called when a mouse button is released inside
			the rectangle.

		"mousebuttondown" (event)
			Called when a mouse button is pressed inside
			the rectangle.

	TextBox(rect, zindex=0) inherit Frame
		Creates a textbox that accepts key inputs.

		properties={
			text,
				Current text of the text box. Keys are automatically
				appended when pressed, while being focused.

			multiline
				If the text box accepts newline '\n' characters,
				otherwise will end the 'focused' state.
		}

		"keyinput", (event)
			Called when a key is pressed while focused. Also
			repeats a key every 0.3 seconds when held.
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