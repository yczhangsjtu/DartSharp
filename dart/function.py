from dart.parameter import ParameterItemElement, ParameterItemParser,\
	ParameterListParser
from eregex.parser import OptionalParser, SpaceParser, TypeNameParser,\
	WordParser, SpacePlainParser, JoinParser
from eregex.element import BasicElement

class FunctionHeaderElement(BasicElement):
	"""docstring for FunctionHeaderElement"""
	def __init__(self, text, end, typename, name, parameter_list, span):
		super(FunctionHeaderElement, self).__init__(text, typename.start, end, span)
		self.typename = typename
		self.name = name
		self.parameter_list = parameter_list


class FunctionHeaderParser(object):
	"""FunctionHeaderParser"""
	def __init__(self):
		super(FunctionHeaderParser, self).__init__()
		self.parser = JoinParser([
			TypeNameParser(),
			SpaceParser(),
			WordParser(),
			SpacePlainParser("("),
			ParameterListParser(),
			SpacePlainParser(")"),
		])

	def parse(self, text, pos):
		elem = self.parser.parse(text, pos)
		if elem is None:
			return None

		typename, name, parameter_list = elem[0], elem[2], elem[4]
		return FunctionHeaderElement(text, elem.end, typename, name, parameter_list, elem.span)
