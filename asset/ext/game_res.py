import random

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

# Redraw from deck. Strictly bottom-side only.
def redraw(deck, hand, l):
	for i in l:
		if not deck:
			break # Empty deck.

		hand[1][i]["color"] = random.randint(0, 5)
		hand[1][i]["type"] = random.randint(0, 1)
		hand[1][i]["effect"] = deck.pop()

''' deck = Bottom side's deck.
	hand = Both players' cards on their hand.
	a = Position of card A.
	b = Position of card B.

	*A and B are not on the same side.*
'''

# An attacking card on the attacker's persepective.
# Handles redrawing.
# A attacks B.
class attack_atk:
	def __new__(self):
		raise Exception("Cannot instantiate this class.")

# An attacking card on the defender's perspective.
# Does not handle redrawing.
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

		random.shuffle(list)

		for i in range(len(list)):
			hand[1][i]["color"], hand[1][i]["type"], hand[1][i]["effect"] = list[i]

	def reset(deck, hand):
		for card in hand[1]:
			if card["effect"]:
				deck.append(card["effect"])

		for card in hand[1]:
			if not deck:
				break # Empty deck.

			card["color"] = random.randint(0, 5)
			card["type"] = random.randint(0, 1)
			card["effect"] = deck.pop()

	def paint(deck, hand):
		for card in hand[1]:
			card["color"] = random.randint(0, 5)

	def chaos(deck, hand):
		redraw(deck, hand, range(6))

# A defending card on the attacker's perspective.
# Handles redrawing.
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

		random.shuffle(list)

		for i in range(6):
			if list:
				hand[1][i]["color"], hand[1][i]["type"], hand[1][i]["effect"] = list[i]
			else:
				hand[1][i]["effect"] = ""

	def reset(deck, hand):
		for card in hand[1]:
			if card["effect"]:
				deck.append(card["effect"])

		random.shuffle(deck)

		for card in hand[1]:
			if not deck:
				break # Empty deck.

			card["color"] = random.randint(0, 5)
			card["type"] = random.randint(0, 1)
			card["effect"] = deck.pop()

	def paint(deck, hand):
		for card in hand[1]:
			card["color"] = random.randint(0, 5)

	def chaos(deck, hand):
		redraw(deck, hand, range(6))

# A defending card on the defender's perspective.
# B attacks A.
class defend_def:
	def __new__(self):
		raise Exception("Cannot instantiate this class.")