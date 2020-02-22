from eregex.element import BasicElement, JoinElement
from eregex.parser import StringParser, BoolParser,\
	NumberParser, OrParser, WordDotParser, JoinParser,\
	TypeNameParser, SpacePlainParser, OptionalParser,\
	ListParser, EmptyParser, WordParser, SpaceParser
from eregex.locator import Block, BlockLocator, locate_all

def is_capitalized(word):
	if word is None or word == "":
		return False

	if ord(word[0]) >= ord("A") and ord(word[0]) <= ord("Z"):
		return True

	if word[0] == "_" and len(word) > 1:
		if ord(word[1]) >= ord("A") and ord(word[1]) <= ord("Z"):
			return True

	return False

class ArgumentElement(BasicElement):
	def __init__(self, text, start, end, span, value, name=None):
		super(ArgumentElement, self).__init__(text, start, end, span)
		self.value = value
		self.name = name

class ArgumentParser(object):
	"""ArgumentParser"""
	def __init__(self):
		super(ArgumentParser, self).__init__()
		self.parser = JoinParser([
			OptionalParser(JoinParser([WordParser(), SpacePlainParser(":")])),
			SimpleExpressionParser()])

	def parse(self, text, pos):
		elem = self.parser.parse(text, pos)
		if elem is None:
			return None

		name, value = elem[0], elem[1]
		if name.content() == "":
			name, start = None, value.start
		else:
			name, start = name[0], elem.start

		return ArgumentElement(text, start, elem.end, elem.span, value, name)

class FunctionInvocationElement(BasicElement):
	def __init__(self, text, start, end, span, name, arguments=None, modifier=None):
		super(FunctionInvocationElement, self).__init__(text, start, end, span)
		self.name = name
		self.arguments = arguments
		self.modifier = modifier

	def name_without_template(self):
		return self.name.name.content()

	def pure_name(self):
		return self.name_without_template().split(".")[-1]

	def possible_class_name(self):
		parts = self.name_without_template().split(".")
		if len(parts) > 1 and is_capitalized(parts[-2]):
			return ".".join(parts[:-1])
		return None

class FunctionInvocationParser(object):
	def __init__(self):
		self.parser = None
	def parse(self, text, pos):
		if self.parser is None:
			self.parser = JoinParser([
				OrParser([SpacePlainParser("const"), SpacePlainParser("new"), EmptyParser()]),
				TypeNameParser(),
				SpacePlainParser("("),
				OptionalParser(ListParser(ArgumentParser(), SpacePlainParser(","))),
				SpacePlainParser(")")
			])
		elem = self.parser.parse(text, pos)
		if elem is None:
			return elem

		modifier, func_name, arguments = elem[0], elem[1], elem[3]

		if modifier.content() == "":
			start = func_name.start
			modifier = None
		else:
			start = elem.start

		if arguments.content() == "":
			arguments = None

		return FunctionInvocationElement(text, start, elem.end, elem.span, func_name, arguments, modifier)

class DartListElement(BasicElement):
	def __init__(self, text, start, end, span, typename=None, elements=None,
			bracket=None, open_bracket=None, close_bracket=None):
		super(DartListElement, self).__init__(text, start, end, span)
		self.typename = typename
		self.elements = elements
		self.bracket = bracket
		self.open_bracket = open_bracket
		self.close_bracket = close_bracket

class DartListParser(object):
	def __init__(self):
		self.parser = None

	def parse(self, text, pos):
		if self.parser is None:
			self.parser = JoinParser([
				OptionalParser(JoinParser([SpacePlainParser("<"), TypeNameParser(), SpacePlainParser(">")])),
				SpacePlainParser("["),
				OptionalParser(ListParser(SimpleExpressionParser(), SpacePlainParser(","))),
				SpacePlainParser("]")
			])

		elem = self.parser.parse(text, pos)
		if elem is None:
			return elem

		if elem[0].content() == "":
			typename, bracket = None, None
			start = elem[1].start
		else:
			typename = elem[0][1]
			start = elem.start
			bracket = elem[0]

		open_bracket, close_bracket = elem[1], elem[3]

		if elem[2].content() == "":
			elements = None
		else:
			elements = elem[2]

		return DartListElement(text, start, elem.end, elem.span, typename, elements, bracket, open_bracket, close_bracket)

class RecursiveCounter:
	def __init__(self, double_dot_level, double_question_mark_level):
		self.double_dot_level = double_dot_level
		self.double_question_mark_level = double_question_mark_level

	def reduce_double_dot_level(self):
		return RecursiveCounter(
			self.double_dot_level-1,
			self.double_question_mark_level,
		)

	def reduce_questoin_mark_level(self):
		return RecursiveCounter(
			self.double_dot_level,
			self.double_question_mark_level-1,
		)

class AssignmentElement(BasicElement):
	"""AssignmentElement"""
	def __init__(self, text, start, end, span, left, right, sign):
		super(AssignmentElement, self).__init__(text, start, end, span)
		self.left = left
		self.right = right
		self.sign = sign

class AssignmentParser(object):
	"""AssignmentParser"""
	def __init__(self, counter=RecursiveCounter(0,1)):
		super(AssignmentParser, self).__init__()
		self.parser = JoinParser([
			WordDotParser(),
			OrParser([SpacePlainParser("="), SpacePlainParser("??=")]),
			SimpleExpressionParser(counter=counter)
		])

	def parse(self, text, pos):
		elem = self.parser.parse(text, pos)
		if elem is None:
			return None

		return AssignmentElement(text, elem.start, elem.end, elem.span, elem[0], elem[2], elem[1])

class DoubleDotElement(BasicElement):
	def __init__(self, text, start, end, span, expression, arms):
		super(DoubleDotElement, self).__init__(text, start, end, span)
		self.expression = expression
		self.arms = arms

