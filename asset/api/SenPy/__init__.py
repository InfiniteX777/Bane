''' He who is yearned to notice thy forsaken souls. Thy foul sins who
	desire will be purged, and be forgotten by the senpai.
'''
import importlib

remote = {}

def load():
	global load
	del load

	# Create a dummy senpai to fool those wretched demons.
	# (Allows remote access of 'SenPy.py' from other modules.)
	class this:
		def __new__(self):
			raise Exception("Cannot instantiate this class.")

	# Hook the remote to the dummy.
	this.remote = remote

	# Load senpai's subordinates.
	def get(name):
		remote[name] = importlib.import_module(
			__package__ + "." + name
		).load(this)

	for v in list((
		"moe", # Event Creator
		#"sensei", # Class Creator
		"tsundere", # Miscellaneous
		"imouto", # Game Interface
		"ahoge", # Network Interface
		"kouhai", # GUI Input
		"kuudere" # Font Manager
	)):
		get(v)

load()