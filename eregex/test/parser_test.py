import unittest
from eregex.element import BasicElement, WordElement
from eregex.parser import BasicParser, WordParser,\
	PlainParser, SpacePlainParser, SpaceParser,\
	JoinParser, OrParser, StringParser, NumberParser,\
	BoolParser, ListParser, TypeNameParser, EmptyParser,\
	OptionalParser, WordDotParser, OneOrMoreParser

from eregex.test.data import text

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

	def test_empty_parser(self):

		parser = EmptyParser()
		self.assertEqual(parser.parse(text, 10).start, 10)
		self.assertEqual(parser.parse(text, 15).start, 15)
		self.assertEqual(parser.parse(text, 10000), None)

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

		pos = text.find("abc.def")
		parser = WordParser()
		elem = parser.parse(text, pos - 1)
		self.assertEqual(elem.content(), "abc")

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

		pos = text.find(" .def")
		parser = WordParser()
		elem = parser.parse(text, pos)
		self.assertEqual(elem, None)

	def test_word_dot_parser(self):

		pos = text.find("printf")
		parser = WordDotParser()
		elem = parser.parse(text, pos - 1)
		self.assertEqual(elem.content(), "printf")

		pos = text.find("abc0")
		parser = WordDotParser()
		elem = parser.parse(text, pos)
		self.assertEqual(elem.content(), "abc0")

		pos = text.find("_1")
		parser = WordDotParser()
		elem = parser.parse(text, pos - 1)
		self.assertEqual(elem.content(), "_1")

		pos = text.find("abc.def")
		parser = WordDotParser()
		elem = parser.parse(text, pos - 1)
		self.assertEqual(elem.content(), "abc.def")

	def test_not_word_dot_parser(self):

		pos = text.find("0123")
		parser = WordDotParser()
		elem = parser.parse(text, pos - 1)
		self.assertEqual(elem, None)

		pos = text.find("0abc")
		parser = WordDotParser()
		elem = parser.parse(text, pos)
		self.assertEqual(elem, None)

		pos = text.find("1_")
		parser = WordDotParser()
		elem = parser.parse(text, pos - 1)
		self.assertEqual(elem, None)

		pos = text.find("1__")
		parser = WordDotParser()
		elem = parser.parse(text, pos)
		self.assertEqual(elem, None)

		pos = text.find("abc. ")
		parser = WordDotParser()
		elem = parser.parse(text, pos)
		self.assertEqual(elem.content(), "abc")

		pos = text.find(" .def")
		parser = WordDotParser()
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

	def test_space_plain_parser(self):

		pos = text.find("int main() {")
		parser = SpacePlainParser("int main() {")
		elem = parser.parse(text, pos - 1)
		self.assertEqual(elem.content(), "int main() {")
		self.assertEqual(elem.textspan(), "\nint main() {")

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
			PlainParser("\"Hello 0123 0abc abc0 _1 1_ 1__ abc.def abc. .def\"")
		])
		pos = text.find("printf")
		elem = parser.parse(text, pos + 7)
		self.assertEqual(elem.content(), "\"Hello World\"")

		pos = text.find("printf(\"Hello 0123")
		elem = parser.parse(text, pos + 7)
		self.assertEqual(elem.content(), "\"Hello 0123 0abc abc0 _1 1_ 1__ abc.def abc. .def\"")

		elem = parser.parse(text, pos + 8)
		self.assertEqual(elem, None)

	def test_one_or_more_parser(self):
		parser = OneOrMoreParser([SpacePlainParser("final"), TypeNameParser()])

		elem = parser.parse("final a = 0;", 0)
		self.assertEqual(elem.content(), "final a")

	def test_optional_parser(self):
		parser = OptionalParser(SpacePlainParser("Hello"))

		pos = text.find("printf")

		elem = parser.parse(text, pos + 7)
		self.assertEqual(elem.content(), "")

		elem = parser.parse(text, pos + 8)
		self.assertEqual(elem.content(), "Hello")

		elem = parser.parse(text, pos + 9)
		self.assertEqual(elem.content(), "")


