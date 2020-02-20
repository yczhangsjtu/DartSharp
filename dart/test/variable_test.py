import unittest
from dart.variable import VariableSimpleDeclareParser, VariableDeclareLocator
from dart.test.data import code
from dart.classes import ClassLocator

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

		elem = parser.parse("final meta = collectMetadata(domNode);", 0)
		self.assertEqual(elem.modifier.content(), "final")
		self.assertEqual(elem.typename, None)
		self.assertEqual(elem.name.content(), "meta")
		self.assertEqual(elem.default_value.content(), "collectMetadata(domNode)")
		self.assertEqual(elem.content(), "final meta = collectMetadata(domNode);")

	def test_variable_locator(self):
		locator = ClassLocator()
		class_blocks = locator.locate_all(code)
		self.assertEqual(len(class_blocks), 15)

		locator = VariableDeclareLocator(indentation="  ")
		variable_declares = locator.locate_all(code, class_blocks[0].inside_start, class_blocks[0].inside_end)
		self.assertEqual(len(variable_declares), 6)
		self.assertEqual(variable_declares[0].modifier.content(), "final")
		self.assertEqual(variable_declares[0].typename.content(), "bool")
		self.assertEqual(variable_declares[0].name.content(), "isBlockElement")
		self.assertEqual(variable_declares[2].modifier.content(), "final")
		self.assertEqual(variable_declares[2].typename.content(), "BuildOpDefaultStyles")
		self.assertEqual(variable_declares[2].name.content(), "_defaultStyles")

		variable_declares = locator.locate_all(code, class_blocks[3].inside_start, class_blocks[3].inside_end)
		self.assertEqual(len(variable_declares), 2)
		self.assertEqual(variable_declares[0].modifier.content(), "final")
		self.assertEqual(variable_declares[0].typename.content(), "TextBlock")
		self.assertEqual(variable_declares[0].name.content(), "block")
		self.assertEqual(variable_declares[1].modifier.content(), "final")
		self.assertEqual(variable_declares[1].typename.content(), "Iterable<Widget>")
		self.assertEqual(variable_declares[1].name.content(), "widgets")

if __name__ == '__main__':
	unittest.main()