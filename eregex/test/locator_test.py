import unittest
from eregex.parser import SpacePlainParser
from eregex.test.data import code
from eregex.locator import BlockFinder, LineFinder,\
	next_line_start, indentation_at

class TestGlobalFunctions(unittest.TestCase):
	"""GlobalFunctions"""
	def test_next_line_start(self):
		text = """
ABC DEF HIJK
  LMN OPQ RST
U

V
"""
		self.assertEqual(next_line_start(text, 0), 1)
		self.assertEqual(next_line_start(text, 1), 14)
		self.assertEqual(next_line_start(text, 2), 14)
		self.assertEqual(next_line_start(text, 5), 14)
		self.assertEqual(next_line_start(text, 13), 14)
		self.assertEqual(next_line_start(text, 14), 28)
		self.assertEqual(next_line_start(text, 15), 28)
		self.assertEqual(next_line_start(text, 27), 28)
		self.assertEqual(next_line_start(text, 28), 30)
		self.assertEqual(next_line_start(text, 29), 30)
		self.assertEqual(next_line_start(text, 30), 31)
		self.assertEqual(next_line_start(text, 31), 33)
		self.assertEqual(next_line_start(text, 32), 33)
		self.assertEqual(next_line_start(text, 33), 33)

		self.assertEqual(text[next_line_start(text, 0):next_line_start(text, 1)], "ABC DEF HIJK\n")

	def test_indentation(self):
		text = """
1
 \t2

3
    4
\t5
\t\t6
"""
		self.assertEqual(indentation_at(text, 0), "")
		self.assertEqual(indentation_at(text, 1), "")
		self.assertEqual(indentation_at(text, 3), " \t")
		self.assertEqual(indentation_at(text, 7), "")
		self.assertEqual(indentation_at(text, 8), "")
		self.assertEqual(indentation_at(text, 10), "    ")
		self.assertEqual(indentation_at(text, 16), "\t")
		self.assertEqual(indentation_at(text, 19), "\t\t")
		self.assertEqual(indentation_at(text, 23), "")

class TestFinders(unittest.TestCase):
	"""TestFinders"""
	def test_block_finder(self):
		finder = BlockFinder(SpacePlainParser("class"), "}")
		blocks = finder.find_all(code, 0)
		self.assertEqual(len(blocks), 13)
		self.assertEqual(blocks[0].content()[:16], "\nclass BuildOp {")
		self.assertEqual(blocks[0].content()[-2:], "}\n")
		self.assertEqual(blocks[-1].content()[:26], "\nclass TextStyleBuilders {")
		self.assertEqual(blocks[-1].content()[-2:], "}\n")

	def test_line_finder(self):
		finder = LineFinder(SpacePlainParser("typedef"))
		elements = finder.find_all(code, 0)
		self.assertEqual(len(elements), 6)
		self.assertEqual(code[elements[0].start:elements[0].start+24], "typedef Iterable<String>")
		self.assertEqual(code[elements[1].start:elements[1].start+20], "typedef NodeMetadata")
		self.assertEqual(code[elements[2].start:elements[2].start+28], "typedef Iterable<BuiltPiece>")
		self.assertEqual(code[elements[3].start:elements[3].start+24], "typedef Iterable<Widget>")
		self.assertEqual(code[elements[4].start:elements[4].start+20], "typedef NodeMetadata")
		self.assertEqual(code[elements[5].start:elements[5].start+17], "typedef TextStyle")

	def test_line_finder_inside_block(self):
		block_finder = BlockFinder(SpacePlainParser("class"), "}")
		blocks = block_finder.find_all(code, 0)
		self.assertEqual(len(blocks), 13)
		block = blocks[0]

		line_finder = LineFinder(SpacePlainParser("final"), indentation="  ")
		elements = line_finder.find_all(block.text, block.start, block.end)
		self.assertEqual(len(elements), 6)

		line_finder = LineFinder(SpacePlainParser("final"), indentation="   ")
		elements = line_finder.find_all(block.text, block.start, block.end)
		self.assertEqual(len(elements), 0)


if __name__ == '__main__':
	unittest.main()