import pygame

import asset.api.SenPy as senpai
kouhai = senpai.remote["kouhai"]
imouto = senpai.remote["imouto"]
kuudere = senpai.remote["kuudere"]

# Font
font_header = kuudere.get("segoe ui", 13, False)
font_body = kuudere.get("calibri", 13, False)

class Window:
	def __init__(self, header, body, callback, choices = ["No", "Yes"]):
		listeners = []
		drag = 0

		frame = kouhai.Frame({
			"rect": (250, 250, 300, 100),
			"zindex": 3
		})

		surface = pygame.Surface(
			(300, 100),
			pygame.SRCALPHA
		)

		surface.fill((0, 0, 0, 63))

		surface.blit(font_header.render(
			header,
			1,
			(255, 255, 255)
		), (5, 2))

		kuudere.draw(
			surface,
			font_body,
			(5, 25, 290, 70),
			body,
			1,
			(255, 255, 255),
			align = (0.5, 0)
		)

		# Your last hovered choice. For aesthetic purposes.
		last_choice = -1
		# Number of choices.
		n = len(choices)
		# Width of the buttons.
		width = (
			# Width of the region that contains all of the choices.
			290 -
			# Total sum of the margins between each button,
			# excluding the outer margin.
			(n - 1)*5
		# Since we've only calculated the sum of each button's
		# length, we divide it with 'n'.
		)//n

		for i in range(n):
			x = 5 + i*(width + 5)

			surface.fill(
				(0, 0, 0),
				(x, 75, width, 20)
			)

			image = font_body.render(
				choices[i],
				1,
				(255, 255, 255)
			)
			rect = image.get_rect()

			surface.blit(image, (
				x + (width - rect.x)/2 - 5,
				79
			))

		def get_choice(x, y):
			if y > 75 and y < 95 and x <= 295:
				for i in reversed(range(n)):
					if (x > 5 + i*(width + 5) and
						x <= (i+1)*(width + 5)):
						return i

			return -1

		# Frame MBD
		def mousebuttondown(event):
			nonlocal drag, get_choice

			if event.button == 1:
				choice = get_choice(
					event.pos[0] - frame.properties["rect"].x,
					event.pos[1] - frame.properties["rect"].y
				)

				if choice == -1:
					drag = 1

		listeners.append(frame.on("mousebuttondown", mousebuttondown))

		# Global MB
		def mousebuttonup(event):
			nonlocal get_choice, drag, callback, self

			if event.button == 1:
				if not drag:
					choice = get_choice(
						event.pos[0] - frame.properties["rect"].x,
						event.pos[1] - frame.properties["rect"].y
					)

					if choice != -1:
						callback(choice, self)

				drag = 0

		listeners.append(imouto.on("mousebuttonup", mousebuttonup))

		# Global MM
		def mousemotion(event):
			nonlocal drag

			if drag:
				nonlocal frame
				frame.properties["rect"].x += event.rel[0]
				frame.properties["rect"].y += event.rel[1]
			else:
				nonlocal get_choice, surface, last_choice
				choice = get_choice(
					event.pos[0] - frame.properties["rect"].x,
					event.pos[1] - frame.properties["rect"].y
				)

				if last_choice != choice:
					if last_choice != -1:
						pygame.draw.rect(
							surface,
							(0, 0, 0),
							(
								5 + last_choice*(width + 5), 75,
								width, 20
							),
							1
						)

					last_choice = choice

				if choice != -1:
					pygame.draw.rect(
						surface,
						(255, 255, 255),
						(5 + choice*(width + 5), 75, width, 20),
						1
					)

		listeners.append(imouto.on("mousemotion", mousemotion))

		def update(dt):
			nonlocal frame, surface

			imouto.screen.blit(
				surface,
				frame.properties["rect"]
			)

		listeners.append(imouto.on("update", update))

		def destroy():
			frame.destroy()

			for v in listeners:
				v.disconnect()

		self.destroy = destroy