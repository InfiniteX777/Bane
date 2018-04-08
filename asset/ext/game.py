''' Protocol:
		6[card_pos][color][type][effect]
			Request change card data in specified position. Repeatable.

		7[card_pos_A][card_pos_B]
			Request attack card A with card B.

		8[lose]
			If [lose] has no value (None), change turn. If [lose] has
			a value of 1 (opponent has no more cards), send same
			protocol with [lose] value of 0 (you still have cards; you
			win) or 1 (you don't have cards left; stalemate).

		9[turn][eos]
			Request 'virtual coin flip'. Both ends will send the same
			protocol twice. The first request has no [turn] value.
			The [turn] value determines the receiver's turn. The [eos]
			determines the end of session.
'''
import random, pygame, threading
import asset.ext.game_res as game_res
import asset.ext.window as window

# Seed the RNG.
random.seed()

import asset.api.SenPy as senpai
ahoge = senpai.remote["ahoge"]
kouhai = senpai.remote["kouhai"]
imouto = senpai.remote["imouto"]
kuudere = senpai.remote["kuudere"]
tsundere = senpai.remote["tsundere"]

# Font
body = kuudere.get("calibri", 14, False)
body_line = body.get_linesize()
body_big = kuudere.get("segoe ui", 24, False)
body_big_bold = kuudere.get("calibri", 24, True)
body_huge = kuudere.get("segoe ui", 48, False)

# Image
img_btn = pygame.image.load("asset/img/turn_button.png")
img_card = pygame.image.load("asset/img/card.png")
img_card_type = pygame.image.load("asset/img/card_type.png")
img_card_effect = {}

# Server
server = code = None
opponent = None

# 'End Turn' Button
btn = kouhai.Frame({
	"rect": (
		368,
		268,
		64,
		64
	),
	"active": 0
})
# 0 = Idle; 1 = Hovered; 2 = Hovered and Held; 3 = Unhovered and Held
btn_state = 0

def mouseenter():
	global btn_state

	if btn_state:
		btn_state = 2
	else:
		btn_state = 1

btn.on("mouseenter", mouseenter)

def mouseleave():
	global btn_state

	if btn_state == 2:
		btn_state = 3
	else:
		btn_state = 0

btn.on("mouseleave", mouseleave)

def mousebuttondown(event):
	global btn_state

	if event.button == 1:
		btn_state = 2

btn.on("mousebuttondown", mousebuttondown)

for v in list((
	"chaos",
	"paint",
	"reset",
	"stun"
)):
	img_card_effect[v] = pygame.image.load(
		"asset/img/effect/" + v + ".png"
	)

# If the game is in progress or not.
# 0 = No game in-progress.
# 1 = In-game.
# 'string' = Post-game. This will pose as the text in the middle
# of the screen.
active = 0
# Turn. Attack. Swap.
trn, atk, swp = 0, 0, 0
# Your deck.
deck = []
# The cards on the players' hand. The opponent's cards are faced down
# by default, while yours is faced up for you.
hand = (
	[], # The opponent's cards. Counts from right to left.
	[] # Your cards. Counts from left to right.
)
# Currently hovered card for showing its effect info.
info_surface = None
# Check if the player is dragging a card towards another card.
drag = target = None
# Desired mouse position and current mouse position.
mouse = mouse_delta = (0, 0)

# Send your cards' data. Also send if you don't have cards left (deck
# and hand). This will tell if you win, lose, or stalemate.
def send_hand():
	global server, opponent
	# Data to be sent.
	v = ""
	# Number of cards.
	n = len(deck)

	for i in range(6):
		# Collect cards with effects. All cards should have an effect,
		# otherwise it's an empty slot.
		if hand[1][i]["effect"]:
			n += 1

		# Append data.
		v += "_" + (
			str(i) + # Position
			str(hand[1][i]["color"]) + # Color
			str(hand[1][i]["type"]) + # Type
			hand[1][i]["effect"] # Effect
		)

	server.send("6" + v[1:], opponent)

	if not n:
		# Tell him you don't have any cards left.
		global active
		active = 2 # Set to post-game mode.
		server.send("81", opponent)

