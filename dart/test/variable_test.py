import unittest
from dart.variable import VariableSimpleDeclareParser
from dart.test.data import code

class TestVariableDeclare(unittest.TestCase):
	"""TestVariableDeclare"""
	def test_variable_declare(self):
		parser = VariableSimpleDeclareParser()

		elem = parser.parse("final bool isBlockElement;", 0)
		self.assertEqual(elem.modifier.content(), "final")
		self.assertEqual(elem.typename.content(), "bool")
		self.assertEqual(elem.name.content(), "isBlockElement")
		self.assertEqual(elem.default_value, None)
		self.assertEqual(elem.content(), "final bool isBlockElement;")

		elem = parser.parse("final bool isBlockElement = false;", 0)
		self.assertEqual(elem.modifier.content(), "final")
		self.assertEqual(elem.typename.content(), "bool")
		self.assertEqual(elem.name.content(), "isBlockElement")
		self.assertEqual(elem.default_value.content(), "false")
		self.assertEqual(elem.content(), "final bool isBlockElement = false;")

		elem = parser.parse("bool isBlockElement;", 0)
		self.assertEqual(elem.modifier, None)
		self.assertEqual(elem.typename.content(), "bool")
		self.assertEqual(elem.name.content(), "isBlockElement")
		self.assertEqual(elem.default_value, None)
		self.assertEqual(elem.content(), "bool isBlockElement;")

		elem = parser.parse("bool isBlockElement = false;", 0)
		self.assertEqual(elem.modifier, None)
		self.assertEqual(elem.typename.content(), "bool")
		self.assertEqual(elem.name.content(), "isBlockElement")
		self.assertEqual(elem.default_value.content(), "false")
		self.assertEqual(elem.content(), "bool isBlockElement = false;")

		elem = parser.parse("final isBlockElement;", 0)
		self.assertEqual(elem, None)

		elem = parser.parse("final isBlockElement = false;", 0)
		self.assertEqual(elem.modifier.content(), "final")
		self.assertEqual(elem.typename, None)
		self.assertEqual(elem.name.content(), "isBlockElement")
		self.assertEqual(elem.default_value.content(), "false")
		self.assertEqual(elem.content(), "final isBlockElement = false;")

if __name__ == '__main__':
	unittest.main()