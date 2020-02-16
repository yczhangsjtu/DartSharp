import re
from element import *

class BasicParser:

	def __init__(self, pattern):

		self.pattern = re.compile(pattern)

	def parse(self, text, pos):

		if pos >= len(text):
			return None

		m = self.pattern.match(text[pos:])
		if m is None:
			return None

		return BasicElement(text, m.start(1) + pos, m.end(1) + pos)

class WordParser(object):
	"""Parse words in text at given position"""
	def __init__(self):
		super(WordParser, self).__init__()
		self.basic_parser = BasicParser(r"\s*\b([_A-Za-z]\w*)\b")

	def parse(self, text, pos):
		basic_elem = self.basic_parser.parse(text, pos)
		if basic_elem is None:
			return None
		return WordElement(text, basic_elem.start, basic_elem.end)
