from eregex.element import BasicElement
from eregex.parser import StringParser, BoolParser,\
	NumberParser, WordParser, OrParser


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
			WordParser(),
		])

	def parse(self, text, pos):
		elem = self.parser.parse(text, pos)
		if elem is None:
			return None

		return SimpleExpressionElement(elem)
