from eregex.element import BasicElement, JoinElement, ListElement
from eregex.parser import TypeNameParser,\
	SpaceParser, WordParser, OrParser, BasicParser,\
	JoinParser, SpacePlainParser, OptionalParser, ListParser,\
	EmptyParser
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
			text, elem[0].start, elem[1], default_value, (pos, elem[2].span[1])
		)

class ParameterItemElement(BasicElement):
	def __init__(self, element):
		super(ParameterItemElement, self).__init__(element.text, element.start, element.end, element.span)
		self.element = element
		self.is_this = type(element) is ThisParameterItemElement
		if type(element) is NormalParameterItemElement:
			self.typename = element.typename
		else:
			self.typename = None
		self.name = element.name
		self.default_value = element.default_value

class ConstructorParameterItemParser(object):
	"""ConstructorParameterItemParser"""
	def __init__(self):
		super(ConstructorParameterItemParser, self).__init__()
		self.parser = OrParser([
			NormalParameterItemParser(),
			ThisParameterItemParser(),
			FunctionHeaderParser(),
		])

	def parse(self, text, pos):
		elem = self.parser.parse(text, pos)
		if elem is None:
			return None
		return ParameterItemElement(elem)

class ParameterItemParser(object):
	"""ParameterItemParser"""
	def __init__(self):
		super(ParameterItemParser, self).__init__()
		self.parser = OrParser([
			NormalParameterItemParser(),
			FunctionHeaderParser(),
		])

	def parse(self, text, pos):
		elem = self.parser.parse(text, pos)
		if elem is None:
			return None
		return ParameterItemElement(elem)

class SingleParameterListElement(ListElement):
	def __init__(self, text, parameters, span=None, has_trailing_comma=False, has_curly_brace=False, start=None, end=None):
		super(SingleParameterListElement, self).__init__(text, parameters, span, has_trailing_comma, start, end)
		self.has_trailing_comma = has_trailing_comma
		self.has_curly_brace = has_curly_brace

class SingleParameterListParser(object):
	"""SingleParameterListParser"""
	def __init__(self, item_parser=None, allow_trailing_comma=True, curly_brace=False):
		super(SingleParameterListParser, self).__init__()
		if curly_brace:
			prefix, postfix = SpacePlainParser("{"), SpacePlainParser("}")
		else:
			prefix, postfix = None, None
		if item_parser is None:
			item_parser = ParameterItemParser()

		self.parser = ListParser(
			item_parser,
			SpacePlainParser(","),
			allow_trailing_seperater = allow_trailing_comma,
			prefix = prefix,
			postfix = postfix
		)
		self.curly_brace = curly_brace

	def parse(self, text, pos):
		elem = self.parser.parse(text, pos)
		if elem is None:
			return None

		return SingleParameterListElement(text,
			elem.elements,
			elem.span,
			elem.has_trailing_seperater,
			self.curly_brace,
			start = elem.start,
			end = elem.end)

class ConstructorSingleParameterListParser(SingleParameterListParser):
	"""ConstructorSingleParameterListParser"""
	def __init__(self, allow_trailing_comma=True, curly_brace=False):
		super(ConstructorSingleParameterListParser, self).__init__(
			ConstructorParameterItemParser(),
			allow_trailing_comma, curly_brace)

class ParameterListElement(BasicElement):
	"""ParameterListElement"""
	def __init__(self, text, start, end, positioned, named, span=None):
		if span is None:
			span = (start, end)
		super(ParameterListElement, self).__init__(text, start, end, span)
		self.positioned = positioned
		self.named = named

class ParameterListParser(object):
	"""ParameterListParser"""
	def __init__(self, is_constructor=False):
		super(ParameterListParser, self).__init__()

		if is_constructor:
			self.parser = OrParser([
				JoinParser([
					ConstructorSingleParameterListParser(allow_trailing_comma=False),
					SpacePlainParser(","),
					ConstructorSingleParameterListParser(curly_brace=True),
				]),
				ConstructorSingleParameterListParser(),
				ConstructorSingleParameterListParser(curly_brace=True),
				EmptyParser()
			])
		else:
			self.parser = OrParser([
				JoinParser([
					SingleParameterListParser(allow_trailing_comma=False),
					SpacePlainParser(","),
					SingleParameterListParser(curly_brace=True),
				]),
				SingleParameterListParser(),
				SingleParameterListParser(curly_brace=True),
				EmptyParser()
			])

	def parse(self, text, pos):
		elem = self.parser.parse(text, pos)
		if elem is None:
			return None

		start, end, span, positioned, named = elem.start, elem.end, elem.span, None, None

		if type(elem) is JoinElement:
			start, end, positioned, named = elem[0].start, elem[2].end, elem[0], elem[2]

		elif type(elem) is SingleParameterListElement:
			if elem.has_curly_brace:
				named = elem
			else:
				positioned = elem

		return ParameterListElement(text, start, end, positioned, named, span)

class ConstructorParameterListParser(ParameterListParser):
	"""ConstructorParameterListParser"""
	def __init__(self):
		super(ConstructorParameterListParser, self).__init__(is_constructor=True)


class FunctionHeaderElement(BasicElement):
	"""docstring for FunctionHeaderElement"""
	def __init__(self, text, end, typename, name, parameter_list, span):
		super(FunctionHeaderElement, self).__init__(text, typename.start, end, span)
		self.typename = typename
		self.name = name
		self.parameter_list = parameter_list

_function_header_parser = None
class _FunctionHeaderParser(object):
	"""_FunctionHeaderParser"""
	def __init__(self):
		super(_FunctionHeaderParser, self).__init__()
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

class FunctionHeaderParser(object):
	"""FunctionHeaderParser"""
	def __init__(self):
		super(FunctionHeaderParser, self).__init__()

	def parse(self, text, pos):
		global _function_header_parser
		if _function_header_parser is None:
			_function_header_parser = _FunctionHeaderParser()
		return _function_header_parser.parse(text, pos)
