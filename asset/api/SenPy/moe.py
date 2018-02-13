''' A moe event handler.

	event()
		Returns 2 functions. 1st one handles the
		listener creation, while the 2nd one
		fires the listeners with the given
		channel.

		on(
			channel[String],
			callback[Function(
				arg[Tuple]
			)],
			volatile[Boolean]=False
		)
			Creates a 'Listener' object that
			can be disconnected. If volatile is
			set to True, it will automatically
			disconnect after being fired once.

			Listener(
				event[Dictionary],
				channel[String],
				callback[Function(
					arg[Tuple]
				)],
				volatile[Boolean]=False
			)
				A 'Listener' object.

				.disconnect()
					Disconnects from the
					event.

		fire(
			channel[String],
			arg[Tuple]
		)
			Executes all listeners from the
			channel with the given arguments.
'''

class Listener:
	def __init__(
		self,
		event,
		channel,
		callback,
		volatile=False
	):
		if channel not in event:
			event[channel] = []

		self.event = event
		self.channel = channel
		self.callback = callback
		self.volatile = volatile

		event[channel].append(self)

	def disconnect(self):
		self.event[self.channel].remove(self)

def event():
	list = {}

	def on(channel, callback, volatile=False):
		return Listener(
			list,
			channel,
			callback,
			volatile
		)

	def fire(channel, *tuple):
		if channel in list:
			for v in list[channel]:
				v.callback(*tuple)

				if v.volatile:
					v.disconnect()

	return (on, fire)

def load(senpai):
	return event