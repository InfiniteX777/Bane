# It's not like I'm doing this for you!
import math

def load(senpai):
	class this:
		__new__ = senpai.__new__

		def lerp(a, b, v, decimal=-1):
			v = max(0, min(1, v))
			v = a*(1 - v) + b*v

			if decimal >= 0:
				n = v > 0 and 1 or -1
				decimal = 10**decimal

				return math.floor(v*n*decimal)*n/decimal
			else:
				return v

	return this