class StandardLibrary(object):
	def __init__(self):
		super(StandardLibrary, self).__init__()
		self.package_namespace_map = {
		}
		self.keyword_namespace_map = {
		}
		self.word_map = {
			"Iterable": "IEnumerator",
			"Function": "Action"
		}

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