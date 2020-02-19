from dart.function import FunctionLocator, ConstructorLocator
from dart.classes import ClassLocator
from eregex.replacer import Replacer

class DartSharpTranspiler(object):
	"""DartSharpTranspiler"""
	def __init__(self, global_class_name="Utils", indent="  "):
		super(DartSharpTranspiler, self).__init__()
		self.global_class_name = global_class_name
		self.class_locator = ClassLocator(inner_indentation=indent)
		self.function_locator = FunctionLocator(inner_indentation=indent)
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
		return replacer.digest()

	def transpile_function(self, func):
		replacer = Replacer(func.text, func.start, func.end)
		return replacer.digest()

	def transpile_constructor(self, constructor):
		replacer = Replacer(constructor.text, constructor.start, constructor.end)
		return replacer.digest()
