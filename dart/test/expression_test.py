import unittest
from dart.expression import SimpleExpressionParser, FunctionInvocationParser
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

	def test_function_invocation(self):
		parser = FunctionInvocationParser()
		pos = code.find("meta._styles.insertAll(0, styles)")
		elem = parser.parse(code, pos)
		self.assertEqual(elem.content(), "meta._styles.insertAll(0, styles)")
		self.assertEqual(elem.name.content(), "meta._styles.insertAll")
		self.assertEqual(elem.arguments.content(), "0, styles")
		self.assertEqual(elem.arguments[0].content(), "0")
		self.assertEqual(elem.arguments[1].content(), "styles")

		pos = code.find("iterator.moveNext()")
		elem = parser.parse(code, pos)
		self.assertEqual(elem.content(), "iterator.moveNext()")
		self.assertEqual(elem.name.content(), "iterator.moveNext")
		self.assertEqual(elem.arguments, None)


if __name__ == '__main__':
	unittest.main()
