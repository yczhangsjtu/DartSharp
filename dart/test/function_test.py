import unittest
from dart.function import NormalParameterItemElement,\
  NormalParameterItemParser, ThisParameterItemElement,\
  ThisParameterItemParser, ParameterItemParser,\
  SingleParameterListParser, ParameterListParser,\
  ConstructorParameterItemParser, ConstructorSingleParameterListParser,\
  ConstructorParameterListParser, FunctionalParameterItemElement,\
  ParameterItemElement, ConstructorHeaderElement, ConstructorHeaderParser,\
  FunctionHeaderParser, FunctionLocator, FunctionModifierParser
from dart.classes import ClassLocator
from data import lazy_set_func, build_op_class, node_meta_data_class, code

class TestParameterElements(unittest.TestCase):
  """TestParameterElements"""
  def test_normal_parameter_item(self):
    parser = NormalParameterItemParser()

    pos = lazy_set_func.find("TextDecorationStyle decorationStyle")
    elem = parser.parse(lazy_set_func, pos-2)
    self.assertEqual(elem.content(), "TextDecorationStyle decorationStyle")
    self.assertEqual(elem.textspan(), "  TextDecorationStyle decorationStyle")
    self.assertEqual(elem.typename.content(), "TextDecorationStyle")
    self.assertEqual(elem.name.content(), "decorationStyle")
    self.assertEqual(elem.default_value, None)

    pos = lazy_set_func.find("String fontFamily")
    elem = parser.parse(lazy_set_func, pos-2)
    self.assertEqual(elem.content(), "String fontFamily = null")
    self.assertEqual(elem.textspan(), "  String fontFamily = null")
    self.assertEqual(elem.typename.content(), "String")
    self.assertEqual(elem.name.content(), "fontFamily")
    self.assertEqual(elem.default_value.content(), "null")

    pos = lazy_set_func.find("bool fontStyleItalic")
    elem = parser.parse(lazy_set_func, pos-2)
    self.assertEqual(elem.content(), "bool fontStyleItalic = false")
    self.assertEqual(elem.textspan(), "  bool fontStyleItalic = false")
    self.assertEqual(elem.typename.content(), "bool")
    self.assertEqual(elem.name.content(), "fontStyleItalic")
    self.assertEqual(elem.default_value.content(), "false")

    pos = lazy_set_func.find("double size")
    elem = parser.parse(lazy_set_func, pos-2)
    self.assertEqual(elem.content(), "double size = 1.0")
    self.assertEqual(elem.textspan(), "  double size = 1.0")
    self.assertEqual(elem.typename.content(), "double")
    self.assertEqual(elem.name.content(), "size")
    self.assertEqual(elem.default_value.content(), "1.0")

    pos = lazy_set_func.find("Iterable<String> stylesPrepend")
    elem = parser.parse(lazy_set_func, pos-2)
    self.assertEqual(elem.content(), "Iterable<String> stylesPrepend = null")
    self.assertEqual(elem.textspan(), "  Iterable<String> stylesPrepend = null")
    self.assertEqual(elem.typename.content(), "Iterable<String>")
    self.assertEqual(elem.name.content(), "stylesPrepend")
    self.assertEqual(elem.default_value.content(), "null")

  def test_this_parameter_item(self):
    parser = ThisParameterItemParser()

    pos = build_op_class.find("this.width")
    elem = parser.parse(build_op_class, pos-2)
    self.assertEqual(elem.content(), "this.width")
    self.assertEqual(elem.textspan(), "  this.width")
    self.assertEqual(elem.name.content(), "width")
    self.assertEqual(elem.default_value, None)

    pos = build_op_class.find("this.size = 1.0")
    elem = parser.parse(build_op_class, pos-2)
    self.assertEqual(elem.content(), "this.size = 1.0")
    self.assertEqual(elem.textspan(), "  this.size = 1.0")
    self.assertEqual(elem.name.content(), "size")
    self.assertEqual(elem.default_value.content(), "1.0")

    pos = build_op_class.find("this.offset = -5.0")
    elem = parser.parse(build_op_class, pos-2)
    self.assertEqual(elem.content(), "this.offset = -5.0")
    self.assertEqual(elem.textspan(), "  this.offset = -5.0")
    self.assertEqual(elem.name.content(), "offset")
    self.assertEqual(elem.default_value.content(), "-5.0")

    pos = build_op_class.find('this.name = "FirstOp"')
    elem = parser.parse(build_op_class, pos-2)
    self.assertEqual(elem.content(), 'this.name = "FirstOp"')
    self.assertEqual(elem.textspan(), '  this.name = "FirstOp"')
    self.assertEqual(elem.name.content(), "name")
    self.assertEqual(elem.default_value.content(), '"FirstOp"')

    pos = build_op_class.find("this.priority = 10")
    elem = parser.parse(build_op_class, pos-2)
    self.assertEqual(elem.content(), "this.priority = 10")
    self.assertEqual(elem.textspan(), "  this.priority = 10")
    self.assertEqual(elem.name.content(), "priority")
    self.assertEqual(elem.default_value.content(), "10")

  def test_parameter_item(self):
    parser = ParameterItemParser()

    pos = lazy_set_func.find("double size")
    elem = parser.parse(lazy_set_func, pos-2)
    self.assertEqual(elem.content(), "double size = 1.0")
    self.assertEqual(elem.textspan(), "  double size = 1.0")
    self.assertEqual(elem.typename.content(), "double")
    self.assertEqual(elem.name.content(), "size")
    self.assertEqual(elem.default_value.content(), "1.0")

    pos = lazy_set_func.find("Iterable<String> stylesPrepend")
    elem = parser.parse(lazy_set_func, pos-2)
    self.assertEqual(elem.content(), "Iterable<String> stylesPrepend = null")
    self.assertEqual(elem.textspan(), "  Iterable<String> stylesPrepend = null")
    self.assertEqual(elem.typename.content(), "Iterable<String>")
    self.assertEqual(elem.name.content(), "stylesPrepend")
    self.assertEqual(elem.default_value.content(), "null")

    parser = ConstructorParameterItemParser()

    pos = build_op_class.find('this.name = "FirstOp"')
    elem = parser.parse(build_op_class, pos-2)
    self.assertEqual(elem.content(), 'this.name = "FirstOp"')
    self.assertEqual(elem.textspan(), '  this.name = "FirstOp"')
    self.assertEqual(elem.name.content(), "name")
    self.assertEqual(elem.default_value.content(), '"FirstOp"')

    pos = build_op_class.find("this.priority = 10")
    elem = parser.parse(build_op_class, pos-2)
    self.assertEqual(elem.content(), "this.priority = 10")
    self.assertEqual(elem.textspan(), "  this.priority = 10")
    self.assertEqual(elem.name.content(), "priority")
    self.assertEqual(elem.default_value.content(), "10")

  def test_single_parameter_list(self):
    parser = SingleParameterListParser(allow_trailing_comma=True, curly_brace=True)
    pos = lazy_set_func.find("{")
    elem = parser.parse(lazy_set_func, pos-1)
    self.assertEqual(elem[0].content(), "BuildOp buildOp")
    self.assertEqual(elem[-1].content(), "Iterable<String> stylesPrepend = null")
    self.assertTrue(elem.has_trailing_comma)
    self.assertEqual(elem.content(), lazy_set_func[pos:lazy_set_func.find("}")+1])
    self.assertEqual(elem.textspan(), lazy_set_func[pos-1:lazy_set_func.find("}")+1])

    parser = SingleParameterListParser(allow_trailing_comma=True, curly_brace=False)
    pos = lazy_set_func.find("{")
    elem = parser.parse(lazy_set_func, pos+1)
    self.assertEqual(elem[0].content(), "BuildOp buildOp")
    self.assertEqual(elem[-1].content(), "Iterable<String> stylesPrepend = null")
    self.assertTrue(elem.has_trailing_comma)
    self.assertEqual(elem.content(), lazy_set_func[pos+4:lazy_set_func.find("}")-1])
    self.assertEqual(elem.textspan(), lazy_set_func[pos+1:lazy_set_func.find("}")-1])

  def test_constructor_single_parameter_list(self):
    parser = ConstructorSingleParameterListParser(allow_trailing_comma=True, curly_brace=True)
    pos = build_op_class.find("({")
    elem = parser.parse(build_op_class, pos+1)
    self.assertEqual(elem[0].content(), "BuildOpDefaultStyles defaultStyles")
    self.assertEqual(elem[-1].content(), "this.priority = 10")
    self.assertTrue(elem.has_trailing_comma)
    self.assertEqual(elem.content(), build_op_class[pos+1:build_op_class.find("}")+1])
    self.assertEqual(elem.textspan(), build_op_class[pos+1:build_op_class.find("}")+1])

    parser = ConstructorSingleParameterListParser(allow_trailing_comma=True, curly_brace=False)
    pos = build_op_class.find("({")
    elem = parser.parse(build_op_class, pos+2)
    self.assertEqual(elem[0].content(), "BuildOpDefaultStyles defaultStyles")
    self.assertEqual(elem[-1].content(), "this.priority = 10")
    self.assertTrue(elem.has_trailing_comma)
    self.assertEqual(elem.content(), build_op_class[pos+7:build_op_class.find("}")-3])
    self.assertEqual(elem.textspan(), build_op_class[pos+2:build_op_class.find("}")-3])

  def test_parameter_list(self):
    parser = ParameterListParser()

    pos = lazy_set_func.find("(")
    elem = parser.parse(lazy_set_func, pos+1)
    self.assertEqual(len(elem.positioned), 1)
    self.assertFalse(elem.positioned.has_trailing_comma)
    self.assertEqual(elem.positioned.content(), "NodeMetadata meta")
    self.assertEqual(elem.positioned.textspan(), "\n  NodeMetadata meta")
    self.assertEqual(elem.named[0].content(), "BuildOp buildOp")
    self.assertEqual(elem.named[-1].content(), "Iterable<String> stylesPrepend = null")
    self.assertTrue(elem.named.has_trailing_comma)
    self.assertEqual(elem.named.content(), lazy_set_func[lazy_set_func.find("{"):lazy_set_func.find("}")+1])
    self.assertEqual(elem.named.textspan(), lazy_set_func[lazy_set_func.find("{")-1:lazy_set_func.find("}")+1])

  def test_constructor_parameter_list(self):
    parser = ConstructorParameterListParser()

    pos = build_op_class.find("({")
    elem = parser.parse(build_op_class, pos+1)
    self.assertEqual(elem.positioned, None)
    self.assertEqual(elem.named[0].content(), "BuildOpDefaultStyles defaultStyles")
    self.assertEqual(elem.named[-1].content(), "this.priority = 10")
    self.assertTrue(elem.named.has_trailing_comma)
    self.assertEqual(elem.named.content(), build_op_class[pos+1:build_op_class.find("}")+1])
    self.assertEqual(elem.named.textspan(), build_op_class[pos+1:build_op_class.find("}")+1])

    parser = ParameterListParser()
    elem = parser.parse(build_op_class, pos+1)
    self.assertEqual(elem.content(), "")

  def test_parameter_list_with_function_header(self):
  	parser = ParameterListParser()

  	pos = node_meta_data_class.find("void styles(void f(String key, String value))")
  	elem = parser.parse(node_meta_data_class, pos + 12)
  	self.assertEqual(len(elem.positioned), 1)
  	self.assertEqual(elem.named, None)
  	self.assertEqual(elem.content(), "void f(String key, String value)")
  	self.assertEqual(elem.positioned[0].content(), "void f(String key, String value)")

  	pos = node_meta_data_class.find("void f({void g(int a) = null, int b})")
  	elem = parser.parse(node_meta_data_class, pos + 7)
  	self.assertEqual(len(elem.named), 2)
  	self.assertEqual(elem.positioned, None)
  	self.assertEqual(elem.content(), "{void g(int a) = null, int b}")
  	self.assertEqual(type(elem.named[0]), ParameterItemElement)
  	self.assertEqual(elem.named[0].content(), "void g(int a) = null")
  	self.assertEqual(elem.named[0].name.content(), "g")
  	self.assertEqual(elem.named[0].typename.content(), "void")
  	self.assertEqual(elem.named[0].default_value.content(), "null")
  	self.assertEqual(elem.named[1].name.content(), "b")
  	self.assertEqual(elem.named[1].typename.content(), "int")
  	self.assertEqual(elem.named[1].default_value, None)

  	pos = node_meta_data_class.find("void h(int o(), {void g(int a) = null, int b})")
  	elem = parser.parse(node_meta_data_class, pos + 7)
  	self.assertEqual(len(elem.named), 2)
  	self.assertEqual(len(elem.positioned), 1)
  	self.assertEqual(elem.content(), "int o(), {void g(int a) = null, int b}")
  	self.assertEqual(elem.positioned[0].content(), "int o()")
  	self.assertEqual(elem.positioned[0].name.content(), "o")
  	self.assertEqual(elem.positioned[0].typename.content(), "int")
  	self.assertEqual(elem.positioned[0].default_value, None)
  	self.assertEqual(type(elem.named[0]), ParameterItemElement)
  	self.assertEqual(elem.named[0].content(), "void g(int a) = null")
  	self.assertEqual(elem.named[0].name.content(), "g")
  	self.assertEqual(elem.named[0].typename.content(), "void")
  	self.assertEqual(elem.named[0].default_value.content(), "null")
  	self.assertEqual(elem.named[1].name.content(), "b")
  	self.assertEqual(elem.named[1].typename.content(), "int")
  	self.assertEqual(elem.named[1].default_value, None)

