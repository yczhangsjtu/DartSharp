from eregex.element import BasicElement, JoinElement, ListElement
from eregex.parser import OptionalParser, JoinParser,\
	SpacePlainParser, SpaceParser, TypeNameParser,\
	ListParser, OrParser, EmptyParser, WordParser
from eregex.locator import Block, BlockLocator, locate_all
from dart.function import FunctionLocator, ConstructorLocator,\
	FunctionModifierParser, FunctionModifierElement
from dart.variable import VariableDeclareLocator

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
		self.inside_start = header.span[1]
		self.inside_end = end-2

	def inside_content(self):
		return self.text[self.inside_start:self.inside_end]

class ClassLocator(object):
	"""ClassLocator"""
	def __init__(self, outer_indentation="", inner_indentation="  "):
		super(ClassLocator, self).__init__()
		self.locator = BlockLocator(ClassHeaderParser(), indentation=outer_indentation)
		self.function_locator = FunctionLocator(
			outer_indentation=outer_indentation+inner_indentation,
			inner_indentation=inner_indentation)
		self.getter_locator = GetterLocator(
			outer_indentation=outer_indentation+inner_indentation,
			inner_indentation=inner_indentation)
		self.setter_locator = SetterLocator(
			outer_indentation=outer_indentation+inner_indentation,
			inner_indentation=inner_indentation)
		self.variable_declare_locator =VariableDeclareLocator(indentation=inner_indentation)
		self.outer_indentation = outer_indentation
		self.inner_indentation = inner_indentation

	def locate(self, text, pos):
		block = self.locator.locate(text, pos)
		if block is None:
			return None

		return self.create_class_block(block)

	def locate_all(self, text, start=0, end=-1):
		return locate_all(self, text, start, end)

	def create_class_block(self, block):
		class_block = ClassBlock(block.text, block.start, block.end, block.indentation, block.element)

		functions = self.function_locator.locate_all(class_block.text, class_block.inside_start, class_block.inside_end)
		if len(functions) > 0:
			class_block.functions = functions

		getters = self.getter_locator.locate_all(class_block.text, class_block.inside_start, class_block.inside_end)
		if len(getters) > 0:
			class_block.getters = getters

		setters = self.setter_locator.locate_all(class_block.text, class_block.inside_start, class_block.inside_end)
		if len(setters) > 0:
			class_block.setters = setters

		constructor_locator = ConstructorLocator(
			class_block.name.name.content(),
			outer_indentation=self.outer_indentation+self.inner_indentation,
			inner_indentation=self.inner_indentation)
		constructors = constructor_locator.locate_all(class_block.text, class_block.inside_start, class_block.inside_end)
		if len(constructors) > 0:
			class_block.constructors = constructors

		attributes = self.variable_declare_locator.locate_all(class_block.text, class_block.inside_start, class_block.inside_end)
		if len(attributes) > 0:
			class_block.attributes = attributes

		return class_block

class GetterBlock(Block):
	"""GetterBlock: typename get name => body;
	                typename get name { body; }"""
	def __init__(self, text, start, end, indentation, modifiers, typename, name, inside_start, inside_end, is_arrow):
		super(GetterBlock, self).__init__(text, start, end, indentation)
		self.modifiers = modifiers
		self.typename = typename
		self.name = name
		self.inside_start = inside_start
		self.inside_end = inside_end
		self.is_arrow = is_arrow
		self.override = False
		if modifiers is not None:
			self.override = modifiers.contains("override")

	def inside_content(self):
		return self.text[self.inside_start:self.inside_end]

