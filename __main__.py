import sys, pygame, time

# Initialize.
pygame.init()

# Call senpai.
import asset.api.SenPy as senpai
imouto = senpai.remote["imouto"]

# Make imouto pretty.
imouto.background = None

# Start the game.
imouto.start(
	120,
	(800, 600),
	pygame.HWSURFACE|pygame.DOUBLEBUF
)

# Ask for name.
import asset.ext.interface_name

while True:
	imouto.update()