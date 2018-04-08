''' Class creator.

	construct(scope_static = [], scope_local = [])
		Construct a class. scope_global creates a set of variables
		that is shared throughout all instantiated objects of
		this class.
'''
import inspect

def load(senpai):
	moe = senpai.remote["moe"]

	class this:
		__new__ = senpai.__new__

		def construct(scope_static = [],
					  scope_local = []):
			l = {}

			class this:
				def __init__(self):
					self.on, self.fire = moe()

			def setter(scope, k):
				@property
				def p(self):
					self.fire("indexed", k)

					return scope[k]

				@p.setter
				def p_set(self, v):
					scope[k] = v

					self.fire("changed", k, v)

				setattr(this, k, p)
				setattr(this, k, p_set)

			def iterate(scope):
				l, i, k = {}, 0, None

				for v in scope:
					if i:
						i = 0
						l[k] = v

						setter(scope, k)
					else:
						if getattr(this, v, None):
							raise Exception(
								"Property '" + k +
								"' already in-use!"
							)

						i = 1
						k = v

				return l

			scope_static = iterate(scope_static)
			scope_local = iterate(scope_local)

			interface = this()

			def new(p = {}):
				obj = this()

				for k in p:
					if not getattr(obj, k, None):
						raise Exception(
							"Property '" + k +
							"' does not exist!"
						)

					setattr(obj, k, p[k])

				return obj

			setattr(interface, "new", new)

			return this

	return this