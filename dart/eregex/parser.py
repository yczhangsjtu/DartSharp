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

		if len(m.groups()) < 1:
			return BasicElement(text, pos, m.end() + pos)

		return BasicElement(text, m.start(1) + pos, m.end(1) + pos, (pos, m.end() + pos))

class _WordParser(object):
	def __init__(self):
		super(_WordParser, self).__init__()
		self.basic_parser = BasicParser(r"\s*\b([_A-Za-z]\w*)\b")

	def parse(self, text, pos):
		basic_elem = self.basic_parser.parse(text, pos)
		if basic_elem is None:
			return None
		return WordElement(text, basic_elem.start, basic_elem.end, basic_elem.span)

_word_parser = None
class WordParser:
	"""Parse words in text at given position, get a WordElement"""
	def __init__(self):
		global _word_parser
		if _word_parser is None:
			_word_parser = _WordParser()

	def parse(self, text, pos):
		global _word_parser
		return _word_parser.parse(text, pos)



class PlainParser(object):
	"""Parse plain text at given position, get a basic element"""
	def __init__(self, pattern):
		super(PlainParser, self).__init__()
		self.pattern = pattern

	def parse(self, text, pos):
		if pos >= len(text):
			return None

		if self.pattern is None or len(self.pattern) + pos > len(text):
			return None

		if text[pos:pos+len(self.pattern)] != self.pattern:
			return None

		return BasicElement(text, pos, pos + len(self.pattern))

class SpacePlainParser(object):
	"""Parse plain text after zero or more spaces"""
	def __init__(self, pattern):
		super(SpacePlainParser, self).__init__()
		self.pattern = pattern

	def parse(self, text, pos):
		if pos >= len(text):
			return None

		if self.pattern is None:
			return None

		curr = pos
		while curr < len(text) and text[curr] in " \n\t\r":
			curr += 1

		if len(self.pattern) + curr > len(text):
			return None

		if text[curr:curr+len(self.pattern)] != self.pattern:
			return None

		return BasicElement(text, curr, curr + len(self.pattern), (pos, curr + len(self.pattern)))

class SpaceParser(object):
	"""SpaceParser"""
	def __init__(self):
		super(SpaceParser, self).__init__()
		self.parser = BasicParser(r"\s+")

	def parse(self, text, pos):
		return self.parser.parse(text, pos)


class JoinParser(object):
	"""Given a list of parsers, join them to a new parser,
	which will parse contents connected by the single parsers"""
	def __init__(self, parsers):
		super(JoinParser, self).__init__()
		self.parsers = parsers

	def parse(self, text, pos):
		if self.parsers is None or len(self.parsers) == 0:
			return None

		elements = []
		curr = pos
		for parser in self.parsers:
			elem = parser.parse(text, curr)
			if elem is None:
				return None
			elements.append(elem)
			curr = elem.span[1]

		return JoinElement(text, elements, (pos, curr))

class OrParser(object):
	"""OrParser, given a list of parsers, try to parse the text
	with each of them in order, and return the first match, or return
	None if none of them matches"""
	def __init__(self, parsers):
		super(OrParser, self).__init__()
		self.parsers = parsers

	def parse(self, text, pos):
		if self.parsers is None or len(self.parsers) == 0:
			return None

		for parser in self.parsers:
			elem = parser.parse(text, pos)
			if elem is not None:
				return elem

		return None

class _StringParser(object):
	def __init__(self):
		super(_StringParser, self).__init__()

	def parse(self, text, pos):
		curr = pos

		# Skip the spaces
		while curr < len(text) and text[curr] in " \t\n\r":
			curr += 1

		if curr >= len(text) or (text[curr] != "\"" and text[curr] != "'"):
			return None

		start = curr
		mark = text[curr]
		slash_open = False
		curr += 1

		while curr < len(text):
			while curr < len(text) and (slash_open or (text[curr] != "\\" and text[curr] != mark)):
				slash_open = False
				curr += 1

			if curr >= len(text):
				return None

			if text[curr] == "\\":
				slash_open = True

			if text[curr] == mark:
				return StringElement(text, start, curr+1, (pos, curr+1))

			curr += 1

		return None

