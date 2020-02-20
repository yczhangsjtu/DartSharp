from eregex.element import BasicElement
from eregex.parser import StringParser, BoolParser,\
	NumberParser, OrParser, WordDotParser, JoinParser,\
	TypeNameParser, SpacePlainParser, OptionalParser,\
	ListParser


class FunctionInvocationElement(BasicElement):
	def __init__(self, text, start, end, span, name, arguments=None):
		super(FunctionInvocationElement, self).__init__(text, start, end, span)
		self.name = name
		self.arguments = arguments

class FunctionInvocationParser(object):
	def __init__(self):
		self.parser = None
	def parse(self, text, pos):
		if self.parser is None:
			self.parser = JoinParser([
				TypeNameParser(),
				SpacePlainParser("("),
				OptionalParser(ListParser(SimpleExpressionParser(), SpacePlainParser(","))),
				SpacePlainParser(")")
			])
		elem = self.parser.parse(text, pos)
		if elem is None:
			return elem

		func_name, arguments = elem[0], elem[2]
		if arguments.content() == "":
			arguments = None

		return FunctionInvocationElement(text, elem.start, elem.end, elem.span, func_name, arguments)

class SimpleExpressionElement(BasicElement):
	"""SimpleExpressionElement"""
	def __init__(self, element):
		super(SimpleExpressionElement, self).__init__(element.text, element.start, element.end, element.span)
		self.expression = element

class SimpleExpressionParser(object):
	"""SimpleExpressionParser recognizes numbers, booleans or strings"""
	def __init__(self):
		super(SimpleExpressionParser, self).__init__()
		self.parser = OrParser([
			StringParser(),
			BoolParser(),
			NumberParser(),
			WordDotParser(),
		])

	def parse(self, text, pos):
		elem = self.parser.parse(text, pos)
		if elem is None:
			return None

		return SimpleExpressionElement(elem)

