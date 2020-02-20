import unittest
from dart.globals import ImportParser

class TestImport(unittest.TestCase):
	def test_import(self):
		parser = ImportParser()
		elem = parser.parse("import 'package:flutter/widgets.dart';", 0)
		self.assertEqual(elem.content(), "import 'package:flutter/widgets.dart';")
		self.assertEqual(elem.target.content(), "'package:flutter/widgets.dart'")
		self.assertEqual(elem.alias, None)

		elem = parser.parse("import 'package:html/parser.dart' as parser;", 0)
		self.assertEqual(elem.content(), "import 'package:html/parser.dart' as parser;")
		self.assertEqual(elem.target.content(), "'package:html/parser.dart'")
		self.assertEqual(elem.alias.content(), "parser")

		elem = parser.parse("import \"package:flutter/widgets.dart\";", 0)
		self.assertEqual(elem.content(), "import \"package:flutter/widgets.dart\";")
		self.assertEqual(elem.target.content(), "\"package:flutter/widgets.dart\"")
		self.assertEqual(elem.alias, None)

		elem = parser.parse("import \"package:html/parser.dart\" as parser;", 0)
		self.assertEqual(elem.content(), "import \"package:html/parser.dart\" as parser;")
		self.assertEqual(elem.target.content(), "\"package:html/parser.dart\"")
		self.assertEqual(elem.alias.content(), "parser")

if __name__ == "__main__":
	unittest.main()