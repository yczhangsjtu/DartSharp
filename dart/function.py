from parameter import ParameterItemElement, ParameterItemParser, ParameterListParser
from eregex.parser import OptionalParser, SpaceParser, TypeNameParser,\
	WordParser, SpacePlainParser

class FunctionHeaderElement(object):
	"""FunctionHeaderElement"""
	def __init__(self):
		super(FunctionHeaderElement, self).__init__()
		self.parser = JoinParser([
			OptionalParser(TypeNameParser()),
			SpaceParser(),
			WordParser(),
			SpacePlainParser("("),
		])
