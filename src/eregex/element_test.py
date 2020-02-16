import unittest
from element import *
from parser import *

text = r"""/* hello world
This is a test string.
Below is a C program */

#include <stdio.h>

int main() {
	printf("Hello World");
	printf("Hello 0123 0abc abc0 _1 1_ 1__");
	return 0;
}
"""

class TestBasicElements(unittest.TestCase):


	def test_simple_element(self):

		pos = text.find("main")
		elem = BasicElement(text, pos, pos + 4)
		self.assertEqual(elem.content(), "main")

	def test_word_element(self):

		pos = text.find("main")
		elem = WordElement(text, pos, pos + 4)
		self.assertEqual(elem.content(), "main")

class TestBasicParser(unittest.TestCase):

	def test_simple_parser_found(self):

		pos = text.find("printf")
		parser = BasicParser(r"\s*(\w+)")
		elem = parser.parse(text, pos - 2)
		self.assertEqual(elem.content(), "printf")

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


if __name__ == '__main__':
	unittest.main()