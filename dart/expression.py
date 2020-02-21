from eregex.element import BasicElement
from eregex.parser import StringParser, BoolParser,\
	NumberParser, OrParser, WordDotParser, JoinParser,\
	TypeNameParser, SpacePlainParser, OptionalParser,\
	ListParser, EmptyParser, WordParser

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

		return FunctionInvocationElement(text, elem.start, elem.end, elem.span, func_name, arguments, modifier)

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

class SimpleExpressionElement(BasicElement):
	"""SimpleExpressionElement"""
	def __init__(self, element):
		super(SimpleExpressionElement, self).__init__(element.text, element.start, element.end, element.span)
		self.expression = element

class SimpleExpressionParser(object):
	"""SimpleExpressionParser recognizes numbers, booleans or strings"""
	def __init__(self):
		super(SimpleExpressionParser, self).__init__()
		self.parser = OrParser([
			FunctionInvocationParser(),
			StringParser(),
			BoolParser(),
			NumberParser(),
			WordDotParser(),
			DartListParser()
		])

	def parse(self, text, pos):
		elem = self.parser.parse(text, pos)
		if elem is None:
			return None

		return SimpleExpressionElement(elem)

