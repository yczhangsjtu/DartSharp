from eregex.element import BasicElement, JoinElement, ListElement
from eregex.parser import TypeNameParser,\
	SpaceParser, WordParser, OrParser, BasicParser,\
	JoinParser, SpacePlainParser, OptionalParser, ListParser,\
	EmptyParser, WordDotParser
from eregex.locator import Block, BlockLocator, locate_all
from dart.expression import SimpleExpressionParser, ForInLocator
from dart.variable import VariableDeclareLocator
from dart.statement import StatementLocator

class NormalParameterItemElement(BasicElement):
	"""NormalParameterItemElement"""
	def __init__(self, text, typename, name, default_value=None):
		end, spanend = name.end, name.span[1]
		if default_value is not None:
			end, spanend = default_value.end, default_value.span[1]

		super(NormalParameterItemElement, self).__init__(text, typename.start, end, (typename.span[0], spanend))
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

class FunctionalParameterItemElement(BasicElement):
	"""FunctionalParameterItemElement"""
	def __init__(self, text, function_header, default_value=None):
		end, spanend = function_header.end, function_header.span[1]
		if default_value is not None:
			end, spanend = default_value.end, default_value.span[1]
		super(FunctionalParameterItemElement, self).__init__(text, function_header.start, end, (function_header.span[0], spanend))
		self.function_header = function_header
		self.name = function_header.name
		self.typename = function_header.typename
		self.default_value = default_value

class FunctionalParameterItemParser(object):
	"""FunctionalParameterItemParser"""
	def __init__(self):
		super(FunctionalParameterItemParser, self).__init__()
		self.parser = JoinParser([
			FunctionHeaderParser(),
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

		if type(elem[1]) is JoinElement:
			default_value = elem[1][1]
		else:
			default_value = None

		return FunctionalParameterItemElement(
			text, elem[0], default_value
		)

class ParameterItemElement(BasicElement):
	def __init__(self, text, start, end, span, element, required=False):
		super(ParameterItemElement, self).__init__(text, start, end, span)
		self.element = element
		self.is_this = type(element) is ThisParameterItemElement
		if type(element) is NormalParameterItemElement or type(element) is FunctionalParameterItemElement:
			self.typename = element.typename
		else:
			self.typename = None
		self.name = element.name
		self.default_value = element.default_value
		self.required = required

class ConstructorParameterItemParser(object):
	"""ConstructorParameterItemParser"""
	def __init__(self):
		super(ConstructorParameterItemParser, self).__init__()
		self.parser = JoinParser([
			OptionalParser(JoinParser([SpacePlainParser("@"), WordDotParser()])),
			OrParser([
				FunctionalParameterItemParser(),
				NormalParameterItemParser(),
				ThisParameterItemParser(),
			])
		])

	def parse(self, text, pos):
		elem = self.parser.parse(text, pos)
		if elem is None:
			return None
		required = elem[0].content() != "" and elem[0][1].content() == "required"
		if required:
			start = elem[0].start
		else:
			start = elem[1].start
		return ParameterItemElement(text, start, elem.end, elem.span, elem[1], required)

class ParameterItemParser(object):
	"""ParameterItemParser"""
	def __init__(self):
		self.parser = JoinParser([
			OptionalParser(JoinParser([SpacePlainParser("@"), WordDotParser()])),
			OrParser([
				FunctionalParameterItemParser(),
				NormalParameterItemParser(),
			])
		])

	def parse(self, text, pos):
		elem = self.parser.parse(text, pos)
		if elem is None:
			return None

		required = elem[0].content() != "" and elem[0][1].content() == "required"
		if required:
			start = elem[0].start
		else:
			start = elem[1].start
		return ParameterItemElement(text, start, elem.end, elem.span, elem[1], required)

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
			TypeNameParser(),
			SpacePlainParser("("),
			ParameterListParser(),
			SpacePlainParser(")"),
		])

	def parse(self, text, pos):
		elem = self.parser.parse(text, pos)
		if elem is None:
			return None

		typename, name, parameter_list = elem[0], elem[2], elem[4]

		if typename.content() == "set":
			return None

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

