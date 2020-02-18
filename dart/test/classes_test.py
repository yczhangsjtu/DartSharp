import unittest
from dart.classes import ClassExtensionParser, ClassHeaderParser
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

	def test_class_header(self):

		parser = ClassHeaderParser()

		pos = classes.find("abstract class MyClass")
		elem = parser.parse(classes, pos-1)
		self.assertEqual(elem.content(), "abstract class MyClass extends BaseClass")
		self.assertEqual(elem.textspan(), "\nabstract class MyClass extends BaseClass {")
		self.assertTrue(elem.is_abstract)
		self.assertEqual(elem.name.content(), "MyClass")
		self.assertEqual(elem.extends.content(), "BaseClass")
		self.assertEqual(elem.with_mixes, None)
		self.assertEqual(elem.implements, None)

		pos = classes.find("class MySecondClass<T>")
		elem = parser.parse(classes, pos-1)
		self.assertEqual(elem.content(), "class MySecondClass<T> extends BaseClass<T>")
		self.assertEqual(elem.textspan(), "\nclass MySecondClass<T> extends BaseClass<T> {")
		self.assertFalse(elem.is_abstract)
		self.assertEqual(elem.name.content(), "MySecondClass<T>")
		self.assertEqual(elem.extends.content(), "BaseClass<T>")
		self.assertEqual(elem.with_mixes, None)
		self.assertEqual(elem.implements, None)

		pos = classes.find("class MyThirdClass<T,K>")
		elem = parser.parse(classes, pos-1)
		self.assertEqual(elem.content(), """class MyThirdClass<T,K> implements MyClass, MySecondClass<T>
                        with BaseClass""")
		self.assertEqual(elem.textspan(), """\nclass MyThirdClass<T,K> implements MyClass, MySecondClass<T>
                        with BaseClass {""")
		self.assertFalse(elem.is_abstract)
		self.assertEqual(elem.name.content(), "MyThirdClass<T,K>")
		self.assertEqual(elem.name.name.content(), "MyThirdClass")
		self.assertEqual(elem.with_mixes.content(), "BaseClass")
		self.assertEqual(elem.extends, None)
		self.assertEqual(elem.implements.content(), "MyClass, MySecondClass<T>")

		pos = classes.find("abstract class MyFourthClass<T,K>")
		elem = parser.parse(classes, pos-1)
		self.assertEqual(elem.content(), """abstract class MyFourthClass<T,K>
  extends MyThirdClass<T,K>
  implements MyClass, MySecondClass<T>
  with BaseClass""")
		self.assertEqual(elem.textspan(), """\nabstract class MyFourthClass<T,K>
  extends MyThirdClass<T,K>
  implements MyClass, MySecondClass<T>
  with BaseClass {""")
		self.assertTrue(elem.is_abstract)
		self.assertEqual(elem.name.content(), "MyFourthClass<T,K>")
		self.assertEqual(elem.name.name.content(), "MyFourthClass")
		self.assertEqual(elem.with_mixes.content(), "BaseClass")
		self.assertEqual(elem.extends.content(), "MyThirdClass<T,K>")
		self.assertEqual(elem.implements.content(), "MyClass, MySecondClass<T>")

if __name__ == '__main__':
	unittest.main()