class TestSpecialParser(unittest.TestCase):
	"""TestSpecialParser tests parsers for special structure,
	like String, Number, List, etc."""

	def test_string_parser(self):
		parser = StringParser()

		pos = text.find("printf")
		elem = parser.parse(text, pos + 7)
		self.assertEqual(elem.content(), "\"Hello World\"")

		pos = text.find("printf(\"Hello 0123")
		elem = parser.parse(text, pos + 7)
		self.assertEqual(elem.content(), "\"Hello 0123 0abc abc0 _1 1_ 1__ abc.def abc. .def\"")

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
			SpacePlainParser(","),
			prefix = SpacePlainParser("["),
			postfix = SpacePlainParser("]"),
		)
		elem = parser.parse(lst, pos - 1)
		self.assertEqual(len(elem), 2)
		self.assertEqual(elem.content(), '[\n\t"First item",\n\t"Second item",\n]')
		self.assertEqual(elem[0].content(), '"First item"')
		self.assertEqual(elem[1].content(), '"Second item"')

		parser = ListParser(
			StringParser(),
			SpacePlainParser(","),
			allow_trailing_seperater=False)
		elem = parser.parse(lst, pos + 1)
		self.assertEqual(len(elem), 2)
		self.assertEqual(elem.content(), '"First item",\n\t"Second item"')
		self.assertEqual(elem[0].content(), '"First item"')
		self.assertEqual(elem[1].content(), '"Second item"')

		parser = ListParser(
			StringParser(),
			SpacePlainParser(","),
			allow_trailing_seperater=True)
		elem = parser.parse(lst, pos + 1)
		self.assertEqual(len(elem), 2)
		self.assertEqual(elem.content(), '"First item",\n\t"Second item",')
		self.assertEqual(elem[0].content(), '"First item"')
		self.assertEqual(elem[1].content(), '"Second item"')

		parser = ListParser(WordDotParser(), SpacePlainParser(","))
		elem = parser.parse("Hello", 0)
		self.assertEqual(len(elem), 1)
		self.assertEqual(elem.content(), "Hello")
		self.assertEqual(elem[0].content(), "Hello")


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

	def test_type_name_parser(self):
		typename = r"""
int a = 10;
Double b = 1.0f
Iterable<Widget> iterable = null;
Map<String, List<Widget>> map = null;
"""

		parser = TypeNameParser()
		pos = typename.find("int")
		elem = parser.parse(typename, pos-1)
		self.assertEqual(elem.content(), "int")
		self.assertEqual(elem.textspan(), "\nint")
		self.assertEqual(elem.name.content(), "int")
		self.assertEqual(elem.template_types, None)

		pos = typename.find("Double")
		elem = parser.parse(typename, pos-1)
		self.assertEqual(elem.content(), "Double")
		self.assertEqual(elem.textspan(), "\nDouble")
		self.assertEqual(elem.name.content(), "Double")
		self.assertEqual(elem.template_types, None)

		pos = typename.find("Iterable")
		elem = parser.parse(typename, pos-1)
		self.assertEqual(elem.content(), "Iterable<Widget>")
		self.assertEqual(elem.textspan(), "\nIterable<Widget>")
		self.assertEqual(elem.name.content(), "Iterable")
		self.assertEqual(len(elem.template_types), 1)
		self.assertEqual(elem.template_types[0].content(), "Widget")

		pos = typename.find("Map")
		elem = parser.parse(typename, pos-1)
		self.assertEqual(elem.content(), "Map<String, List<Widget>>")
		self.assertEqual(elem.textspan(), "\nMap<String, List<Widget>>")
		self.assertEqual(elem.name.content(), "Map")
		self.assertEqual(len(elem.template_types), 2)
		self.assertEqual(elem.template_types[0].content(), "String")
		self.assertEqual(elem.template_types[1].content(), "List<Widget>")
		self.assertEqual(elem.template_types[1].name.content(), "List")
		self.assertEqual(elem.template_types[1].template_types.content(), "<Widget>")
		self.assertEqual(elem.template_types[1].template_types.textspan(), "<Widget>")

	def test_number_parser(self):
		text_with_numbers = """
int a = 1;
double b = 1.0;
float c = -10.0;
long d = -1000;
"""
		parser = NumberParser()
		pos = text_with_numbers.find("1")
		elem = parser.parse(text_with_numbers, pos-1)
		self.assertEqual(elem.start, pos)
		self.assertEqual(elem.end, pos+1)
		self.assertEqual(elem.span, (pos-1,pos+1))
		self.assertEqual(elem.content(), "1")
		self.assertEqual(elem.int_part, "1")
		self.assertEqual(elem.frac_part, None)

		pos = text_with_numbers.find("1.0")
		elem = parser.parse(text_with_numbers, pos-1)
		self.assertEqual(elem.content(), "1.0")
		self.assertEqual(elem.int_part, "1")
		self.assertEqual(elem.frac_part, "0")

		pos = text_with_numbers.find("-10.0")
		elem = parser.parse(text_with_numbers, pos-1)
		self.assertEqual(elem.content(), "-10.0")
		self.assertEqual(elem.int_part, "-10")
		self.assertEqual(elem.frac_part, "0")

		pos = text_with_numbers.find("-1000")
		elem = parser.parse(text_with_numbers, pos-1)
		self.assertEqual(elem.content(), "-1000")
		self.assertEqual(elem.int_part, "-1000")
		self.assertEqual(elem.frac_part, None)

	def test_bool_parser(self):
		text_with_bool_values = """
bool a = true;
bool b = false;
"""
		parser = BoolParser()
		pos = text_with_bool_values.find("true")
		elem = parser.parse(text_with_bool_values, pos-1)
		self.assertEqual(elem.content(), "true")
		self.assertTrue(elem.value)

		pos = text_with_bool_values.find("false")
		elem = parser.parse(text_with_bool_values, pos-1)
		self.assertEqual(elem.content(), "false")
		self.assertFalse(elem.value)

if __name__ == '__main__':
	unittest.main()