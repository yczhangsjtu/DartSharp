import unittest
from eregex.element import BasicElement, WordElement,\
	StringElement, NumberElement, BoolElement, JoinElement,\
	ListElement, TypeNameElement

text = r"""/* hello world
This is a test string.
Below is a C program */

#include <stdio.h>

int main() {
	printf("Hello World");
	printf("Hello 0123 0abc abc0 _1 1_ 1__");
	printf(
	 "Hello World!\"\\"
	);
	printf("\d\d\d", 12, 13, 14)
	return 0;
}
"""

class TestBasicElements(unittest.TestCase):


	def test_basic_element(self):

		pos = text.find("main")
		elem = BasicElement(text, pos, pos + 4)
		self.assertEqual(elem.content(), "main")
		self.assertEqual(elem.textspan(), "main")

		pos = text.find("main")
		elem = BasicElement(text, pos, pos + 4, (pos-1, pos+4))
		self.assertEqual(elem.content(), "main")
		self.assertEqual(elem.textspan(), " main")

		pos = text.find("main")
		elem = BasicElement(text, pos, pos + 4, (pos+1, pos+4))
		self.assertEqual(elem.content(), None)
		self.assertEqual(elem.textspan(), None)

	def test_word_element(self):

		pos = text.find("main")
		elem = WordElement(text, pos, pos + 4)
		self.assertEqual(elem.content(), "main")

if __name__ == '__main__':
	unittest.main()