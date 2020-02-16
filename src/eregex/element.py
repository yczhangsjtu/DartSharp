
class BasicElement:

	def __init__(self, text, start, end):

		if(start > end or start < 0 or end > len(text)):
			self.start = 0
			self.end = 0
			self.text = None
			return

		self.text = text
		self.start = start
		self.end = end

	def content(self):
		if self.text is None:
			return None

		return self.text[self.start:self.end]

class WordElement(BasicElement):
	pass