_string_parser = None
class StringParser:
	"""StringParser finds next complete string"""
	def __init__(self):
		global _string_parser
		if _string_parser is None:
			_string_parser = _StringParser()

	def parse(self, text, pos):
		global _string_parser
		return _string_parser.parse(text, pos)

class _NumberParser(object):
	def __init__(self):
		super(_NumberParser, self).__init__()
		self.parser = re.compile(r"\s*(-?\d+)(?:\.(\d+))?")

	def parse(self, text, pos):

		if pos >= len(text):
			return None

		m = self.parser.match(text[pos:])

		if m is None:
			return None

		return NumberElement(
			text,
			m.start(1)+pos,
			max(m.end(1)+pos, m.end(2)+pos),
			m.group(1),
			m.group(2),
			(m.start(0)+pos, m.end(0)+pos)
		)

_number_parser = None
class NumberParser:
	"""NumberParser recognize numbers"""
	def __init__(self):
		global _number_parser
		if _number_parser is None:
			_number_parser = _NumberParser()

	def parse(self, text, pos):
		global _number_parser
		return _number_parser.parse(text, pos)

class ListParser(object):
	"""ListParser identifies a list of items of the same type,
	which are separated by items of the same type"""
	def __init__(self, item_parser,
			seperater_parser,
			allow_trailing_seperater=True,
			prefix=None,
			postfix=None):
		super(ListParser, self).__init__()
		self.item_parser = item_parser
		self.seperater_parser = seperater_parser
		self.allow_trailing_seperater = allow_trailing_seperater
		self.prefix = prefix
		self.postfix = postfix

	def parse(self, text, pos):
		curr = pos
		elements = []
		has_trailing = False

		if self.prefix is not None:
			pre = self.prefix.parse(text, curr)
			if pre is None:
				return None
			curr = pre.span[1]

		while True:
			elem = self.item_parser.parse(text, curr)
			if elem is None:
				if self.allow_trailing_seperater:
					has_trailing = True
					break
				return None

			elements.append(elem)
			curr = elem.span[1]

			elem = self.seperater_parser.parse(text, curr)
			if elem is None:
				break

			curr = elem.span[1]

		if len(elements) == 0 and (self.prefix is None or self.postfix is None):
			return None

		if self.postfix is not None:
			post = self.postfix.parse(text, curr)
			if post is None:
				return None
			curr = post.span[1]

		return ListElement(text, elements, (pos, curr), has_trailing)

class _TypeNameParser(object):
	def __init__(self):
		super(_TypeNameParser, self).__init__()
		self.parser = OrParser([
			JoinParser([
				WordParser(),
				ListParser(
					self,
					SpacePlainParser(","),
					prefix = SpacePlainParser("<"),
					postfix = SpacePlainParser(">")
				)
			]),
			WordParser()
		])

	def parse(self, text, pos):
		elem = self.parser.parse(text, pos)
		if elem is None:
			return None

		if type(elem) is WordElement:
			return TypeNameElement(text, elem, span=elem.span)

		if type(elem) is JoinElement:
			if len(elem) != 2:
				raise Exception("This element should contain two sub-elements: a word and a list")

			return TypeNameElement(text, elem[0], elem[1], elem.span)

		raise Exception("This element should be either WordElement or JoinElement")

_typename_parser = None
class TypeNameParser:
	"""TypeNameParser recognizes type names"""
	def __init__(self):
		global _typename_parser
		if _typename_parser is None:
			_typename_parser = _TypeNameParser()

	def parse(self, text, pos):
		global _typename_parser
		return _typename_parser.parse(text, pos)