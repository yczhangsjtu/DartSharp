import unittest
from dart.classes import ClassExtensionParser, ClassHeaderParser,\
	ClassLocator
from dart.test.data import classes, code

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

class TestClassLocator(unittest.TestCase):
	"""TestClassLocator"""
	def test_class_locator(self):
		locator = ClassLocator()
		class_blocks = locator.locate_all(code)
		self.assertEqual(len(class_blocks), 15)

		self.assertEqual(class_blocks[0].name.content(), "BuildOp")
		self.assertFalse(class_blocks[0].is_abstract)
		self.assertEqual(class_blocks[0].content()[-14:], "?? widgets;\n}\n")
		self.assertEqual(class_blocks[0].inside_content()[-12:], "?? widgets;\n")
		function_blocks = class_blocks[0].functions
		self.assertEqual(function_blocks[0].name.content(), "defaultStyles")
		self.assertEqual(function_blocks[0].parameter_list.content(), "NodeMetadata meta, dom.Element e")
		self.assertEqual(function_blocks[0].inside_content(), "\n      _defaultStyles != null ? _defaultStyles(meta, e) : null")
		self.assertEqual(function_blocks[0].content()[-31:], "_defaultStyles(meta, e) : null;")
		self.assertEqual(function_blocks[1].name.content(), "onChild")
		self.assertEqual(function_blocks[1].parameter_list.content(), "NodeMetadata meta, dom.Element e")
		self.assertEqual(function_blocks[1].inside_content(), "\n      _onChild != null ? _onChild(meta, e) : meta")
		self.assertEqual(function_blocks[2].name.content(), "onPieces")
		self.assertEqual(function_blocks[2].parameter_list.content(), "NodeMetadata meta,\n    Iterable<BuiltPiece> pieces,")
		self.assertEqual(function_blocks[2].inside_content(), "\n      _onPieces != null ? _onPieces(meta, pieces) : pieces")
		self.assertEqual(len(function_blocks), 4)

		self.assertEqual(class_blocks[1].name.content(), "BuilderContext")
		self.assertEqual(class_blocks[1].with_mixes, None)
		self.assertFalse(class_blocks[1].is_abstract)
		self.assertEqual(class_blocks[1].content()[-16:], "this.origin);\n}\n")
		self.assertEqual(class_blocks[1].inside_content()[-14:], "this.origin);\n")
		self.assertEqual(class_blocks[1].functions, None)

		self.assertEqual(class_blocks[2].name.content(), "BuiltPiece")
		self.assertEqual(class_blocks[2].extends, None)
		self.assertTrue(class_blocks[2].is_abstract)
		self.assertEqual(class_blocks[2].content()[-15:], "get widgets;\n}\n")

		self.assertEqual(class_blocks[3].name.content(), "BuiltPieceSimple")
		self.assertEqual(class_blocks[3].extends.content(), "BuiltPiece")
		self.assertFalse(class_blocks[3].is_abstract)
		self.assertEqual(class_blocks[3].content()[-19:], "widgets != null;\n}\n")

		self.assertEqual(class_blocks[6].name.content(), "CssMargin")
		self.assertFalse(class_blocks[6].is_abstract)
		self.assertEqual(class_blocks[6].content()[-27:], "..top = top ?? this.top;\n}\n")
		function_blocks = class_blocks[6].functions
		self.assertEqual(function_blocks[0].name.content(), "copyWith")
		self.assertEqual(function_blocks[0].parameter_list.content(), "{\n    CssLength bottom,\n    CssLength left,\n    CssLength right,\n    CssLength top,\n  }")
		self.assertEqual(function_blocks[0].inside_content(), "\n      CssMargin()\n        ..bottom = bottom ?? this.bottom\n        ..left = left ?? this.left\n        ..right = right ?? this.right\n        ..top = top ?? this.top")
		self.assertEqual(len(function_blocks), 1)

		self.assertEqual(class_blocks[7].name.content(), "CssLength")
		self.assertFalse(class_blocks[7].is_abstract)
		self.assertEqual(class_blocks[7].content()[-20:], "return value;\n  }\n}\n")
		function_blocks = class_blocks[7].functions
		self.assertEqual(function_blocks[0].name.content(), "getValue")
		self.assertEqual(function_blocks[0].parameter_list.content(), "BuilderContext bc, TextStyleBuilders tsb")
		self.assertEqual(function_blocks[0].inside_content()[-16:], "return value;\n  ")
		self.assertEqual(len(function_blocks), 1)

		self.assertEqual(class_blocks[11].name.content(), "SpaceBit")
		self.assertFalse(class_blocks[11].is_abstract)
		self.assertEqual(class_blocks[11].extends.content(), "TextBit")
		self.assertEqual(class_blocks[11].content()[-28:], "String get data => _data;\n}\n")

		self.assertEqual(class_blocks[14].name.content(), "TextStyleBuilders")
		self.assertFalse(class_blocks[14].is_abstract)
		self.assertEqual(class_blocks[14].content()[-25:], "_textAlign = null;\n  }\n}\n")


if __name__ == '__main__':
	unittest.main()