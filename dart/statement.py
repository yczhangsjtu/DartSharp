from eregex.element import BasicElement
from eregex.parser import WordDotParser, SpacePlainParser, JoinParser, OrParser
from eregex.locator import LineLocator
from dart.expression import FunctionInvocationParser, SimpleExpressionParser

class AssignmentElement(BasicElement):
	"""AssignmentElement"""
	def __init__(self, text, start, end, span, left, right):
		super(AssignmentElement, self).__init__(text, start, end, span)
		self.left = left
		self.right = right

class AssignmentParser(object):
	"""AssignmentParser"""
	def __init__(self):
		super(AssignmentParser, self).__init__()
		self.parser = JoinParser([WordDotParser(), SpacePlainParser("="), SimpleExpressionParser()])

	def parse(self, text, pos):
		elem = self.parser.parse(text, pos)
		if elem is None:
			return None

		return AssignmentElement(text, elem.start, elem.end, elem.span, elem[0], elem[2])

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
