from eregex.element import BasicElement
from eregex.parser import JoinParser, StringParser, SpacePlainParser, WordParser,\
	OptionalParser, OrParser
from eregex.locator import LineLocator

class ImportElement(BasicElement):
	def __init__(self, text, start, end, span, target, alias=None):
		super(ImportElement, self).__init__(text, start, end, span)
		self.target = target
		self.alias = alias

class ImportParser(object):
	def __init__(self):
		super(ImportParser, self).__init__()
		self.parser = JoinParser([
			SpacePlainParser("import"),
			StringParser(),
			OptionalParser(JoinParser([SpacePlainParser("as"), WordParser()])),
			SpacePlainParser(";")
		])

	def parse(self, text, pos):
		elem = self.parser.parse(text, pos)
		if elem is None:
			return None

		target, alias = elem[1], elem[2]
		if alias.content() == "":
			alias = None
		else:
			alias = alias[1]

		return ImportElement(text, elem.start, elem.end, elem.span, target, alias)


class PartOfElement(BasicElement):
	def __init__(self, text, start, end, span, target):
		super(PartOfElement, self).__init__(text, start, end, span)
		self.target = target

class PartOfParser(object):
	def __init__(self):
		super(PartOfParser, self).__init__()
		self.parser = JoinParser([
			OrParser([SpacePlainParser("part of"), SpacePlainParser("part")]),
			StringParser(),
			SpacePlainParser(";")
		])

	def parse(self, text, pos):
		elem = self.parser.parse(text, pos)
		if elem is None:
			return None

		target = elem[1]

		return PartOfElement(text, elem.start, elem.end, elem.span, target)

class ImportLocator(LineLocator):
	"""ImportLocator"""
	def __init__(self, indentation=""):
		super(ImportLocator, self).__init__(ImportParser(), indentation=indentation)

class PartLocator(LineLocator):
	"""PartLocator"""
	def __init__(self, indentation=""):
		super(PartLocator, self).__init__(PartLocator(), indentation=indentation)