class DoubleDotParser(object):
	def __init__(self, counter):
		super(DoubleDotParser, self).__init__()
		self.parser = None
		self.counter = counter

	def parse(self, text, pos):
		if self.parser is None:
			self.parser = JoinParser([
				SimpleExpressionParser(counter=self.counter.reduce_double_dot_level()),
				ListParser(
					JoinParser([
						SpacePlainParser(".."),
						OrParser([
							AssignmentParser(),
							FunctionInvocationParser(),
						])
					]),
					SpaceParser(),
				)
			])
		elem = self.parser.parse(text, pos)
		if elem is None:
			return elem

		return DoubleDotElement(text, elem.start, elem.end, elem.span, elem[0], elem[1])

class DoubleQuestionMarkElement(BasicElement):
	def __init__(self, text, start, end, span, left, right):
		super(DoubleQuestionMarkElement, self).__init__(text, start, end, span)
		self.left = left
		self.right = right

class DoubleQuesionMarkParser(object):
	def __init__(self, counter):
		super(DoubleQuesionMarkParser, self).__init__()
		self.parser = None
		self.counter = counter

	def parse(self, text, pos):
		if self.parser is None:
			self.parser = JoinParser([
				SimpleExpressionParser(counter=self.counter.reduce_questoin_mark_level()),
				SpacePlainParser("??"),
				SimpleExpressionParser(counter=self.counter.reduce_questoin_mark_level())
			])
		elem = self.parser.parse(text, pos)
		if elem is None:
			return elem

		return DoubleQuestionMarkElement(text, elem.start, elem.end, elem.span, elem[0], elem[1])

class SimpleExpressionElement(BasicElement):
	"""SimpleExpressionElement"""
	def __init__(self, element):
		super(SimpleExpressionElement, self).__init__(element.text, element.start, element.end, element.span)
		self.expression = element

class SimpleExpressionParser(object):
	"""SimpleExpressionParser recognizes numbers, booleans or strings"""
	def __init__(self, counter=RecursiveCounter(1,1)):
		super(SimpleExpressionParser, self).__init__()
		options = []
		if counter.double_dot_level > 0:
			options.append(DoubleDotParser(counter))
		if counter.double_question_mark_level > 0:
			options.append(DoubleQuesionMarkParser(counter))
		options.append(FunctionInvocationParser())
		options.append(StringParser())
		options.append(BoolParser())
		options.append(NumberParser())
		options.append(WordDotParser())
		options.append(DartListParser())
		self.parser = OrParser(options)

	def parse(self, text, pos):
		elem = self.parser.parse(text, pos)
		if elem is None:
			return None

		return SimpleExpressionElement(elem)

class ForInHeaderElement(BasicElement):
	"""ForInHeaderElement"""
	def __init__(self, text, start, end, span, typename, variable, collection):
		super(ForInHeaderElement, self).__init__(text, start, end, span)
		self.typename = typename
		self.variable = variable
		self.collection = collection

class ForInHeaderParser(object):
	def __init__(self):
		super(ForInHeaderParser, self).__init__()
		self.parser = JoinParser([
			SpacePlainParser("for"),
			SpacePlainParser("("),
			TypeNameParser(),
			WordParser(),
			SpacePlainParser("in"),
			SimpleExpressionParser(),
			SpacePlainParser(")")
		])

	def parse(self,text, pos):
		elem = self.parser.parse(text, pos)
		if elem is None:
			return None

		return ForInHeaderElement(text, elem.start, elem.end, elem.span, elem[2], elem[3], elem[5])

class ForInBlock(Block):
	"""ForInBlock"""
	def __init__(self, text, start, end, indentation, header, inside_start, inside_end, for_in_blocks):
		super(ForInBlock, self).__init__(text, start, end, indentation)
		self.header = header
		self.typename = header.typename
		self.variable = header.variable
		self.collection = header.collection
		self.for_in_blocks = for_in_blocks

class ForInLocator(object):
	"""ForInLocator"""
	def __init__(self, outer_indentation="", inner_indentation="  "):
		super(ForInLocator, self).__init__()
		self.brace_locator = BlockLocator(
			JoinParser([ForInHeaderParser(), SpacePlainParser("{")]),
			indentation=outer_indentation)
		self.no_brace_locator = BlockLocator(ForInHeaderParser(),
			endchar=";",
			indentation=outer_indentation)
		self.inner_indentation = inner_indentation
		self.outer_indentation = outer_indentation

	def locate(self, text, pos):
		block = self.brace_locator.locate(text, pos)

		if block is None:
			block = self.no_brace_locator.locate(text, pos)

		if block is None:
			return None

		return self.create_for_in_block(block)

	def locate_with_indentation(self, text, pos):
		locator = ForInLocator(outer_indentation=self.inner_indentation+self.outer_indentation, inner_indentation=self.inner_indentation)
		return locator.locate(text, pos)

	def locate_all(self, text, start=0, end=-1):
		return locate_all(self, text, start, end)

	def locate_all_with_indentation(self, text, start=0, end=-1):
		locator = ForInLocator(outer_indentation=self.inner_indentation+self.outer_indentation, inner_indentation=self.inner_indentation)
		return locator.locate_all(text, start, end)

	def create_for_in_block(self, block):
		if isinstance(block.element, JoinElement):
			header = block.element[0]
		else:
			header = block.element

		inside_start = block.element.span[1]
		if block.element.content().endswith("{"):
			inside_end = block.end - 2
		else:
			inside_end = block.end - 1

		for_in_blocks = self.locate_all_with_indentation(block.text, inside_start, inside_end)

		return ForInBlock(block.text, block.start, block.end, block.indentation,
			header, inside_start, inside_end, for_in_blocks=for_in_blocks)