# Data sent from your opponent.
def received(addr, i, data, name=""):
	global deck, hand, trn, atk, swp, active, active, opponent

	if i == 6: # Card Change
		for v in data.split("_"):
			try:
				i = int(v[0])
				hand[0][i]["color"] = int(v[1])
				hand[0][i]["type"] = int(v[2])
				hand[0][i]["effect"] = v[3:]
			except:
				pass
	elif i == 7: # Attack
		# Draw > Attacker's effect > Defender's effect
		try:
			a, b = int(data[0]), int(data[1])

			aa, ab = hand[1][a]["type"], hand[1][a]["effect"]
			ba, bb = hand[0][b]["type"], hand[0][b]["effect"]

			# Draw.
			game_res.draw(
				deck,
				hand,
				game_res.hit(hand[1], a)
			)

			# Check for opponent's card effect first.
			if not ba:
				# Opponent's card is an attack-type.
				func = getattr(game_res.attack_def, bb, None)

				if func:
					# Invoke effect.
					func(deck, hand)

			# Check for your card effect.
			if aa:
				# Your card is a defense-type.
				func = getattr(game_res.defend_def, ab, None)

				if func:
					# Invoke effect.
					func(deck, hand)

			send_hand()
		except:
			pass
	elif i == 8: # End Turn
		# Check if a data was sent.
		if data:
			# Received additional data (A request to end the game. 
			# Either out of cards, disconnection, or conceded).
			data = int(data)
			# Count how many cards you got.
			n = len(deck)

			for card in hand[1]:
				if card["effect"]:
					# We only need to know if we still have at
					# least 1 card on our hand, so we break
					# immediately.
					n += 1
					break

			# Tell him if you still have cards.
			if type(active) != str:
				# Tell him if you still have cards.
				server.send("8" + (n and "0" or "1"), addr)

			# Re-check the data again. This time, check if it has
			# a value of 1.
			if data:
				# Opponent is out of cards or conceded.
				active = n and "You won!" or "Stalemate!"
			else:
				# Opponent still has cards.
				active = n and "Stalemate!" or "You lost!"

			def wait():
				global active
				active = 0

			threading.Timer(
				3,
				wait
			).start()
		else:
			# End turn.
			trn = atk = swp = 1
	elif i == 9: # Flip Coin
		# Make sure that you are not in a game.
		if not active:
			# 2nd request.
			if data:
				trn, atk, swp = int(data[0]), 0, 1
				opponent = addr

				if not data[2:]:
					# Tell your opponent "I accept your challenge,
					# peasant. You're a third rate duelist with a
					# 4th rate deck."
					server.send("9" + str(1-trn) + "0", addr)

				start() # DU-DU-DU-DU-DUEL!
			# 1st request.
			else:
				# 1st request. Make a window prompt so the user has
				# a psuedo-consent with the duel.
				def callback(choice, win):
					if choice:
						# Accepted.
						global trn, atk, swp, server, opponent
						nonlocal addr
						opponent = addr

						if random.random() < 0.5:
							# You get 1st turn.
							trn, atk, swp = 1, 0, 1

							server.send("90", addr)
						else:
							# Your opponent gets 1st turn.
							trn = 0

							server.send("91", addr)

					# Destroy after the user has chosen their decision.
					win.destroy()

				win = window.Window(
					"It's time to du-du-du-duel!",
					"Player '" + name +
					"' would like to have a duel with you!",
					callback
				)

def mousemotion(event):
	global drag

	if drag:
		global mouse
		mouse = event.pos

imouto.on("mousemotion", mousemotion)

