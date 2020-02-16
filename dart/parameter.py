from eregex.element import BasicElement, JoinElement
from eregex.parser import TypeNameParser,\
	SpaceParser, WordParser, OrParser, BasicParser,\
	JoinParser, SpacePlainParser, OptionalParser
from dart.expression import SimpleExpressionParser

class NormalParameterItemElement(BasicElement):
	"""NormalParameterItemElement"""
	def __init__(self, text, typename, name, default_value=None):
		end = name.end
		if default_value is not None:
			end = default_value.span[1]
		super(NormalParameterItemElement, self).__init__(text, typename.start, end, (typename.span[0], end))
		self.typename = typename
		self.name = name
		self.default_value = default_value

class NormalParameterItemParser(object):
	"""NormalParameterItemParser"""
	def __init__(self):
		super(NormalParameterItemParser, self).__init__()
		self.parser = JoinParser([
			TypeNameParser(),
			SpaceParser(),
			WordParser(),
			OptionalParser(
				JoinParser([
					SpacePlainParser("="),
					SimpleExpressionParser()
				])
			)
		])

	def parse(self, text, pos):
		elem = self.parser.parse(text, pos)
		if elem is None:
			return None

		if type(elem[3]) is JoinElement:
			default_value = elem[3][1]
		else:
			default_value = None

		return NormalParameterItemElement(
			text, elem[0], elem[2], default_value
		)


class ThisParameterItemElement(BasicElement):
	"""ThisParameterItemElement"""
	def __init__(self, text, start, name, default_value=None, span=None):
		end = name.end
		if default_value is not None:
			end = default_value.span[1]

		super(ThisParameterItemElement, self).__init__(text, start, end, span)
		self.name = name
		self.default_value = default_value

class ThisParameterItemParser(object):
	"""ThisParameterItemParser"""
	def __init__(self):
		super(ThisParameterItemParser, self).__init__()
		self.parser = JoinParser([
			SpacePlainParser("this."),
			WordParser(),
			OptionalParser(
				JoinParser([
					SpacePlainParser("="),
					SimpleExpressionParser()
				])
			)
		])

	def parse(self, text, pos):
		elem = self.parser.parse(text, pos)
		if elem is None:
			return None

		if type(elem[2]) is JoinElement:
			default_value = elem[2][1]
		else:
			default_value = None

		return ThisParameterItemElement(
			text, elem[0].start, elem[1], default_value, (pos, elem[2].end)
		)
