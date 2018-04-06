import random

# State at which the game is still processing 'drawing cards'.
# This helps preserve the streamlining, as some data may end up
# being sent first.
drawing = 0
# This is for collecting callbacks, where all will be fired as soon
# as the 'drawing' state is back to 0.
drawing_queue = []
info = {
	"stun": [
		"Shuffle the opponent's cards on their hand.",
		"Shuffle the opponent's cards on their hand."
	],
	"reset": [
		"Make the opponent shuffle and redraw their cards.",
		"Make the opponent shuffle and redraw their cards."
	],
	"mirror": [
		"Copy the opponent's cards. Only the non-affected cards will change.",
		"Copy the opponent's cards. Only the non-affected cards will change."
	],
	"paint": [
		"Recolor the opponent's cards.",
		"Recolor the opponent's cards."
	],
	"swap": [
		"Switch cards with the opponent.",
		"Switch cards with the opponent."
	],
	"chaos": [
		"Destroy both you and the opponent's cards. Attacking another card with the same effect will double the effect.",
		"Destroy both you and the opponent's cards. Attacking another card with the same effect will double the effect."
	],
	"xmark": [
		"Reveal the replacing card(s) for this turn.",
		"For this turn, Any card on the attacking card's position will be revealed."
	]
}

# Wait for 'drawing' state to end. Will fire immediately if it is not
# drawing.
def wait(callback, tuple):
	global drawing, drawing_queue

	if drawing:
		drawing_queue.append((callback, tuple))
	else:
		callback(*tuple)

# Default attack pattern.
def hit(handY, pos):
	l = [pos]
	i = 1
	color = handY[pos]["color"]

	while 1:
		d = 0

		# Check left.
		if (pos - i >= 0 and
			handY[pos - i]["effect"] and
			handY[pos - i]["color"] == color):
			d += 1

			l.append(pos - i)

		# Check right.
		if (pos + i < 6 and
			handY[pos + i]["effect"] and
			handY[pos + i]["color"] == color):
			d += 1

			l.append(pos + i)

		i += 1

		if not d:
			break

	return l

# Draw from deck. Strictly bottom-side only.
def draw(deck, hand, l):
	global drawing, drawing_queue
	# Increment state. This tells the system that you are going to
	# need some time to process it.
	drawing += 1

	for i in l:
		if deck:
			hand[1][i]["color"] = random.randint(0, 5)
			hand[1][i]["type"] = random.randint(0, 1)
			hand[1][i]["effect"] = deck.pop()
		else:
			# Empty deck. Replace with emply slot instead.
			hand[1][i]["effect"] = ""

	if deck:
		# No need to re-arrange since your hand must be full at
		# all times.
		return

	l = [] # Re-use the array.

	# Collect all cards with effects (All cards should have an
	# effect. This means that if there is no effect, it must
	# be an empty slot.)
	for card in hand[1]:
		if card["effect"]:
			l.append((
				card["color"],
				card["type"],
				card["effect"]
			))

			card["effect"] = ""

	# Iterate through the array, respectively
	# (color, type, effect).
	for i in range(len(l)):
		hand[1][i]["color"], hand[1][i]["type"], hand[1][i]["effect"] = l[i]

	# Decrement state.
	drawing -= 1

	if not drawing and drawing_queue:
		l = drawing_queue.copy()
		drawing_queue = []

		for callback, tuple in l:
			callback(*tuple)

# deck = Bottom side's deck.
# hand = Both players' cards on their hand.

# An attacking card on the attacker's persepective.
# A attacks B.
class attack_atk:
	def __new__(self):
		raise Exception("Cannot instantiate this class.")

# An attacking card on the defender's perspective.
# B attacks A.
class attack_def:
	def __new__(self):
		raise Exception("Cannot instantiate this class.")

	def stun(deck, hand):
		list = []

		for card in hand[1]:
			if card["effect"]:
				list.append((
					card["color"],
					card["type"],
					card["effect"]
				))

				card["effect"] = ""

		random.shuffle(list)

		for i in range(len(list)):
			hand[1][i]["color"], hand[1][i]["type"], hand[1][i]["effect"] = list[i]

	def reset(deck, hand):
		for card in hand[1]:
			if card["effect"]:
				deck.append(card["effect"])

				card["effect"] = ""

		for card in hand[1]:
			if not deck:
				break # Empty deck.

			card["color"] = random.randint(0, 5)
			card["type"] = random.randint(0, 1)
			card["effect"] = deck.pop()

	def paint(deck, hand):
		for card in hand[1]:
			if card["effect"]:
				card["color"] = random.randint(0, 5)

	def chaos(deck, hand):
		draw(deck, hand, range(6))

# A defending card on the attacker's perspective.
# A attacks B.
class defend_atk:
	def __new__(self):
		raise Exception("Cannot instantiate this class.")

	def stun(deck, hand):
		list = []

		for card in hand[1]:
			if card["effect"]:
				list.append((
					card["color"],
					card["type"],
					card["effect"]
				))

				card["effect"] = ""

		random.shuffle(list)

		for i in range(len(list)):
			hand[1][i]["color"], hand[1][i]["type"], hand[1][i]["effect"] = list[i]

	def reset(deck, hand):
		for card in hand[1]:
			if card["effect"]:
				deck.append(card["effect"])

				card["effect"] = ""

		random.shuffle(deck)

		for card in hand[1]:
			if not deck:
				break # Empty deck.

			card["color"] = random.randint(0, 5)
			card["type"] = random.randint(0, 1)
			card["effect"] = deck.pop()

	def paint(deck, hand):
		for card in hand[1]:
			if card["effect"]:
				card["color"] = random.randint(0, 5)

	def chaos(deck, hand):
		draw(deck, hand, range(6))

# A defending card on the defender's perspective.
# B attacks A.
class defend_def:
	def __new__(self):
		raise Exception("Cannot instantiate this class.")