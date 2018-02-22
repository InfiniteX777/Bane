''' The one.
'''

import importlib

# Private
remote_list = (
	"moe", # Event Creator
	"imouto", # Game Interface
	"ahoge", # Network Interface
	"kouhai", # GUI Input
	"kuudere" # Font Manager
)

remote = {}

# Make senpai's clone
class this:
	remote = None

this.remote = remote

# Load senpai's subordinates.
def get(name):
	this.remote[name] = importlib.import_module(__package__ + "." + name).load(this)

for v in remote_list:
	get(v)