def mousebuttonup(event):
	if event.button == 1:
		global server, code, opponent, drag, target, info_surface, btn_state, trn, atk

		# Check if player wants to end their turn.
		if btn_state == 2:
			# It's the player's turn and has attacked.
			if trn and not atk:
				trn = 0

				# Send an 'end turn' request.
				server.send("8", opponent)

		# Reset 'end turn' button.
		btn_state = 0

		# Check if player is dragging a card towards another card.
		if target and drag:
			if target[0]:
				# Target is on the same side. Swap.
				global swp

				if swp:
					swp -= 1
					# Get the cards.
					a = hand[1][drag[1]]
					b = hand[1][target[1]]

					# Get values.
					aa = a["color"]
					ab = a["type"]
					ac = a["effect"]

					# Get positions.
					ax = a["frame"].properties["rect"].x
					bx = b["frame"].properties["rect"].x

					# Swap values.
					a["color"] = b["color"]
					a["type"] = b["type"]
					a["effect"] = b["effect"]
					a["pos_delta"][0] = bx - ax
					b["color"] = aa
					b["type"] = ab
					b["effect"] = ac
					b["pos_delta"][0] = ax - bx

					send_hand()
			elif atk:
				# Target is on the opposite side. Attack.
				atk -= 1

				aa = hand[1][drag[1]]["type"]
				ab = hand[1][drag[1]]["effect"]
				ba = hand[0][target[1]]["type"]
				bb = hand[0][target[1]]["effect"]

				game_res.draw(deck, hand, [drag[1]])

				if not aa:
					func = getattr(game_res.attack_atk, ab, None)

					if func:
						func(deck, hand)

				if ba:
					func = getattr(game_res.defend_atk, bb, None)

					if func:
						func(deck, hand)

				server.send(
					"7" + str(target[1]) + str(drag[1]),
					opponent
				)

				send_hand()

		drag = target = info_surface = None

imouto.on("mousebuttonup", mousebuttonup)

# Build the frames for the cards.
for y in range(2):
	for x in range(6):
		def scope(y, x):
			i = 500 - x*100

			if y:
				i = x*100

			frame = kouhai.Frame({
				"rect": (
					105 + i,
					10 + y*460,
					90,
					120
				),
				"active": 0
			})

			card = {
				# For mouse detection.
				"frame": frame,
				# Flips the card (Face up/down).
				"flip": 0,
				# Color of the card (up to 6 colors).
				"color": 0,
				# Type of card (attack/defense).
				"type": 0,
				# Effect of the card (See 'game_res.py' for info).
				"effect": "",
				# Desired offset from its position.
				"pos": [0, 0],
				# Current offset from its position.
				"pos_delta": [0, 0]
			}

			hand[y].append(card)

			def mousebuttondown(event):
				global trn
				nonlocal card

				if event.button == 1 and y and trn and card["effect"]:
					global drag, mouse, mouse_delta, info_surface
					drag = (y, x)
					mouse = mouse_delta = event.pos
					card["pos"][1] = 0
					info_surface = None

			frame.on("mousebuttondown", mousebuttondown)

			def mouseenter():
				global drag, info_surface, trn

				if drag and trn:
					global atk, swp

					if (y and not swp) or (not y and not atk):
						return

					if (hand[drag[0]][drag[1]] != card and
						card["effect"]):
						global target
						target = (y, x)
						image = body_big_bold.render(
							y and "Swap" or "Attack",
							True,
							(255, 255, 255)
						)
						rect = image.get_rect()
						info_surface = pygame.Surface(
							(rect.width + 20, rect.height + 15),
							pygame.SRCALPHA
						)

						info_surface.fill((0, 0, 0, 191))
						info_surface.blit(
							image,
							(10, 10)
						)
				elif ((card["flip"] - y) and
					  card["effect"] in game_res.info):
					card["pos"][1] = y and -20 or 20
					res, height, _ = kuudere.wrap(
						body,
						(390, 0),
						body_line,
						game_res.info[card["effect"]][card["type"]],
						1,
						(255, 255, 255)
					)

					info_surface = pygame.Surface(
						(400, height + 5),
						pygame.SRCALPHA
					)

					info_surface.fill((0, 0, 0, 191))

					i = 0
					for image in res:
						info_surface.blit(
							image,
							((400 - image.get_rect().width)/2, i + 5)
						)

						i += body_line

			frame.on("mouseenter", mouseenter)

			def mouseleave():
				global drag, info_surface

				if drag:
					global target

					if target and hand[target[0]][target[1]] == card:
						target = info_surface = None
				else:
					card["pos"][1] = 0
					info_surface = None

			frame.on("mouseleave", mouseleave)

		scope(y, x)

