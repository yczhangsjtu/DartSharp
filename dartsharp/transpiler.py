from dart.function import FunctionLocator, ConstructorLocator
from dart.classes import ClassLocator
from eregex.replacer import Replacer
from eregex.element import NumberElement

class DartSharpTranspiler(object):
	"""DartSharpTranspiler"""
	def __init__(self, global_class_name="Utils", indent="  ", double_to_float=True):
		super(DartSharpTranspiler, self).__init__()
		self.global_class_name = global_class_name
		self.class_locator = ClassLocator(inner_indentation=indent)
		self.function_locator = FunctionLocator(inner_indentation=indent)
		self.double_to_float = double_to_float
		self.reset()

	def reset(self):
		self.global_functions = {}
		self.global_variables = {}
		self.class_variables = {}
		self.error_messages = []

	def transpile_dart_code(self, code):
		self.reset()
		replacer = Replacer(code)

		class_blocks = self.class_locator.locate_all(code)
		for class_block in class_blocks:
			replacer.update((class_block.start, class_block.end, self.transpile_class(class_block)))

		global_functions = self.function_locator.locate_all(code)
		for func in global_functions:
			replacer.update((func.start, func.end, self.transpile_function(func)))

		self.error_messages.extend(replacer.error_messages)

		return replacer.digest()

	def transpile_class(self, class_block):
		replacer = Replacer(class_block.text, class_block.start, class_block.end)

		replacer.update((class_block.header.start, class_block.header.end, self.transpile_class_header(class_block.header)))

		if class_block.functions is not None:
			for func in class_block.functions:
				replacer.update((func.start, func.end, self.transpile_function(func)))

		if class_block.constructors is not None:
			for constructor in class_block.constructors:
				replacer.update((constructor.start, constructor.end, self.transpile_constructor(constructor)))

		self.error_messages.extend(replacer.error_messages)

		return replacer.digest()

	def transpile_class_header(self, header):
		replacer = Replacer(header.text, header.start, header.end)
		words = []
		if not header.name.content().startswith("_"):
			words.append("public")
		if header.is_abstract:
			words.append("abstract")
		words.append("class")
		words.append(header.name.content())

		extensions = []
		if header.extends is not None:
			extensions.extend(map(lambda element: element.content(), header.extends.elements))
		if header.with_mixes is not None:
			extensions.extend(map(lambda element: element.content(), header.with_mixes.elements))
		if header.implements is not None:
			extensions.extend(map(lambda element: element.content(), header.implements.elements))
		if len(extensions) > 0:
			words.append(":")
			words.extend(extensions)

		return " ".join(words)

	def transpile_function(self, func):
		replacer = Replacer(func.text, func.start, func.end)
		replacer.update((func.header.start, func.header.end, self.transpile_funcheader(func.header, func.override)))
		if func.modifiers is not None:
			replacer.update((func.modifiers.start, func.modifiers.end, ""))

		self.error_messages.extend(replacer.error_messages)
		return replacer.digest()

	def transpile_constructor(self, constructor):
		replacer = Replacer(constructor.text, constructor.start, constructor.end)
		self.error_messages.extend(replacer.error_messages)
		return replacer.digest()

	def transpile_funcheader(self, header, override):
		replacer = Replacer(header.text, header.start, header.end)
		name_parts = []
		if not header.name.content().startswith("_"):
			name_parts.append("public")
		if override:
			name_parts.append("override")
		if self.double_to_float and header.typename.content() == "double":
			name_parts.append("float")
		else:
			name_parts.append(header.typename.content())
		name_parts.append(header.name.content())
		return "%s(%s)" % (" ".join(name_parts), self.transpile_parameter_list(header.parameter_list))

	def transpile_parameter_list(self, parameter_list):
		lists = []
		if parameter_list.positioned is not None:
			lists.append(self.transpile_positioned_parameter_list(parameter_list.positioned))
		if parameter_list.named is not None:
			lists.append(self.transpile_named_parameter_list(parameter_list.named))
		return ",".join(lists)

	def transpile_positioned_parameter_list(self, parameter_list):
		replacer = Replacer(parameter_list.text, parameter_list.start, parameter_list.end)
		items = parameter_list.elements
		for i in range(len(items)):
			if items[i].default_value is None:
				replacer.update((items[i].start, items[i].end, self.transpile_parameter_item(items[i])))
		self.error_messages.extend(replacer.error_messages)
		return replacer.digest()

	def transpile_named_parameter_list(self, parameter_list):
		replacer = Replacer(parameter_list.text, parameter_list.start, parameter_list.end)
		items = parameter_list.elements
		for i in range(len(items)):
			if items[i].default_value is None:
				replacer.update((items[i].start, items[i].end, self.transpile_parameter_item(items[i], add_default_value=True)))
		self.error_messages.extend(replacer.error_messages)
		return replacer.digest()[1:-1]

	def transpile_parameter_item(self, parameter_item, add_default_value=False):
		items = []

		default_value = None
		if parameter_item.default_value is not None:
			default_value = parameter_item.default_value.content()

		typename = None
		if parameter_item.typename is not None:
			typename = parameter_item.typename.content()
			if self.double_to_float and typename == "double":
				typename = "float"
				if default_value is not None and isinstance(parameter_item.default_value, NumberElement):
					default_value = default_value + "f"

		if default_value is None and add_default_value:
			default_value = "null"
			if typename == "int":
				default_value = "0"
			elif typename == "float":
				default_value = "0.0f"
			elif typename == "double":
				default_value = "0.0"
			elif typename == "bool":
				default_value = "false"

		if typename is not None:
			items.append(typename)
		items.append(parameter_item.name.content())
		if default_value is not None:
			items.append("=")
			items.append(default_value)

		return " ".join(items)
