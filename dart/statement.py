from eregex.element import BasicElement
from eregex.parser import WordDotParser, SpacePlainParser, JoinParser, OrParser
from eregex.locator import LineLocator
from dart.expression import FunctionInvocationParser, SimpleExpressionParser,\
	AssignmentParser


class StatementElement(BasicElement):
	"""StatementElement"""
	def __init__(self, text, start, end, span, element):
		super(StatementElement, self).__init__(text, start, end, span)
		self.element = element

class StatementParser(object):
	def __init__(self):
		super(StatementParser, self).__init__()
		self.parser = JoinParser([OrParser([
			AssignmentParser(),
			FunctionInvocationParser()
		]), SpacePlainParser(";")])

	def parse(self, text, pos):
		elem = self.parser.parse(text, pos)
		if elem is None:
			return elem

		return StatementElement(text, elem.start, elem.end, elem.span, elem[0])

class StatementLocator(LineLocator):
	"""StatementLocator"""
	def __init__(self, indentation=""):
		super(StatementLocator, self).__init__(StatementParser(), indentation=indentation)
