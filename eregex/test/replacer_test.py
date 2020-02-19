import unittest
from eregex.replacer import Replacer

text="""
2234567890
3234567890
4234567890
5234567890
6234567890
7234567890
8234567890
9234567890
"""

class TestReplacer(unittest.TestCase):
	"""TestReplacer"""
	def test_replacer_line_col_number(self):
		replacer = Replacer(text)

		self.assertEqual(replacer.get_line_number(0), 1)
		self.assertEqual(replacer.get_col_number(0), 1)

		self.assertEqual(replacer.get_line_number(1), 2)
		self.assertEqual(replacer.get_col_number(1), 1)

		self.assertEqual(replacer.get_line_number(3), 2)
		self.assertEqual(replacer.get_col_number(3), 3)

		self.assertEqual(replacer.get_line_number(11), 2)
		self.assertEqual(replacer.get_col_number(11), 11)

		self.assertEqual(replacer.get_line_number(88), 9)
		self.assertEqual(replacer.get_col_number(88), 11)

	def test_replacer_update_digest(self):
		replacer = Replacer(text)

		self.assertTrue(replacer.update((12, 22, "Line 3")))
		self.assertFalse(replacer.update((21, 22, "Line 3")))
		self.assertEqual(len(replacer.replaces), 1)
		self.assertEqual(replacer.digest(), """
2234567890
Line 3
4234567890
5234567890
6234567890
7234567890
8234567890
9234567890
""")

		self.assertTrue(replacer.update((12, 12, "Start of Line 3:")))
		self.assertEqual(len(replacer.replaces), 2)
		self.assertEqual(replacer.digest(), """
2234567890
Start of Line 3:Line 3
4234567890
5234567890
6234567890
7234567890
8234567890
9234567890
""")

		self.assertFalse(replacer.update((88, 90, "End of Text")))
		self.assertEqual(len(replacer.replaces), 2)
		self.assertEqual(replacer.digest(), """
2234567890
Start of Line 3:Line 3
4234567890
5234567890
6234567890
7234567890
8234567890
9234567890
""")

		self.assertTrue(replacer.update((89, 89, "End of Text")))
		self.assertEqual(len(replacer.replaces), 3)
		self.assertEqual(replacer.digest(), """
2234567890
Start of Line 3:Line 3
4234567890
5234567890
6234567890
7234567890
8234567890
9234567890
End of Text""")

		self.assertFalse(replacer.update((13, 13, "Part of line 3")))
		self.assertEqual(len(replacer.replaces), 3)
		self.assertEqual(replacer.digest(), """
2234567890
Start of Line 3:Line 3
4234567890
5234567890
6234567890
7234567890
8234567890
9234567890
End of Text""")

if __name__ == '__main__':
	unittest.main()