from eregex.element import BasicElement, JoinElement, ListElement
from eregex.parser import OptionalParser, JoinParser,\
	SpacePlainParser, SpaceParser, TypeNameParser,\
	ListParser, OrParser, EmptyParser
from eregex.locator import Block, BlockLocator

class ClassHeaderElement(BasicElement):
	"""ClassHeaderElement"""
	def __init__(self, text, start, end, span,\
			name, is_abstract, extends, with_mixes, implements):
		super(ClassHeaderElement, self).__init__(text, start, end, span)
		self.name = name
		self.is_abstract = is_abstract
		self.extends = extends
		self.with_mixes = with_mixes
		self.implements = implements

class ClassExtensionElement(BasicElement):
	"""ClassExtensionElement"""
	def __init__(self, text, start, end, span, name, elements):
		super(ClassExtensionElement, self).__init__(text, start, end, span)
		self.name = name
		self.elements = elements

class ClassExtensionParser(object):
	"""ClassExtensionParser"""
	def __init__(self):
		super(ClassExtensionParser, self).__init__()
		self.parser = JoinParser([
			SpaceParser(),
			OrParser([
				SpacePlainParser("extends"),
				SpacePlainParser("with"),
				SpacePlainParser("implements"),
			]),
			SpaceParser(),
			ListParser(TypeNameParser(), SpacePlainParser(","))
		])

	def parse(self, text, pos):
		elem = self.parser.parse(text, pos)
		if elem is None:
			return None
		name, elements = elem[1], elem[3]
		return ClassExtensionElement(text, name.start, elements.end, elem.span, name, elements)

class ClassHeaderParser(object):
	"""docstring for ClassHeaderParser"""
	def __init__(self):
		super(ClassHeaderParser, self).__init__()
		self.parser = JoinParser([
			OptionalParser(JoinParser([SpacePlainParser("abstract"), SpaceParser()])),
			SpacePlainParser("class"),
			SpaceParser(),
			TypeNameParser(),
			OptionalParser(ListParser(
				ClassExtensionParser(),
				EmptyParser()
			)),
			SpacePlainParser("{")
		])

	def parse(self, text, pos):
		elem = self.parser.parse(text, pos)
		if elem is None:
			return None
		is_abstract = type(elem[0]) is JoinElement
		if is_abstract:
			start = elem.start
		else:
			start = elem[1].start
		name = elem[3]
		extends, with_mixes, implements = None, None, None
		if type(elem[4]) is ListElement:
			for i in range(len(elem[4])):
				extension_elem = elem[4][i]
				if extension_elem.name.content() == "extends":
					extends = extension_elem.elements
				elif extension_elem.name.content() == "with":
					with_mixes = extension_elem.elements
				elif extension_elem.name.content() == "implements":
					implements = extension_elem.elements
		return ClassHeaderElement(text, start, elem[4].end, elem.span,\
			name, is_abstract, extends, with_mixes, implements)

class ClassBlock(Block):
	"""ClassBlock"""
	def __init__(self, text, start, end, indentation, header,\
			constructors=None, functions=None, abstract_functions=None,\
			setters=None, getters=None, attributes=None):
		super(ClassBlock, self).__init__(text, start, end, indentation)
		self.header = header
		self.is_abstract = header.is_abstract
		self.name = header.name
		self.extends = header.extends
		self.with_mixes = header.with_mixes
		self.implements = header.implements
		self.constructors = constructors
		self.functions = functions
		self.abstract_functions = abstract_functions
		self.setters = setters
		self.getters = getters
		self.attributes = attributes

class ClassLocator(object):
	"""docstring for ClassLocator"""
	def __init__(self):
		super(ClassLocator, self).__init__()
		self.locator = BlockLocator(ClassHeaderParser())

	def locate(self, text, pos):
		block = self.locator.locate(text, pos)
		if block is None:
			return None

		return self.create_class_block(block)

	def locate_all(self, text, start=0, end=-1):
		blocks = self.locator.locate_all(text, start, end)
		return list(map(lambda block: self.create_class_block(block), blocks))

	def create_class_block(self, block):
		return ClassBlock(block.text, block.start, block.end, block.indentation, block.element)