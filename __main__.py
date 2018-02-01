import asset.api.sen as senpai
import asset.api.ahoge as ahoge
import sys, pygame, socket, time

ahoge.server_start(ahoge.ip, 5005)

speed = [1, 1]

ball = pygame.image.load("ball.bmp")
ballrect = ball.get_rect()

def update(dt):
	global ballrect

	ballrect = ballrect.move(speed)
	if ballrect.left < 0 or ballrect.right > senpai.width:
		speed[0] = -speed[0]
	if ballrect.top < 0 or ballrect.bottom > senpai.height:
		speed[1] = -speed[1]

	senpai.screen.blit(ball, ballrect)

bob = ahoge.stream(ahoge.ip, 5005)
print(bob.status)

def test(data):
	print(data)
	bob.send("yo")

def nein(sock, addr, data):
	print(data)

bob.on_recv(test)
ahoge.on_recv(nein, bob.sock.getsockname())
ahoge.broadcast("hey")

def yes(*l):
	bob.send("hi")

senpai.on("update", update)

while True:
	senpai.update()