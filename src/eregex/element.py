
class BasicElement:

	def __init__(self, text, start, end, span=None):

		if(start > end or
			start < 0 or
			end > len(text) or
			(span is not None and (span[0] > start or span[1] < end))):
			self.start = 0
			self.end = 0
			self.text = None
			self.span = None
			return

		self.text = text
		self.start = start
		self.end = end
		if span is None:
			self.span = (start, end)
		else:
			self.span = span

	def content(self):
		if self.text is None:
			return None

		return self.text[self.start:self.end]

	def textspan(self):
		if self.text is None:
			return None

		return self.text[self.span[0]:self.span[1]]

class WordElement(BasicElement):
	pass


class StringElement(BasicElement):
	pass

class JoinElement(BasicElement):
	"""JoinElement"""
	def __init__(self, text, elements, span=None):
		if elements is None or len(elements) == 0:
			self.start = 0
			self.end = 0
			self.text = None
			self.span = None
			self.elements = None
		else:
			super(JoinElement, self).__init__(text, elements[0].start, elements[-1].end, span)
			self.elements = elements

	def __len__(self):
		if self.elements is None:
			return 0
		return len(self.elements)

	def __getitem__(self, key):
		if self.elements is None:
			return None
		return self.elements[key]

class ListElement(JoinElement):
	"""ListElement"""
	def __init__(self, text, elements, span=None, has_trailing_seperater=False):
		super(ListElement, self).__init__(text, elements, span)
		self.has_trailing_seperater = has_trailing_seperater

class TypeNameElement(BasicElement):
	"""TypeNameElement"""
	def __init__(self, text, name, template_types=None, span=None):
		end = name.end
		if template_types is not None:
			end = template_types.span[1]
		super(TypeNameElement, self).__init__(text, name.start, end, span)
		self.name = name
		self.template_types = template_types
