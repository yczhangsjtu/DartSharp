
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