class GetterLocator(object):

	def __init__(self, outer_indentation="", inner_indentation="  "):
		super(GetterLocator, self).__init__()
		self.brace_locator = BlockLocator(
			JoinParser([FunctionModifierParser(),
				TypeNameParser(),
				SpacePlainParser("get"),
				WordParser(),
				SpacePlainParser("{")]),
			indentation=outer_indentation)
		self.arrow_locator = BlockLocator(
			JoinParser([FunctionModifierParser(),
				TypeNameParser(),
				SpacePlainParser("get"),
				WordParser(),
				SpacePlainParser("=>")]),
			endchar=";",
			indentation=outer_indentation)

	def locate(self, text, pos):
		block = self.brace_locator.locate(text, pos)

		if block is None:
			block = self.arrow_locator.locate(text, pos)

		if block is None:
			return None

		return self.create_getter_block(block)

	def locate_all(self, text, start=0, end=-1):
		return locate_all(self, text, start, end)

	def create_getter_block(self, block):
		if isinstance(block.element[0], FunctionModifierElement):
			modifiers = block.element[0]
		else:
			modifiers = None

		body_starter = block.element[-1]
		is_arrow = body_starter.content() == "=>"
		inside_start = body_starter.span[1]
		if is_arrow:
			inside_end = block.end - 1
		else:
			inside_end = block.end - 2

		"""
		variable_declares = None
		if not is_arrow:
			variable_declares = self.variable_declare_locator.locate_all(block.text, block.start, block.end)
			if len(variable_declares) == 0:
				variable_declares = None
		"""

		"""
		for_in_blocks = None
		if not is_arrow:
			for_in_blocks = self.for_in_locator.locate_all(block.text, block.start, block.end)
			if len(for_in_blocks) == 0:
				for_in_blocks = None
		"""

		return GetterBlock(block.text, block.start, block.end, block.indentation,\
			modifiers, block.element[1], block.element[3], inside_start, inside_end, is_arrow)

class SetterBlock(Block):
	"""SetterBlock: set name(typename variable) => body;
	                set name(typename variable) { body; }"""
	def __init__(self, text, start, end, indentation, modifiers,\
			name, typename, variable, inside_start, inside_end, is_arrow):
		super(SetterBlock, self).__init__(text, start, end, indentation)
		self.modifiers = modifiers
		self.name = name
		self.typename = typename
		self.variable = variable
		self.inside_start = inside_start
		self.inside_end = inside_end
		self.is_arrow = is_arrow
		self.override = False
		if modifiers is not None:
			self.override = modifiers.contains("override")

	def inside_content(self):
		return self.text[self.inside_start:self.inside_end]

class SetterLocator(object):

	def __init__(self, outer_indentation="", inner_indentation="  "):
		super(SetterLocator, self).__init__()
		self.brace_locator = BlockLocator(
			JoinParser([FunctionModifierParser(),
				SpacePlainParser("set"),
				WordParser(),
				SpacePlainParser("("),
				TypeNameParser(),
				WordParser(),
				SpacePlainParser(")"),
				SpacePlainParser("{")]),
			indentation=outer_indentation)
		self.arrow_locator = BlockLocator(
			JoinParser([FunctionModifierParser(),
				SpacePlainParser("set"),
				WordParser(),
				SpacePlainParser("("),
				TypeNameParser(),
				WordParser(),
				SpacePlainParser(")"),
				SpacePlainParser("=>")]),
			endchar=";",
			indentation=outer_indentation)

	def locate(self, text, pos):
		block = self.brace_locator.locate(text, pos)

		if block is None:
			block = self.arrow_locator.locate(text, pos)

		if block is None:
			return None

		return self.create_setter_block(block)

	def locate_all(self, text, start=0, end=-1):
		return locate_all(self, text, start, end)

	def create_setter_block(self, block):
		if isinstance(block.element[0], FunctionModifierElement):
			modifiers = block.element[0]
		else:
			modifiers = None

		body_starter = block.element[-1]
		is_arrow = body_starter.content() == "=>"
		inside_start = body_starter.span[1]
		if is_arrow:
			inside_end = block.end - 1
		else:
			inside_end = block.end - 2

		"""
		variable_declares = None
		if not is_arrow:
			variable_declares = self.variable_declare_locator.locate_all(block.text, block.start, block.end)
			if len(variable_declares) == 0:
				variable_declares = None
		"""

		"""
		for_in_blocks = None
		if not is_arrow:
			for_in_blocks = self.for_in_locator.locate_all(block.text, block.start, block.end)
			if len(for_in_blocks) == 0:
				for_in_blocks = None
		"""

		return SetterBlock(block.text, block.start, block.end, block.indentation,\
			modifiers, block.element[2], block.element[4], block.element[5],\
			inside_start, inside_end, is_arrow)