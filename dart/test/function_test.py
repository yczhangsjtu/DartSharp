import unittest
from dart.test.data import lazy_set_func
from dart.function import FunctionHeaderParser

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

if __name__ == '__main__':
	unittest.main()
