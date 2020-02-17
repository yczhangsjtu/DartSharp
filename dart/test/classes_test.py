import unittest
from dart.classes import ClassExtensionParser
from dart.test.data import classes

class TestClassHeader(unittest.TestCase):
	"""TestClassHeader"""
	def test_class_extension(self):
		parser = ClassExtensionParser()
		pos = classes.find("MyClass")
		elem = parser.parse(classes, pos+7)
		self.assertEqual(elem.content(), "extends BaseClass")

		pos = classes.find("MySecondClass<T>")
		elem = parser.parse(classes, pos+16)
		self.assertEqual(elem.content(), "extends BaseClass<T>")

		pos = classes.find("MyThirdClass<T,K>")
		elem = parser.parse(classes, pos+17)
		self.assertEqual(elem.content(), "implements MyClass, MySecondClass<T>")

		pos = classes.find("with BaseClass")
		elem = parser.parse(classes, pos-1)
		self.assertEqual(elem.content(), "with BaseClass")

		pos = classes.find("MyFourthClass<T,K>")
		elem = parser.parse(classes, pos+18)
		self.assertEqual(elem.content(), "extends MyThirdClass<T,K>")

		pos = classes.find("extends MyThirdClass<T,K>")
		elem = parser.parse(classes, pos+25)
		self.assertEqual(elem.content(), "implements MyClass, MySecondClass<T>")

		pos = classes.find("implements MyClass, MySecondClass<T>")
		elem = parser.parse(classes, pos+36)
		self.assertEqual(elem.content(), "with BaseClass")


if __name__ == '__main__':
	unittest.main()