import unittest
from dart.expression import SimpleExpressionParser

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

if __name__ == '__main__':
	unittest.main()