class TestFunctionHeader(unittest.TestCase):
	"""TestFunctionHeader"""
	def test_function_header(self):
		parser = FunctionHeaderParser()

		elem = parser.parse(lazy_set_func, 0)
		self.assertEqual(elem.typename.content(), "NodeMetadata")
		self.assertEqual(elem.name.content(), "lazySet")
		self.assertEqual(len(elem.parameter_list.positioned), 1)
		self.assertFalse(elem.parameter_list.positioned.has_trailing_comma)
		self.assertEqual(elem.parameter_list.positioned.content(), "NodeMetadata meta")
		self.assertEqual(elem.parameter_list.positioned.textspan(), "\n  NodeMetadata meta")
		self.assertEqual(elem.parameter_list.named[0].content(), "BuildOp buildOp")
		self.assertEqual(elem.parameter_list.named[-1].content(), "Iterable<String> stylesPrepend = null")
		self.assertTrue(elem.parameter_list.named.has_trailing_comma)
		self.assertEqual(elem.parameter_list.named.content(), lazy_set_func[lazy_set_func.find("{"):lazy_set_func.find("}")+1])
		self.assertEqual(elem.parameter_list.named.textspan(), lazy_set_func[lazy_set_func.find("{")-1:lazy_set_func.find("}")+1])

	def test_function_header_with_functional_parameters(self):
		parser = FunctionHeaderParser()

		pos = node_meta_data_class.find("void styles(void f(String key, String value))")
		elem = parser.parse(node_meta_data_class, pos)
		self.assertEqual(elem.name.content(), "styles")
		self.assertEqual(elem.typename.content(), "void")
		self.assertEqual(len(elem.parameter_list.positioned), 1)
		self.assertEqual(elem.parameter_list.named, None)
		self.assertEqual(elem.parameter_list.content(), "void f(String key, String value)")
		self.assertEqual(elem.parameter_list.positioned[0].content(), "void f(String key, String value)")

		pos = node_meta_data_class.find("void f({void g(int a) = null, int b})")
		elem = parser.parse(node_meta_data_class, pos)
		self.assertEqual(elem.name.content(), "f")
		self.assertEqual(elem.typename.content(), "void")
		self.assertEqual(len(elem.parameter_list.named), 2)
		self.assertEqual(elem.parameter_list.positioned, None)
		self.assertEqual(elem.parameter_list.content(), "{void g(int a) = null, int b}")
		self.assertEqual(type(elem.parameter_list.named[0]), ParameterItemElement)
		self.assertEqual(elem.parameter_list.named[0].content(), "void g(int a) = null")
		self.assertEqual(elem.parameter_list.named[0].name.content(), "g")
		self.assertEqual(elem.parameter_list.named[0].typename.content(), "void")
		self.assertEqual(elem.parameter_list.named[0].default_value.content(), "null")
		self.assertEqual(elem.parameter_list.named[1].name.content(), "b")
		self.assertEqual(elem.parameter_list.named[1].typename.content(), "int")
		self.assertEqual(elem.parameter_list.named[1].default_value, None)

		pos = node_meta_data_class.find("void h(int o(), {void g(int a) = null, int b})")
		elem = parser.parse(node_meta_data_class, pos)
		self.assertEqual(elem.name.content(), "h")
		self.assertEqual(elem.typename.content(), "void")
		self.assertEqual(len(elem.parameter_list.named), 2)
		self.assertEqual(len(elem.parameter_list.positioned), 1)
		self.assertEqual(elem.parameter_list.content(), "int o(), {void g(int a) = null, int b}")
		self.assertEqual(elem.parameter_list.positioned[0].content(), "int o()")
		self.assertEqual(elem.parameter_list.positioned[0].name.content(), "o")
		self.assertEqual(elem.parameter_list.positioned[0].typename.content(), "int")
		self.assertEqual(elem.parameter_list.positioned[0].default_value, None)
		self.assertEqual(type(elem.parameter_list.named[0]), ParameterItemElement)
		self.assertEqual(elem.parameter_list.named[0].content(), "void g(int a) = null")
		self.assertEqual(elem.parameter_list.named[0].name.content(), "g")
		self.assertEqual(elem.parameter_list.named[0].typename.content(), "void")
		self.assertEqual(elem.parameter_list.named[0].default_value.content(), "null")
		self.assertEqual(elem.parameter_list.named[1].name.content(), "b")
		self.assertEqual(elem.parameter_list.named[1].typename.content(), "int")
		self.assertEqual(elem.parameter_list.named[1].default_value, None)

	def test_constructor_header(self):
		parser = ConstructorHeaderParser("BuildOp")
		pos = build_op_class.find("BuildOp({")
		elem = parser.parse(build_op_class, pos)
		self.assertEqual(elem.name.content(), "BuildOp")
		self.assertEqual(elem.parameter_list.positioned, None)
		self.assertEqual(elem.parameter_list.named[0].content(), "BuildOpDefaultStyles defaultStyles")
		self.assertEqual(elem.parameter_list.named[-1].content(), "this.priority = 10")
		self.assertEqual(elem.content()[-4:], "  })")

