from eregex.element import *
from eregex.parser import *

class NormalParameterItemElement(BasicElement):
	"""docstring for ParameterItemElement"""
	def __init__(self, text, typename, name, default_value=None):
		end = name.end
		if default_value is not None:
			end = default_value.span[1]
		super(ParameterItemElement, self).__init__(text, typename.start, end, (typename.span[0], end))
		self.typename = typename
		self.name = name
		self.default_value = default_value

class NormalParameterItemParser(object):
	"""NormalParameterItemParser"""
	def __init__(self, arg):
		super(NormalParameterItemParser, self).__init__()
		self.parser = JoinParser([
			TypeNameParser(),
			SpaceParser(),
			WordParser(),
			OrParser([
				BasicParser()
			])
		])
