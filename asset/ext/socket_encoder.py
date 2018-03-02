''' Shortens socket addresses.

	.encode(address)
		Encodes the address.

	.decode(v)
		Decodes the given string and returns the address. Returns
		'None' if invalid format.
'''
import re

index = []

for i in range(26):
	if i < 10:
		index.insert(i, str(i))

	index.insert(i+10, chr(i+97))
	#index.insert(i+10, chr(i+65))
	#index.insert(i+37, chr(i+97))

def encode(addr):
	n = len(index)
	v = "1"
	res = ""

	for k in re.split("\.", addr[0]):
		v += ("000" + k)[-3:]

	v = int(v + str(addr[1]))

	while v:
		i = v%n
		res = str(index[i]) + res
		v = v//n

	return res

def decode(v):
	n = len(index)
	res = 0
	i = len(v)-1

	for k in v:
		if not k in index:
			return # Invalid syntax.

		res += index.index(k)*(n**i)
		i -= 1

	try:
		res = str(res)[1:]
		ip = ""

		for i in range(4):
			ip += str(int(res[:3]))
			res = res[3:]

			if i < 3:
				ip += "."
		return ip, int(res)
	except:
		pass