
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

class NumberElement(BasicElement):
	"""NumberElement"""
	def __init__(self, text, start, end, int_part, frac_part=None, span=None):
		super(NumberElement, self).__init__(text, start, end, span)
		self.int_part = int_part
		self.frac_part = frac_part

class BoolElement(BasicElement):
	def __init__(self, text, start, end, value, span=None):
		super(BoolElement, self).__init__(text, start, end, span)
		self.value = value

class JoinElement(BasicElement):
	"""JoinElement"""
	def __init__(self, text, elements, span=None, start=None, end=None):
		if elements is None or len(elements) == 0:
			self.start = 0
			self.end = 0
			self.text = None
			self.span = None
			self.elements = None
		else:
			if start is None:
				start = elements[0].start
			if end is None:
				end = elements[-1].end

			super(JoinElement, self).__init__(text, start, end, span)
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
	def __init__(self, text, elements, span=None, has_trailing_seperater=False, start=None, end=None):
		super(ListElement, self).__init__(text, elements, span, start, end)
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