class ConstructorHeaderElement(BasicElement):
	"""ConstructorHeaderElement"""
	def __init__(self, text, end, name, parameter_list, span):
		super(ConstructorHeaderElement, self).__init__(text, name.start, end, span)
		self.name = name
		self.parameter_list = parameter_list

class ConstructorHeaderParser(object):
	"""ConstructorHeaderParser"""
	def __init__(self, class_name):
		super(ConstructorHeaderParser, self).__init__()
		self.parser = JoinParser([
			SpacePlainParser(class_name),
			SpacePlainParser("("),
			ConstructorParameterListParser(),
			SpacePlainParser(")"),
		])

	def parse(self, text, pos):
		elem = self.parser.parse(text, pos)
		if elem is None:
			return None

		name, parameter_list = elem[0], elem[2]
		return ConstructorHeaderElement(text, elem.end, name, parameter_list, elem.span)

class FunctionModifierElement(BasicElement):
	"""docstring for FunctionModiferElement"""
	def __init__(self, text, start, end, span, modifiers):
		super(FunctionModifierElement, self).__init__(text, start, end, span)
		self.modifiers = modifiers

	def contains(self, modifier):
		if self.modifiers is None or len(self.modifiers) == 0:
			return False
		for m in self.modifiers:
			if m.content() == modifier:
				return True
		return False


class FunctionModifierParser(object):
	"""FunctionModifierParser"""
	def __init__(self):
		super(FunctionModifierParser, self).__init__()
		self.parser = OptionalParser(ListParser(
			JoinParser([SpacePlainParser("@"), WordParser()]),
			SpaceParser(),
			allow_trailing_seperater=False
		))

	def parse(self, text, pos):
		elem = self.parser.parse(text, pos)
		if elem is None:
			return None

		if isinstance(elem, ListElement):
			return FunctionModifierElement(text, elem.start, elem.end, elem.span,\
				list(map(lambda elem: elem[1], elem.elements)))

		return elem


class FunctionBlock(Block):
	"""FunctionBlock"""
	def __init__(self, text, start, end, indentation, header, inside_start, inside_end, is_arrow, modifiers,
			variable_declares=None, for_in_blocks=None, statements=None):
		super(FunctionBlock, self).__init__(text, start, end, indentation)
		self.header = header
		self.typename = header.typename
		self.name = header.name
		self.parameter_list = header.parameter_list
		self.inside_start = inside_start
		self.inside_end = inside_end
		self.is_arrow = is_arrow
		self.modifiers = modifiers
		self.override = False
		if modifiers is not None:
			self.override = self.modifiers.contains("override")
		self.variable_declares = variable_declares
		self.for_in_blocks = for_in_blocks
		self.statements = statements

	def inside_content(self):
		return self.text[self.inside_start:self.inside_end]

