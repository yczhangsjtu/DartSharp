import unittest
from dart.expression import SimpleExpressionParser, FunctionInvocationParser,\
	DartListParser, TypeNameParser, SpacePlainParser, OptionalParser, ListParser,\
	JoinParser, ForInHeaderParser, ForInLocator
from eregex.test.data import code

class TestSimpleExpression(unittest.TestCase):
	"""TestSimpleExpression"""
	def test_simple_expression(self):
		text_with_expression = """
int a = 1.0;
bool b = true;
String c = "Hello World";
int d = a;
"""
		parser = SimpleExpressionParser()

		pos = text_with_expression.find("1.0")
		elem = parser.parse(text_with_expression, pos-1)
		self.assertEqual(elem.content(), "1.0")

		pos = text_with_expression.find("true")
		elem = parser.parse(text_with_expression, pos-1)
		self.assertEqual(elem.content(), "true")

		pos = text_with_expression.find("Hello World")
		elem = parser.parse(text_with_expression, pos-1)
		self.assertEqual(elem.content(), '"Hello World"')

		pos = text_with_expression.find("int d")
		elem = parser.parse(text_with_expression, pos+7)
		self.assertEqual(elem.content(), "a")

		elem = parser.parse("collectMetadata(domNode)", 0)
		self.assertEqual(elem.content(), "collectMetadata(domNode)")
		self.assertEqual(elem.expression.name.content(), "collectMetadata")
		self.assertEqual(elem.expression.arguments.content(), "domNode")
		self.assertEqual(elem.expression.arguments[0].content(), "domNode")

	def test_function_invocation(self):
		parser = FunctionInvocationParser()
		pos = code.find("meta._styles.insertAll(0, styles)")
		elem = parser.parse(code, pos)
		self.assertEqual(elem.content(), "meta._styles.insertAll(0, styles)")
		self.assertEqual(elem.name.content(), "meta._styles.insertAll")
		self.assertEqual(elem.arguments.content(), "0, styles")
		self.assertEqual(elem.arguments[0].content(), "0")
		self.assertEqual(elem.arguments[1].content(), "styles")

		elem = parser.parse("collectMetadata(domNode)", 0)
		self.assertEqual(elem.content(), "collectMetadata(domNode)")
		self.assertEqual(elem.name.content(), "collectMetadata")
		self.assertEqual(elem.arguments.content(), "domNode")
		self.assertEqual(elem.arguments[0].content(), "domNode")

		pos = code.find("iterator.moveNext()")
		elem = parser.parse(code, pos)
		self.assertEqual(elem.content(), "iterator.moveNext()")
		self.assertEqual(elem.name.content(), "iterator.moveNext")
		self.assertEqual(elem.arguments, None)

	def test_dart_list(self):
		parser = DartListParser()

		elem = parser.parse("  []", 0)
		self.assertEqual(elem.content(), "[]")
		self.assertEqual(elem.elements, None)
		self.assertEqual(elem.typename, None)

		elem = parser.parse(" <Widget> []", 0)
		self.assertEqual(elem.content(), "<Widget> []")
		self.assertEqual(elem.elements, None)
		self.assertEqual(elem.typename.content(), "Widget")

		elem = parser.parse("  [1.0, abc, \"Hello\"]", 0)
		self.assertEqual(elem.content(), "[1.0, abc, \"Hello\"]")
		self.assertEqual(elem.elements.content(), "1.0, abc, \"Hello\"")
		self.assertEqual(elem.typename, None)

		elem = parser.parse(" <Widget> [1.0, abc, \"Hello\"]", 0)
		self.assertEqual(elem.content(), "<Widget> [1.0, abc, \"Hello\"]")
		self.assertEqual(elem.elements.content(), "1.0, abc, \"Hello\"")
		self.assertEqual(elem.typename.content(), "Widget")

	def test_for_in_header(self):
		parser = ForInHeaderParser()

		elem = parser.parse("for (var i in list)", 0)
		self.assertEqual(elem.content(), "for (var i in list)")
		self.assertEqual(elem.typename.content(), "var")
		self.assertEqual(elem.variable.content(), "i")
		self.assertEqual(elem.collection.content(), "list")

	def test_for_in_block(self):
		locator = ForInLocator(outer_indentation="    ")

		blocks = locator.locate_all(code)
		self.assertEqual(len(blocks), 2)
		self.assertEqual(blocks[0].header.content(), "for (final child in _children)")
		self.assertEqual(blocks[1].header.content(), "for (final child in _children)")




if __name__ == '__main__':
	unittest.main()
