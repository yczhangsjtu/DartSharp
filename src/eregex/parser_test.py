import unittest
from parser import *
from element_test import text

class TestBasicParser(unittest.TestCase):

	def test_simple_parser_found(self):

		pos = text.find("printf")
		parser = BasicParser(r"\s*(\w+)")
		elem = parser.parse(text, pos - 2)
		self.assertEqual(elem.content(), "printf")
		self.assertEqual(elem.textspan(), "\n\tprintf")

		parser = BasicParser(r"\s*\w+")
		elem = parser.parse(text, pos - 2)
		self.assertEqual(elem.content(), "\n\tprintf")
		self.assertEqual(elem.textspan(), "\n\tprintf")

	def test_simple_parser_not_found(self):

		pos = text.find("return")
		parser = BasicParser(r"\s*\b(\w+)\b")
		elem = parser.parse(text, pos + 8)
		self.assertEqual(elem, None)

	def test_word_parser(self):

		pos = text.find("printf")
		parser = WordParser()
		elem = parser.parse(text, pos - 1)
		self.assertEqual(elem.content(), "printf")

		pos = text.find("abc0")
		parser = WordParser()
		elem = parser.parse(text, pos)
		self.assertEqual(elem.content(), "abc0")

		pos = text.find("_1")
		parser = WordParser()
		elem = parser.parse(text, pos - 1)
		self.assertEqual(elem.content(), "_1")

	def test_not_word_parser(self):

		pos = text.find("0123")
		parser = WordParser()
		elem = parser.parse(text, pos - 1)
		self.assertEqual(elem, None)

		pos = text.find("0abc")
		parser = WordParser()
		elem = parser.parse(text, pos)
		self.assertEqual(elem, None)

		pos = text.find("1_")
		parser = WordParser()
		elem = parser.parse(text, pos - 1)
		self.assertEqual(elem, None)

		pos = text.find("1__")
		parser = WordParser()
		elem = parser.parse(text, pos)
		self.assertEqual(elem, None)

	def test_plain_parser(self):

		pos = text.find("int main() {")
		parser = PlainParser("\nint main() {")
		elem = parser.parse(text, pos - 1)
		self.assertEqual(elem.content(), "\nint main() {")

		parser = PlainParser("")
		elem = parser.parse(text, pos)
		self.assertEqual(elem.content(), "")
		self.assertEqual(elem.textspan(), "")
		elem = parser.parse(text, pos + 1)
		self.assertEqual(elem.content(), "")
		self.assertEqual(elem.textspan(), "")

	def test_not_plain_parser(self):

		pos = text.find("int main() {")
		parser = PlainParser("\nint main() { ")
		elem = parser.parse(text, pos - 1)
		self.assertEqual(elem, None)

class TestCompositeParser(unittest.TestCase):
	"""TestCompositeParser tests composite parsers,
	like JoinParser, OrParser, etc."""

	def test_join_parser(self):

		parser = JoinParser([
			BasicParser(r"printf\s*\(\s*\""),
			WordParser(),
			BasicParser(r"\s+"),
			WordParser(),
			BasicParser(r"\"\s*\)\s*;")
		])

		pos = text.find("printf")
		elem = parser.parse(text, pos)
		self.assertEqual(len(elem), 5)
		self.assertTrue(type(elem[0]) is BasicElement)
		self.assertEqual(elem[0].content(), "printf(\"")
		self.assertTrue(type(elem[1]) is WordElement)
		self.assertEqual(elem[1].content(), "Hello")
		self.assertTrue(type(elem[2]) is BasicElement)
		self.assertEqual(elem[2].content(), " ")
		self.assertTrue(type(elem[3]) is WordElement)
		self.assertEqual(elem[3].content(), "World")
		self.assertTrue(type(elem[4]) is BasicElement)
		self.assertEqual(elem[4].content(), "\");")

		pos = text.find("printf(\"Hello 0123")
		elem = parser.parse(text, pos)
		self.assertEqual(elem, None)

	def test_or_parser(self):
		parser = OrParser([
			PlainParser("\"Hello World\""),
			PlainParser("\"Hello 0123 0abc abc0 _1 1_ 1__\"")
		])
		pos = text.find("printf")
		elem = parser.parse(text, pos + 7)
		self.assertEqual(elem.content(), "\"Hello World\"")

		pos = text.find("printf(\"Hello 0123")
		elem = parser.parse(text, pos + 7)
		self.assertEqual(elem.content(), "\"Hello 0123 0abc abc0 _1 1_ 1__\"")

		elem = parser.parse(text, pos + 8)
		self.assertEqual(elem, None)

	def test_string_parser(self):
		parser = StringParser()

		pos = text.find("printf")
		elem = parser.parse(text, pos + 7)
		self.assertEqual(elem.content(), "\"Hello World\"")

		pos = text.find("printf(\"Hello 0123")
		elem = parser.parse(text, pos + 7)
		self.assertEqual(elem.content(), "\"Hello 0123 0abc abc0 _1 1_ 1__\"")

		pos = text.find("printf(\n")
		elem = parser.parse(text, pos + 7)
		self.assertEqual(elem.content(), '"Hello World!\\"\\\\"')
		self.assertEqual(elem.textspan(), '\n\t "Hello World!\\"\\\\"')

	def test_list_parser(self):
		lst = r"""
var list = [
	"First item",
	"Second item",
]
"""
		parser = ListParser(BasicParser(r"\s*(\d+)"), BasicParser(r"\s*,"))

		pos = text.find("printf(\"\\d")
		elem = parser.parse(text, pos + 17)
		self.assertEqual(len(elem), 3)
		self.assertEqual(elem.content(), "12, 13, 14")
		self.assertEqual(elem[0].content(), "12")
		self.assertEqual(elem[1].content(), "13")
		self.assertEqual(elem[2].content(), "14")

		pos = lst.find("[")
		parser = ListParser(
			StringParser(),
			BasicParser(r"\s*,"),
			prefix = BasicParser(r"\s*\["),
			postfix = BasicParser(r"\s*\]"),
		)
		elem = parser.parse(lst, pos - 1)
		self.assertEqual(len(elem), 2)
		self.assertEqual(elem.content(), '"First item",\n\t"Second item"')
		self.assertEqual(elem[0].content(), '"First item"')
		self.assertEqual(elem[1].content(), '"Second item"')


	def test_nested_list(self):
		nested_list = r"""
var list = [
	"First item",
	"Second item",
	[
		"First nested item",
		"second nested item"
	]
]
"""

		parser = ListParser(
			OrParser([
				ListParser(
					StringParser(),
					BasicParser(r"\s*,"),
					prefix = BasicParser(r"\s*\["),
					postfix = BasicParser(r"\s*\]")
				),
				StringParser()
			]),
			BasicParser(r"\s*,")
		)
		pos = nested_list.find("[")

		elem = parser.parse(nested_list, pos + 1)

		self.assertEqual(len(elem), 3)
		self.assertEqual(elem[0].content(), '"First item"')
		self.assertEqual(elem[1].content(), '"Second item"')
		self.assertEqual(len(elem[2]), 2)
		self.assertEqual(elem[2][0].content(), '"First nested item"')
		self.assertEqual(elem[2][1].content(), '"second nested item"')


if __name__ == '__main__':
	unittest.main()