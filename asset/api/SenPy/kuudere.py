''' A cool-headed font manager.

	.get(name, size, bold=False, italic=False)
		Returns a 'Font' object with the given parameters. Will
		store in a cache and will return the same object when
		called again.

	.draw(
		surface,
		font,
		rect,
		text="",
		antialias=0,
		color=(0, 0, 0),
		background=None,
		align=(0, 0)
	)
		Draws the given font and its paremeters on a surface. See
		pygame.Font for more details.

	.wrap(
		font,
		size,
		linesize,
		text="",
		antialias=0,
		color=(0, 0, 0),
		background=None
	)
		Creates a list of 'Image' surface objects wrapped with the
		given 'size' argument. If size's height is 0, will only
		restrict the width.

		Returns a list (list), total height (int), and excess
		text (string).

	.flush()
		Clears the font cache, allowing new 'Font' objects with
		similar parameters to be created.
'''
import pygame

cache = {}

def load(senpai):
	class this:
		__new__ = senpai.__new__

		def get(name, size, bold=False, italic=False):
			global cache
			tuple = (name, size, bold, italic)

			if tuple not in cache:
				cache[tuple] = pygame.font.SysFont(
					name,
					size,
					bold,
					italic
				)

			return cache[tuple]

		def draw(
			surface,
			font,
			rect,
			text="",
			antialias=0,
			color=(0, 0, 0),
			background=None,
			align=(0, 0)
		):
			rect = pygame.Rect(rect)

			if rect.width > 0:
				res = []
				y = rect.top
				linesize = font.get_linesize()
				center = align[1] > 0 and align[1] < 1

				while text:
					i = 0 # Text length.
					s = None # Last whitespace seen.

					if rect.height > 0 and y > rect.bottom:
						break

					# Get length of text relative to width.
					while i < len(text):
						i += 1

						if text[i-1].isspace():
							s = i

						if font.size(text[:i+1])[0] >= rect.width:
							# Max width reached.
							if s and (i < len(text) or not text[i].isspace()):
								# Move back to the last whole word.
								i = s

							break

					image = font.render(
						text[:i],
						antialias,
						color,
						background
					)

					if center:
						res.append(image)
					else:
						image_rect = image.get_rect()

						# Draw on surface.
						surface.blit(image, (
							rect.x + align[0]*(rect.width - image_rect.width),
							y + align[1]*(rect.height - y*2 - image_rect.height)
						))

					text = text[i:]
					y += linesize

				n = len(res)
				if n > 0:
					w = y-rect.top-(linesize-res[n-1].get_rect().height)
					y = rect.top

					for image in res:
						image_rect = image.get_rect()

						surface.blit(image, (
							rect.x + align[0]*(rect.width - image_rect.width),
							y + align[1]*(rect.height - w)
						))

						y += linesize

				return text

			surface.blit(font.render(
				text,
				antialias,
				color,
				background
			), rect)

		def wrap(
			font,
			size,
			linesize,
			text="",
			antialias=0,
			color=(0, 0, 0),
			background=None
		):
			res = []
			y = 0

			while text:
				i = 0 # Text length.
				s = None # Last whitespace seen.

				# Get length of text relative to width.
				while i < len(text):
					i += 1

					if text[i-1].isspace():
						s = i

					if font.size(text[:i+1])[0] >= size[0]:
						# Max width reached.
						if s and (i < len(text) or not text[i].isspace()):
							# Move back to the last whole word.
							i = s

						break

				res.append(font.render(
					text[:i],
					antialias,
					color,
					background
				))

				text = text[i:]

				if size[1] > 0 and y + linesize > size[1]:
					break

				y += linesize

			return res, y, text

		def flush():
			global cache

			cache = {}

	return this