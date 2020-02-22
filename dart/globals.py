from eregex.element import BasicElement
from eregex.parser import JoinParser, StringParser, SpacePlainParser, WordParser,\
	OptionalParser, OrParser
from eregex.locator import LineLocator
from dart.function import FunctionHeaderParser

class ImportElement(BasicElement):
	def __init__(self, text, start, end, span, target, alias=None, show=None):
		super(ImportElement, self).__init__(text, start, end, span)
		self.target = target
		self.alias = alias
		self.show = show

	def package(self):
		return self.target.inside_content()

class ImportParser(object):
	def __init__(self):
		super(ImportParser, self).__init__()
		self.parser = JoinParser([
			SpacePlainParser("import"),
			StringParser(),
			OptionalParser(JoinParser([SpacePlainParser("as"), WordParser()])),
			OptionalParser(JoinParser([SpacePlainParser("show"), WordParser()])),
			SpacePlainParser(";")
		])

	def parse(self, text, pos):
		elem = self.parser.parse(text, pos)
		if elem is None:
			return None

		target, alias, show = elem[1], elem[2], elem[3]
		if alias.content() == "":
			alias = None
		else:
			alias = alias[1]
		if show.content() == "":
			show = None
		else:
			show = show[1]

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

class PartOfLocator(LineLocator):
	"""PartOfLocator"""
	def __init__(self, indentation=""):
		super(PartOfLocator, self).__init__(PartOfParser(), indentation=indentation)

class TypedefElement(BasicElement):
	"""TypedefElement"""
	def __init__(self, text, start, end, span, header):
		super(TypedefElement, self).__init__(text, start, end, span)
		self.header = header
		self.typename = header.typename
		self.name = header.name
		self.parameter_list = header.parameter_list

class TypedefParser(object):
	"""TypedefParser"""
	def __init__(self):
		super(TypedefParser, self).__init__()
		self.parser = JoinParser([
			SpacePlainParser("typedef"),
			FunctionHeaderParser(),
			SpacePlainParser(";")
		])

	def parse(self, text, pos):
		elem = self.parser.parse(text, pos)
		if elem is None:
			return None

		funcheader = elem[1]
		return TypedefElement(text, elem.start, elem.end, elem.span, funcheader)

class TypedefLocator(LineLocator):
	"""TypedefLocator"""
	def __init__(self, indentation=""):
		super(TypedefLocator, self).__init__(TypedefParser(), indentation=indentation)
