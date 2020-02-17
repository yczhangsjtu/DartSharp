import unittest
from eregex.element import BasicElement, WordElement,\
	StringElement, NumberElement, BoolElement, JoinElement,\
	ListElement, TypeNameElement
from eregex.test.data import text

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