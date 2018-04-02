''' A FRAME FOR YOUR SENPAI!@&!#!112
'''

import pygame

def load(senpai, kouhai):
	moe = senpai.remote["moe"]

	class this:
		def __init__(self, prop={}):
			self.on, self.fire = moe()

			prop = dict({
				"rect": (0, 0, 0, 0),
				"zindex": 0,
				"scale_pos": (0, 0),
				"scale_size": (0, 0),
				"active": 1,
				"parent": None
			}, **prop)

			self.properties = prop

			# Setup rect.
			if not isinstance(prop["rect"], pygame.Rect):
				prop["rect"] = pygame.Rect(prop["rect"])

			# Setup child.
			list = "child" in prop and prop["child"] or []

			prop["child"] = {}

			for v in list:
				self.append(v)

			# Setup parent & zindex.
			list = prop["parent"] and prop["parent"].properties["child"] or kouhai.list

			if prop["zindex"] not in list:
				list[prop["zindex"]] = []

			list[prop["zindex"]].append(self)

		# Adopt the child.
		def append(self, v):
			prop = self.properties
			child = prop["child"]
			prop_c = v.properties
			list_c = prop_c["parent"] and prop_c["parent"].properties["child"] or kouhai.list
			zindex_c = prop_c["zindex"]

			# Remove from previous parent.
			list_c[zindex_c].remove(v)

			# Create list.
			if zindex_c not in child:
				child[zindex_c] = []

			# Make sure to add to the list first before setting the parent.
			child[zindex_c].append(v)

			prop_c["parent"] = self

		# Disown the child.
		def remove(self, v):
			list = kouhai.list
			prop = self.properties
			prop_c = v.properties
			zindex_c = prop_c["zindex"]

			if zindex_c in prop["child"] and v in prop["child"][zindex_c]:
				# Remove from previous parent.
				prop["child"][zindex_c].remove(v)

				# Create list.
				if zindex_c not in list:
					list[zindex_c] = []

				# Make sure to add to the list first before setting the parent.
				list[zindex_c].append(v)

				prop_c["parent"] = None

		# Set layer from parent.
		def set_zindex(self, v):
			prop = self.properties
			list = prop["parent"] and prop["parent"].properties["child"] or kouhai.list

			list[prop["zindex"]].remove(self)

			prop["zindex"] = v

			if v not in list:
				list[v] = []

			list[v].append(self)

		def set_rect(self, rect):
			if not isinstance(rect, pygame.Rect):
				rect = pygame.Rect(Rect)

			self.properties["rect"] = rect

		def set_active(self, v):
			self.properties["active"] = v

			if not v:
				if self in kouhai.hover:
					kouhai.hover.remove(self)
					self.fire("mouseleave")

				if kouhai.target == self:
					kouhai.target = None
					self.fire("untargeted")

				if kouhai.focus == self:
					kouhai.focus = None
					self.fire("unfocused")

		def set_focus(self, flag):
			if flag:
				prev = kouhai.focus
				kouhai.focus = self

				if prev:
					prev.fire("unfocused")

				self.fire("focused")
			elif kouhai.focus == self:
				kouhai.focus = None

				self.fire("unfocused")

		def is_hovered(self):
			return self in kouhai.hover

		def is_targeted(self):
			return self == kouhai.target

		def is_focused(self):
			return self == kouhai.focus

		def is_descendant(self, v):
			parent = self.properties["parent"]

			if parent:
				return parent == v or parent.is_descendant(v)

			return False

		def destroy(self):
			prop = self.properties
			list = prop["parent"] and prop["parent"].properties["child"] or kouhai.list

			if self in kouhai.hover:
				kouhai.hover.remove(self)
				self.fire("mouseleave")

			if kouhai.target == self:
				# Remove target.
				kouhai.target = None
				self.fire("untargeted")

			if kouhai.focus == self:
				kouhai.focus = None
				self.fire("unfocused")

			list[prop["zindex"]].remove(self)

	return this