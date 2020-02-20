from eregex.element import BasicElement
from eregex.parser import JoinParser, StringParser, SpacePlainParser, WordParser,\
	OptionalParser

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