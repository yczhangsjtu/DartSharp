import re

def next_line_start(text, pos):
	next_eol = text.find("\n", pos)
	if next_eol < 0:
		return len(text)
	return next_eol+1

def next_line_start_or_here(text, pos):
	"""Find next line start, or `pos` if `pos` is already a line start
	"""
	if pos == 0 or (pos-1 < len(text) and text[pos-1] == "\n"):
		return pos
	return next_line_start(text, pos)

spaces = re.compile(r"[ \t]*")
def indentation_at(text, pos):
	global spaces
	mat = spaces.match(text[pos:])
	return mat.group(0)

class Block:
	def __init__(self, text, start, end, indentation):
		self.text = text
		self.start = start
		self.end = end
		self.indentation = indentation

	def content(self):
		return self.text[self.start:self.end]

class BlockFinder(object):
	"""BlockFinder"""
	def __init__(self, parser, endline=None, endchar=None):
		super(BlockFinder, self).__init__()
		self.parser = parser
		self.endline = endline
		self.endchar = endchar

	def find_all(self, text, start=0, end=-1):
		if end < 0:
			end = len(text)

		curr, blocks = start, []
		while curr < end:
			elem = self.parser.parse(text, curr)
			if elem is None:
				curr = next_line_start(text, curr)
				continue

			indentation = indentation_at(text, curr)
			block_end = next_line_start_or_here(text, elem.span[1])
			while block_end < end:
				next_end = next_line_start(text, block_end)
				if next_end > end:
					break

				if text[block_end:next_end] == indentation + self.endline or\
					 text[block_end:next_end] == indentation + self.endline + "\n":
					blocks.append(Block(text, curr, next_end, indentation))
					curr = next_end
					break

				block_end = next_end

			if curr == elem.span[0]:
				curr = next_line_start(text, curr)

		return blocks

class LineFinder(object):
	"""LineFinder"""
	def __init__(self, parser, indentation=None):
		super(LineFinder, self).__init__()
		self.parser = parser
		self.indentation = indentation

	def find_all(self, text, start=0, end=-1):
		if end < 0:
			end = len(text)

		curr, elements = start, []
		while curr < end:
			elem = self.parser.parse(text, curr)
			if elem is None or (self.indentation != None and\
					indentation_at(text, curr) != self.indentation):
				curr = next_line_start(text, curr)
				continue

			if elem.span[1] > end:
				break

			elements.append(elem)
			curr = next_line_start_or_here(text, elem.span[1])

		return elements