# Draw the cards.
def draw():
	global active, info_surface

	if type(active) == str:
		# Post-game.
		image = body_huge.render(active, True, (255, 255, 255))
		rect = image.get_rect()

		# Draw the result of the game.
		imouto.screen.blit(image, (
			400 - rect.width/2,
			300 - rect.height/2
		))
	elif active:
		# Game in-progress.
		global trn, btn_state, atk
		image = body_big.render(str(len(deck)), True, (255, 255, 255))
		rect = image.get_rect()

		# Draw the number of cards in your deck.
		imouto.screen.blit(image, (
			400 - rect.width/2,
			450 - rect.height
		))

		# Draw the button in the middle.
		imouto.screen.blit(img_btn, (
			358, 258
		), (
			trn and (
				(btn_state == 2 or atk) and 252 or
				btn_state == 1 and 168 or
				84
			) or 0,
			0,
			84,
			84
		))

		for i in range(2):
			for card in hand[i]:
				# Slowly set the delta towards the position for
				# an easing effect.
				card["pos_delta"][0] = tsundere.lerp(
					card["pos_delta"][0],
					card["pos"][0],
					0.2,
					1
				)
				card["pos_delta"][1] = tsundere.lerp(
					card["pos_delta"][1],
					card["pos"][1],
					0.2,
					1
				)

				pos = card["frame"].properties["rect"].topleft
				pos = (
					card["pos_delta"][0] + pos[0],
					card["pos_delta"][1] + pos[1]
				)

				if card["effect"]:
					if (card["flip"] - i):
						# Faced up.

						# Draw the card.
						imouto.screen.blit(img_card, pos, (
							card["color"]*90, 0,
							90, 120
						))

						# Card type. Bottom-left.
						imouto.screen.blit(img_card_type, (
							pos[0] + 10,
							pos[1] + 94
						), (
							card["type"]*16, 0,
							16, 16
						))

						# Card effect icon. Center.
						if card["effect"] in img_card_effect:
							imouto.screen.blit(
								img_card_effect[card["effect"]],
								(pos[0] + 21, pos[1] + 36)
							)
					else:
						# Faced down.
						imouto.screen.blit(img_card, pos, (
							540, 0,
							90, 120
						))

		if drag:
			global target, mouse, mouse_delta
			a = hand[drag[0]][drag[1]]

			center = a["frame"].properties["rect"].center
			v = (target and
				hand[target[0]][target[1]]["frame"].properties["rect"].center or
				mouse
			)
			mouse_delta = (tsundere.lerp(
				v[0], mouse_delta[0],
				0.4, 1
			), tsundere.lerp(
				v[1], mouse_delta[1],
				0.4, 1
			))

			pygame.draw.line(
				imouto.screen,
				(0, 0, 0),
				(
					center[0] + a["pos_delta"][0]/2,
					center[1] + a["pos_delta"][1]/2
				),
				mouse_delta,
				6
			)

		if info_surface:
			rect = info_surface.get_rect()
			imouto.screen.blit(info_surface, (
				(800 - rect.width)/2,
				(600 - rect.height)/2
			))



def start():
	global opponent

	if not opponent:
		return # How can this game be real if the opponent isn't real?

	global deck, active

	if active:
		return # There's already a game in progress.

	# Reset the deck.
	deck = []
	# Your collection. Max cards is 50.
	coll = {
		"paint": 10,
		"reset": 10,
		"stun": 20,
		"chaos": 10
	}

	# Put your collection in the deck.
	for k in coll:
		for _ in range(coll[k]):
			deck.append(k)

	# Shuffle the deck.
	random.shuffle(deck)

	for i in range(2):
		for card in hand[i]:
			# Activate the frames for mouse detection.
			card["frame"].properties["active"] = 1

			# Check if it's your hand.
			if i and deck:
				# Draw a card.
				card["color"] = random.randint(0, 5)
				card["type"] = random.randint(0, 1)
				card["effect"] = deck.pop()

	send_hand()

	# Active the button in the middle.
	btn.properties["active"] = 1

	# ITS TIME TO DU-DU-DU-DU-DUEL!
	active = 1