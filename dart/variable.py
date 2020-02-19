from eregex.element import BasicElement, SpacePlainElement
from eregex.parser import TypeNameParser, WordParser, SpacePlainParser,\
	OrParser, OptionalParser, JoinParser
from eregex.locator import LineLocator
from dart.expression import SimpleExpressionParser

class VariableSimpleDeclareElement(BasicElement):
	"""VariableSimpleDeclareElement: [final/var/const] [typename] varname[ = simple expression];
	where at least one of [final/var/const] or [typename] should exist, and at least one
	of [typename] and default value should exist"""
	def __init__(self, text, start, end, span, modifier, typename, name, default_value=None):
		super(VariableSimpleDeclareElement, self).__init__(text, start, end, span)
		self.modifier = modifier
		self.typename = typename
		self.name = name
		self.default_value = default_value

class VariableSimpleDeclareParser(object):
	"""VariableSimpleDeclareParser"""
	def __init__(self):
		super(VariableSimpleDeclareParser, self).__init__()
		self.modifier_parser = OrParser([
			SpacePlainParser("final"),
			SpacePlainParser("var"),
			SpacePlainParser("const")
		])
		self.declare_parser = OrParser([
			JoinParser([
				self.modifier_parser,
				TypeNameParser(),
				WordParser(),
			]),
			JoinParser([
				self.modifier_parser,
				WordParser(),
			]),
			JoinParser([
				TypeNameParser(),
				WordParser(),
			]),
		])
		self.parser = JoinParser([
			self.declare_parser,
			OptionalParser(JoinParser([
				SpacePlainParser("="),
				SimpleExpressionParser()
			])),
			SpacePlainParser(";")
		])

	def parse(self, text, pos):
		elem = self.parser.parse(text, pos)
		if elem is None:
			return None

		declare, default_value, semicolon = elem[0], elem[1], elem[2]

		modifier, typename, name = None, None, None
		if len(declare) == 3:
			modifier, typename, name = declare[0], declare[1], declare[2]
		elif isinstance(declare[0], SpacePlainElement):
			modifier, name = declare[0], declare[1]
		else:
			typename, name = declare[0], declare[1]

		if typename is not None and\
			(typename.content() == "final" or\
			typename.content() == "var" or\
			typename.content() == "const"):
			return None

		if default_value.content() == "":
			default_value = None
		else:
			default_value.start = default_value[1].start
			default_value.end = default_value[1].end

		if typename is None and default_value is None:
			return None

		return VariableSimpleDeclareElement(text, elem.start, elem.end, elem.span,
			modifier, typename, name, default_value)

class VariableDeclareLocator(LineLocator):
	"""VariableDeclareLocator"""
	def __init__(self, indentation=""):
		super(VariableDeclareLocator, self).__init__(VariableSimpleDeclareParser(), indentation=indentation)
