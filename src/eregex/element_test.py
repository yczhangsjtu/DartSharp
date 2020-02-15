import unittest
from element import *

class TestBasicElements(unittest.TestCase):

	def test_simple_element(self):
		text = r"""/* hello world
This is a test string.
Below is a C program */

#include <stdio.h>

int main() {
	printf("Hello World");
	return 0;
}
"""

		pos = text.find("main")
		elem = BasicElement(text, pos, pos + 4)
		self.assertEqual(elem.content(), "main")

if __name__ == '__main__':
	unittest.main()