class FunctionLocator(object):
	"""FunctionLocator"""
	def __init__(self, outer_indentation="", inner_indentation="  "):
		super(FunctionLocator, self).__init__()
		self.brace_function_locator = BlockLocator(
			JoinParser([FunctionModifierParser(), FunctionHeaderParser(), SpacePlainParser("{")]),
			indentation=outer_indentation)
		self.arrow_function_locator = BlockLocator(
			JoinParser([FunctionModifierParser(), FunctionHeaderParser(), SpacePlainParser("=>")]),
			endchar=";",
			indentation=outer_indentation)
		self.variable_declare_locator = VariableDeclareLocator(indentation=outer_indentation+inner_indentation)
		self.for_in_locator = ForInLocator(outer_indentation=outer_indentation+inner_indentation, inner_indentation=inner_indentation)
		self.statement_locator = StatementLocator(indentation=outer_indentation+inner_indentation)

	def locate(self, text, pos):
		block = self.brace_function_locator.locate(text, pos)

		if block is None:
			block = self.arrow_function_locator.locate(text, pos)

		if block is None:
			return None

		return self.create_function_block(block)

	def locate_all(self, text, start=0, end=-1):
		return locate_all(self, text, start, end)

	def create_function_block(self, block):
		if isinstance(block.element[0], FunctionModifierElement):
			modifiers = block.element[0]
		else:
			modifiers = None

		body_starter = block.element[-1]
		is_arrow = body_starter.content() == "=>"
		inside_start = body_starter.span[1]
		if is_arrow:
			inside_end = block.end - 1
		else:
			inside_end = block.end - 2

		variable_declares = None
		if not is_arrow:
			variable_declares = self.variable_declare_locator.locate_all(block.text, block.start, block.end)
			if len(variable_declares) == 0:
				variable_declares = None

		for_in_blocks = None
		if not is_arrow:
			for_in_blocks = self.for_in_locator.locate_all(block.text, block.start, block.end)
			if len(for_in_blocks) == 0:
				for_in_blocks = None

		statements = None
		if not is_arrow:
			statements = self.statement_locator.locate_all(block.text, inside_start, inside_end)

		return FunctionBlock(block.text, block.start, block.end, block.indentation,\
			block.element[1], inside_start, inside_end, is_arrow, modifiers,\
			variable_declares, for_in_blocks, statements)

class ConstructorBlock(Block):
	"""ConstructorBlock"""
	def __init__(self, text, start, end, indentation, header,
			initializer_start=None, initializer_end=None, open_brace=None, close_brace=None):
		super(ConstructorBlock, self).__init__(text, start, end, indentation)
		self.header = header
		self.name = self.header.name
		self.parameter_list = self.header.parameter_list
		self.initializer_start = initializer_start
		self.initializer_end = initializer_end
		self.open_brace = open_brace
		self.close_brace = close_brace

	def initializer_content(self):
		if self.initializer_start is None or self.initializer_end is None:
			return None
		return self.text[self.initializer_start:self.initializer_end]

	def braced_content(self):
		if self.open_brace is None or self.close_brace is None:
			return None
		return self.text[self.open_brace+1:self.close_brace]

class ConstructorLocator(object):
	"""ConstructorLocator"""
	def __init__(self, name, outer_indentation="", inner_indentation="  "):
		super(ConstructorLocator, self).__init__()
		self.brace_locator = BlockLocator(
			JoinParser([ConstructorHeaderParser(name), OrParser([
				SpacePlainParser(":"),
				SpacePlainParser("{")
			])]),
			indentation=outer_indentation)
		self.no_brace_locator = BlockLocator(
			JoinParser([ConstructorHeaderParser(name), OptionalParser(
				SpacePlainParser(":")
			)]),
			endchar=";",
			indentation=outer_indentation)

	def locate(self, text, pos):
		block = self.brace_locator.locate(text, pos)

		if block is None:
			block = self.no_brace_locator.locate(text, pos)

		if block is None:
			return None

		return self.create_constructor_block(block)

	def locate_all(self, text, start=0, end=-1):
		return locate_all(self, text, start, end)

	def create_constructor_block(self, block):
		header = block.element[0]
		endchar = block.content().strip()[-1]
		if block.element[1].content() == ":":
			initializer_start = block.element[1].span[1]
		else:
			initializer_start = None
		initializer_end = None

		if endchar == ";":
			open_brace, close_brace = None, None
			if initializer_start is not None:
				initializer_end = block.end-1
		else:
			open_brace = block.text.find("{", header.span[1])
			if block.text[open_brace] != "{":
				raise Exception("Open brace { not found as expected!")
			if initializer_start is not None:
				initializer_end = open_brace
			close_brace = block.end-2

			if block.text[close_brace] != "}":
				raise Exception("Close brace } not found as expected!")

		return ConstructorBlock(block.text, block.start, block.end, block.indentation, header,
			initializer_start, initializer_end, open_brace, close_brace)

