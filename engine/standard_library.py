import re

class StandardLibrary(object):
	def __init__(self):
		super(StandardLibrary, self).__init__()
		self.package_namespace_map = {
		}
		self.keyword_namespace_map = {
			"RegExp": "System.Text.RegularExpressions",
		}
		self.word_map = {
			"Iterable": "IEnumerator",
			"Function": "Action",
			"RegExp": "Regex",
		}
		self.patterns = [
			(re.compile(r"(\breturn\b|[?:()])\s*(Regex)\b"), r"\1 new \2"),
			(re.compile(r"\.moveNext\(\)"), r".MoveNext()"),
			(re.compile(r"\.addAll\("), r".AddRange("),
		]

	def get_namespace(self, dart_package):
		if dart_package in self.package_namespace_map:
			return self.package_namespace_map[dart_package]
		return None

	def require_namespace(self, word):
		if word in self.keyword_namespace_map:
			return self.keyword_namespace_map[word]
		return None

	def map_word(self, word):
		if word in self.word_map:
			return self.word_map[word]
		return None

	def post_process(self, text):
		for pattern in self.patterns:
			text = pattern[0].sub(pattern[1], text)
		return text