class TestFunctionLocator(unittest.TestCase):
	"""docstring for TestFunctionLocator"""
	def test_function_modifier(self):
		text="""
@override
@deprecated
void f() {
}
"""
		parser = FunctionModifierParser()
		elem = parser.parse(text, 0)
		self.assertEqual(elem.content(), "@override\n@deprecated")

	def test_function_locator(self):
		locator = ClassLocator()
		class_blocks = locator.locate_all(code)
		self.assertEqual(len(class_blocks), 15)

		locator = FunctionLocator()
		function_blocks = locator.locate_all(code)
		self.assertEqual(len(function_blocks), 1)
		function_block = function_blocks[0]
		self.assertEqual(function_block.typename.content(), "NodeMetadata")
		self.assertEqual(function_block.name.content(), "lazySet")
		self.assertEqual(function_block.content()[-15:], "return meta;\n}\n")

		locator = FunctionLocator(outer_indentation="  ")

		function_blocks = locator.locate_all(code, class_blocks[0].inside_start, class_blocks[0].inside_end)
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

		function_blocks = locator.locate_all(code, class_blocks[1].inside_start, class_blocks[1].inside_end)
		self.assertEqual(len(function_blocks), 0)

		function_blocks = locator.locate_all(code, class_blocks[6].inside_start, class_blocks[6].inside_end)
		self.assertEqual(function_blocks[0].name.content(), "copyWith")
		self.assertEqual(function_blocks[0].parameter_list.content(), "{\n    CssLength bottom,\n    CssLength left,\n    CssLength right,\n    CssLength top,\n  }")
		self.assertEqual(function_blocks[0].inside_content(), "\n      CssMargin()\n        ..bottom = bottom ?? this.bottom\n        ..left = left ?? this.left\n        ..right = right ?? this.right\n        ..top = top ?? this.top")
		self.assertEqual(len(function_blocks), 1)

		function_blocks = locator.locate_all(code, class_blocks[7].inside_start, class_blocks[7].inside_end)
		self.assertEqual(function_blocks[0].name.content(), "getValue")
		self.assertEqual(function_blocks[0].parameter_list.content(), "BuilderContext bc, TextStyleBuilders tsb")
		self.assertEqual(function_blocks[0].inside_content()[-16:], "return value;\n  ")
		self.assertEqual(len(function_blocks), 1)

		function_blocks = locator.locate_all(code, class_blocks[8].inside_start, class_blocks[8].inside_end)
		self.assertEqual(function_blocks[0].name.content(), "styles")
		self.assertEqual(function_blocks[0].parameter_list.content(), "void f(String key, String value)")
		self.assertEqual(function_blocks[0].inside_content()[-34:], "f(key, iterator.current);\n    }\n  ")
		self.assertEqual(len(function_blocks), 1)

		function_blocks = locator.locate_all(code, class_blocks[13].inside_start, class_blocks[13].inside_end)
		self.assertEqual(function_blocks[0].name.content(), "addBit")
		self.assertEqual(function_blocks[0].modifiers.content(), "@override")
		self.assertEqual(function_blocks[0].parameter_list.content(), "TextBit bit, {int index}")
		self.assertEqual(function_blocks[0].inside_content(), "\n      _children.insert(index ?? _children.length, bit)")
		self.assertEqual(function_blocks[1].name.content(), "addSpace")
		self.assertEqual(function_blocks[1].modifiers.content(), "@override\n  @deprecated")
		self.assertEqual(function_blocks[1].parameter_list.content(), "String data")
		self.assertEqual(function_blocks[1].inside_content()[-15:], "return true;\n  ")
		self.assertEqual(function_blocks[4].name.content(), "forEachBit")
		self.assertEqual(function_blocks[4].parameter_list.content(), "void f(TextBit bit, int index), {bool reversed = false}")
		self.assertEqual(function_blocks[4].inside_content()[-15:], "return true;\n  ")
		self.assertEqual(len(function_blocks), 9)


if __name__ == '__main__':
	unittest.main()
