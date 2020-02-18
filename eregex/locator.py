import re

def next_line_start(text, pos):
	next_eol = text.find("\n", pos)
	if next_eol < 0:
		return len(text)
	return next_eol+1

def start_of_line(text, pos):
	if pos >= len(text):
		return len(text)
	while pos > 0:
		if text[pos-1] == "\n":
			return pos
		pos -= 1
	return 0

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

empty_line = re.compile(r"\n\s*\n")
def contains_empty_line(text):
	global empty_line
	return empty_line.search(text) is not None

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
	def __init__(self, parser, endline=None, endchar=None, indentation=None):
		super(BlockFinder, self).__init__()
		self.parser = parser
		if endline is None and endchar is None:
			endline = "}"
		self.endline = endline
		self.endchar = endchar
		self.indentation = indentation

	def find_at(self, text, pos):
		elem = self.parser.parse(text, pos)
		if elem is None:
			return None
		indentation = indentation_at(text, start_of_line(text, elem.start))
		if self.indentation is not None and self.indentation != indentation:
			return None

		if self.endline is not None:
			block_end = next_line_start_or_here(text, elem.span[1])
			while block_end < len(text):
				next_end = next_line_start(text, block_end)
				if text[block_end:next_end] == indentation + self.endline or\
					 text[block_end:next_end] == indentation + self.endline + "\n":
					return Block(text, pos, next_end, indentation)
				block_end = next_end
			return None

		end = text.find(self.endchar, elem.span[1])
		if end < 0:
			return None

		if contains_empty_line(text[elem.span[1]:end]):
			return None

		return Block(text, pos, end+1, indentation)

	def find_all(self, text, start=0, end=-1):
		if end < 0:
			end = len(text)

		curr, blocks = start, []
		while curr < end:
			block = self.find_at(text, curr)
			if block is None or block.end > end:
				curr = next_line_start(text, curr)
				continue

			blocks.append(block)
			curr = next_line_start_or_here(text, block.end)

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
