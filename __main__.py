import sys, pygame, time

# Initialize.
pygame.init()

# Call senpai.
import asset.api.SenPy as senpai
ahoge = senpai.remote["ahoge"]
kouhai = senpai.remote["kouhai"]
imouto = senpai.remote["imouto"]
kuudere = senpai.remote["kuudere"]

# Make imouto pretty.
imouto.background = (255, 255, 255)

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