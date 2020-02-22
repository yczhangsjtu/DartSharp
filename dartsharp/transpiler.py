from dart.function import FunctionLocator, ConstructorLocator, VariableDeclareLocator
from dart.expression import DartListElement, FunctionInvocationElement, DoubleDotElement,\
  is_capitalized, AssignmentElement
from dart.classes import ClassLocator, GetterLocator
from dart.globals import ImportLocator, PartOfLocator, TypedefLocator
from eregex.replacer import Replacer
from eregex.element import NumberElement, StringElement
import re

class DartSharpTranspiler(object):
  """DartSharpTranspiler"""
  def __init__(self, global_class_name="Utils", indent="  ", double_to_float=True, engines=[]):
    super(DartSharpTranspiler, self).__init__()
    self.global_class_name = global_class_name
    self.import_locator = ImportLocator(indentation="")
    self.part_of_locator = PartOfLocator(indentation="")
    self.class_locator = ClassLocator(inner_indentation=indent)
    self.function_locator = FunctionLocator(inner_indentation=indent)
    self.variable_declare_locator = VariableDeclareLocator(indentation="")
    self.typedef_locator = TypedefLocator(indentation="")
    self.double_to_float = double_to_float
    self.indent = indent
    self.engines = engines
    self.reset()

  def reset(self):
    self.global_functions = {}
    self.global_variables = {}
    self.class_attributes = {}
    self.needed_namespaces = {}
    self.need_initialize = {}
    self.setters = {}
    self.error_messages = []

  def using_namespace(self, namespace):
    if namespace is not None:
      self.needed_namespaces[namespace] = True

  def get_namespaces(self):
    return "\n".join(map(lambda x: "using %s;" % x, self.needed_namespaces.keys()))

  def get_static_util_class(self):
    parts = []
    parts.extend(self.global_functions.values())
    parts.extend(self.global_variables.values())
    return "static class %s {\n%s\n}" % (self.global_class_name, self.indented("\n\n".join(parts)))

  def front_matter(self):
    parts = []
    if len(self.needed_namespaces) > 0:
      parts.append(self.get_namespaces())

    if len(self.global_functions) + len(self.global_variables) > 0:
      parts.append(self.get_static_util_class())

    if len(parts) > 0:
      return "\n\n".join(parts)

    return ""

  def get_class_attribute_type(self, class_name, attribute_name):
    if class_name in self.class_attributes:
      if attribute_name in self.class_attributes[class_name]:
        return self.class_attributes[class_name][attribute_name]

  def add_need_initialize(self, class_name, attribute_name):
    if class_name not in self.need_initialize:
      self.need_initialize[class_name] = []

    if attribute_name not in self.need_initialize[class_name]:
      self.need_initialize[class_name].append(attribute_name)

  def add_setter(self, class_name, setter):
    if class_name not in self.setters:
      self.setters[class_name] = {}

    self.setters[class_name][setter.name.content()] = setter

  def get_setter(self, class_name, name):
    if class_name not in self.setters:
      return None

    if name not in self.setters[class_name]:
      return None

    return self.setters[class_name][name]

  def transpile_dart_code(self, code):
    self.reset()
    replacer = Replacer(code)

    imports = self.import_locator.locate_all(code)
    for imp in imports:
      replacer.update((imp.start, imp.end, ""))
      for engine in self.engines:
        namespace = engine.get_namespace(imp.target.inside_content())
        if namespace is not None:
          self.using_namespace(namespace)

    part_ofs = self.part_of_locator.locate_all(code)
    for part_of in part_ofs:
      replacer.update((part_of.start, part_of.end, ""))

    global_variables = self.variable_declare_locator.locate_all(code)
    for global_variable in global_variables:
      gv = self.transpile_attribute(global_variable).strip()
      if not gv.startswith("public"):
        gv = "public static %s" % gv
      else:
        gv = "public static%s" % gv[6:]
      self.global_variables[global_variable.name.content()] = gv
      replacer.update((global_variable.start, global_variable.end, ""))

    global_functions = self.function_locator.locate_all(code)
    for func in global_functions:
      gf = self.transpile_function(func).strip()
      if not gf.startswith("public"):
        gf = "public static %s" % gf
      else:
        gf = "public static%s" % gf[6:]
      self.global_functions[func.name.content()] = gf
      replacer.update((func.start, func.end, ""))

    class_blocks = self.class_locator.locate_all(code)
    for class_block in class_blocks:
      replacer.update((class_block.start, class_block.end, self.transpile_class(class_block)))

    typedefs = self.typedef_locator.locate_all(code)
    for typedef in typedefs:
      replacer.update((typedef.start, typedef.end, self.transpile_typedef(typedef)))

    replacer.update((0, 0, self.front_matter()))

    self.error_messages.extend(replacer.error_messages)

    return replacer.digest()

  def transpile_class(self, class_block):
    replacer = Replacer(class_block.text, class_block.start, class_block.end)

    replacer.update((class_block.header.start, class_block.header.end, self.transpile_class_header(class_block.header)))

    self.class_attributes[class_block.name.name.content()] = {}
    if class_block.attributes is not None:
      for attribute in class_block.attributes:
        replacer.update((attribute.start, attribute.end, self.transpile_attribute(attribute, class_block.name)))

    if class_block.functions is not None:
      for func in class_block.functions:
        replacer.update((func.start, func.end, self.transpile_function(func)))

    if class_block.setters is not None:
      for setter in class_block.setters:
        self.add_setter(class_block.name.content(), setter)

    if class_block.getters is not None:
      for getter in class_block.getters:
        replacer.update((getter.start, getter.end, self.transpile_getter(getter, class_block.name.content())))
        setter = self.get_setter(class_block.name.content(), getter.name.content())
        if setter is not None:
          del self.setters[class_block.name.content()][setter.name.content()]
          replacer.update((setter.start, setter.end, ""))

    if class_block.name.content() in self.setters:
      for name in self.setters[class_block.name.content()]:
        setter = self.setters[class_block.name.content()][name]
        replacer.update((setter.start, setter.end, self.transpile_setter(setter)))

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

  def transpile_typedef(self, typedef):
    items = []
    if not typedef.name.content().startswith("_"):
      items.append("public")

    items.append("delegate")

    header = self.transpile_funcheader(typedef.header, override=False)
    if header.startswith("public "):
      header = header[7:]
    items.append(header)
    return "%s;" % " ".join(items)

  def transpile_attribute(self, attribute, class_name=None):
    items = []
    if not attribute.name.content().startswith("_"):
      items.append("public")

    if attribute.modifier is not None:
      if attribute.modifier.content() == "final" or\
        attribute.modifier.content() == "const":
        items.append("readonly")

    if attribute.typename is not None:
      typename = self.transpile_typename(attribute.typename)
    else:
      typename = self.deduce_type(attribute.default_value)
      if typename is None:
        self.error_messages.append("Cannot deduce type of %s." % attribute.default_value.content())
    if typename is not None:
      items.append(typename)
      if class_name is not None:
        self.class_attributes[class_name.name.content()][attribute.name.content()] = typename

    items.append(attribute.name.content())

    if attribute.default_value is not None:
      items.append("=")
      items.append(self.transpile_expression(attribute.default_value))

    return "%s;" % " ".join(items)

  def transpile_variable_declare(self, attribute, func_name=None):
    items = []

    if attribute.modifier is not None:
      if attribute.modifier.content() == "var":
        items.append("var")

    if attribute.typename is not None:
      items.append(self.transpile_typename(attribute.typename))
    elif len(items) == 0 or items[-1] != "var":
      items.append("var")

    items.append(attribute.name.content())

    if attribute.default_value is not None:
      items.append("=")
      items.append(self.transpile_expression(attribute.default_value))

    return "%s;" % " ".join(items)

  def transpile_function(self, func):
    replacer = Replacer(func.text, func.start, func.end)
    replacer.update((func.header.start, func.header.end, self.transpile_funcheader(func.header, func.override)))
    if func.modifiers is not None:
      replacer.update((func.modifiers.start, func.modifiers.end, ""))

    if func.statements is not None:
      for statement in func.statements:
        replacer.update((statement.start, statement.end, self.transpile_statement(statement)))

    if func.variable_declares is not None:
      for variable_declare in func.variable_declares:
        replacer.update((variable_declare.start, variable_declare.end, self.transpile_variable_declare(variable_declare, func.name)))

    if func.for_in_blocks is not None:
      for for_in_block in func.for_in_blocks:
        replacer.update((for_in_block.start, for_in_block.end, self.transpile_for_in_block(for_in_block)))

    if func.expression_body is not None:
      replacer.update((func.expression_body.start, func.expression_body.end, self.transpile_expression(func.expression_body)))

    self.error_messages.extend(replacer.error_messages)
    return replacer.digest()

  def transpile_statement(self, statement):
    element = statement.element
    if isinstance(element, FunctionInvocationElement):
      return "%s;" % self.transpile_function_invocation(element)
    if isinstance(element, AssignmentElement):
      if element.sign.content() == "??=":
        left = element.left.content()
        right = self.transpile_expression(element.right)
        return "%s = %s ?? %s;" % (left, left, right)
    return statement.content()

  def transpile_getter(self, getter, class_name):
    header_parts = []

    if not getter.name.content().startswith("_"):
      header_parts.append("public")

    if getter.override:
      header_parts.append("override")

    header_parts.append(self.transpile_typename(getter.typename))
    header_parts.append(getter.name.content())

    header = " ".join(header_parts)
    if getter.is_arrow:
      body = "return %s;" % getter.inside_content()
    else:
      body = getter.inside_content()

    setter = self.get_setter(class_name, getter.name.content())
    if setter is None:
      return "\n%s%s {\n%s%sget {\n%s%s%s\n%s%s}\n%s}" % (
        getter.indentation,
        header,
        getter.indentation,
        self.indent,
        getter.indentation,
        self.indent,
        self.indented(body),
        getter.indentation,
        self.indent,
        getter.indentation
      )

    return "\n%s%s {\n%s%sget {\n%s%s%s\n%s%s}\n\n%s%s%s\n%s}" % (
      getter.indentation,
      header,
      getter.indentation,
      self.indent,
      getter.indentation,
      self.indent,
      self.indented(body),
      getter.indentation,
      self.indent,
      getter.indentation,
      self.indent,
      self.transpile_setter(setter, only_inside=True),
      getter.indentation
    )

  def transpile_setter(self, setter, only_inside=False):
    header_parts = []

    if not setter.name.content().startswith("_"):
      header_parts.append("public")

    if setter.override:
      header_parts.append("override")

    header_parts.append(self.transpile_typename(setter.typename))
    header_parts.append(setter.name.content())

    header = " ".join(header_parts)
    if setter.is_arrow:
      body = "%s;" % re.sub(r"\b%s\b" % setter.variable.content(), "value", setter.inside_content())
    else:
      body = re.sub(r"\b%s\b" % setter.variable.content(), "value", setter.inside_content())

    if only_inside:
      return "set {\n%s%s%s\n%s%s}" % (
        setter.indentation,
        self.indent,
        self.indented(body),
        setter.indentation,
        self.indent,
      )

    return "\n%s%s {\n%s%sset {\n%s%s%s\n%s%s}\n%s}" % (
      setter.indentation,
      header,
      setter.indentation,
      self.indent,
      setter.indentation,
      self.indent,
      self.indented(body),
      setter.indentation,
      self.indent,
      setter.indentation
    )

  def transpile_constructor(self, constructor):
    replacer = Replacer(constructor.text, constructor.start, constructor.end)

    replacer.update((constructor.header.start, constructor.header.end, self.transpile_constructor_header(constructor.header)))

    body_start, body_end = constructor.header.end, constructor.end
    body_indentation = "%s%s" % (constructor.indentation, self.indent)
    body_parts = [" {"]

    if constructor.name.content() in self.need_initialize:
      attributes = self.need_initialize[constructor.name.content()]
      body_parts.append("%s%s" % (body_indentation, ("\n%s" % body_indentation).join(
        map(lambda a: "this.%s = %s;" % (a, a), attributes)
      )))

    if constructor.initializer_content() is not None:
      body_parts.append("%s%s;" % (body_indentation, constructor.initializer_content().strip()))

    if constructor.braced_content() is not None:
      body_parts.append(constructor.braced_content())

    body_parts.append("%s}" % constructor.indentation)

    replacer.update((body_start, body_end, "\n".join(body_parts)))
    self.error_messages.extend(replacer.error_messages)
    return replacer.digest()

  def transpile_funcheader(self, header, override):
    replacer = Replacer(header.text, header.start, header.end)
    name_parts = []
    if not header.name.content().startswith("_"):
      name_parts.append("public")
    if override:
      name_parts.append("override")
    if self.double_to_float and self.transpile_typename(header.typename) == "double":
      name_parts.append("float")
    else:
      name_parts.append(self.transpile_typename(header.typename))
    name_parts.append(self.transpile_func_name(header.name))
    return "%s(%s)" % (" ".join(name_parts), self.transpile_parameter_list(header.parameter_list))

  def transpile_func_name(self, name):
    if name.content() in self.global_functions:
      return "%s.%s" % (self.global_class_name, name.content())

    if name.content() == "super":
      return "base"

    if name.content().startswith("super."):
      return "base%s" % name.content()[5:]

    return name.content()

  def transpile_constructor_header(self, header):
    replacer = Replacer(header.text, header.start, header.end)
    name_parts = []
    if not header.name.content().startswith("_"):
      name_parts.append("public")
    name_parts.append(header.name.content())
    return "%s(%s)" % (" ".join(name_parts), self.transpile_parameter_list(header.parameter_list, header.name))

  def transpile_parameter_list(self, parameter_list, class_name=None):
    lists = []
    if parameter_list.positioned is not None:
      lists.append(self.transpile_positioned_parameter_list(parameter_list.positioned, class_name))
    if parameter_list.named is not None:
      lists.append(self.transpile_named_parameter_list(parameter_list.named, class_name))
    result = ", ".join(lists)
    if result.strip().endswith(","):
      index = result.rfind(",")
      result = result[:index] + result[index+1:]
    return result

  def transpile_positioned_parameter_list(self, parameter_list, class_name=None):
    replacer = Replacer(parameter_list.text, parameter_list.start, parameter_list.end)
    items = parameter_list.elements
    for i in range(len(items)):
      if items[i].default_value is None:
        replacer.update((items[i].start, items[i].end, self.transpile_parameter_item(items[i], class_name=class_name)))
    self.error_messages.extend(replacer.error_messages)
    return replacer.digest()

  def transpile_named_parameter_list(self, parameter_list, class_name=None):
    replacer = Replacer(parameter_list.text, parameter_list.start, parameter_list.end)
    items = parameter_list.elements
    for i in range(len(items)):
      replacer.update((items[i].start, items[i].end, self.transpile_parameter_item(items[i], add_default_value=True, class_name=class_name)))
    self.error_messages.extend(replacer.error_messages)
    return replacer.digest()[1:-1]

  def transpile_parameter_item(self, parameter_item, add_default_value=False, class_name=None):
    items = []

    default_value = None
    if parameter_item.default_value is not None:
      default_value = self.transpile_expression(parameter_item.default_value)

    typename = None
    if parameter_item.typename is not None:
      typename = self.transpile_typename(parameter_item.typename)
      if self.double_to_float and typename == "double":
        typename = "float"
        if default_value is not None and isinstance(parameter_item.default_value, NumberElement):
          default_value = default_value + "f"
    else:
      if class_name is not None:
        typename = self.get_class_attribute_type(class_name.content(), parameter_item.name.content())
        self.add_need_initialize(class_name.content(), parameter_item.name.content())

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

    if parameter_item.required:
      items.append("/* @required */")

    if typename is not None:
      items.append(typename)

    items.append(parameter_item.name.content())
    if default_value is not None:
      items.append("=")
      items.append(default_value)

    return " ".join(items)

  def transpile_for_in_block(self, for_in_block):
    replacer = Replacer(for_in_block.text, for_in_block.start, for_in_block.end)
    replacer.update((for_in_block.forword.start, for_in_block.forword.end, "foreach"))
    if for_in_block.typename.content() == "final":
      replacer.update((for_in_block.typename.start, for_in_block.typename.end, "var"))
    if for_in_block.for_in_blocks is not None:
      for subblock in for_in_block.for_in_blocks:
        replacer.update((subblock.start, subblock.end, self.transpile_for_in_block(subblock)))
    self.error_messages.extend(replacer.error_messages)
    return replacer.digest()

  def transpile_typename(self, typename):
    if typename.content() == "String":
      return "string"

    replacer = Replacer(typename.text, typename.start, typename.end)
    for engine in self.engines:
      namespace = engine.require_namespace(typename.name.content())
      if namespace is not None:
        self.using_namespace(namespace)
      mapped_word = engine.map_word(typename.name.content())
      if mapped_word is not None:
        replacer.update((typename.name.start, typename.name.end, mapped_word))
        break

    if typename.template_types is not None:
      for i in range(len(typename.template_types)):
        replacer.update((typename.template_types[i].start,
          typename.template_types[i].end,
          self.transpile_typename(typename.template_types[i])))

    self.error_messages.extend(replacer.error_messages)
    return replacer.digest()

  def transpile_expression(self, value):
    expression = value.expression

    if isinstance(expression, DartListElement):
      self.using_namespace("System.Collections.Generic")
      replacer = Replacer(expression.text, expression.start, expression.end)
      if expression.typename is not None:
        replacer.update((expression.bracket.start, expression.bracket.end, "List<%s>" % self.transpile_typename(expression.typename)))
      else:
        replacer.update((expression.start, expression.start, "List"))
      if expression.elements is None:
        replacer.update((expression.open_bracket.start, expression.close_bracket.end, "()"))
      else:
        replacer.update((expression.open_bracket.start, expression.open_bracket.end, "{"))
        replacer.update((expression.close_bracket.start, expression.close_bracket.end, "}"))
        for i in range(len(expression.elements)):
          replacer.update((expression.elements[i].start, expression.elements[i].end, self.transpile_expression(expression.elements[i])))
      self.error_messages.extend(replacer.error_messages)
      return replacer.digest()

    if isinstance(expression, FunctionInvocationElement):
      return self.transpile_function_invocation(expression)

    if isinstance(expression, StringElement):
      if expression.is_raw:
        return "@\"%s\"" % expression.inside_content()
      else:
        return "\"%s\"" % expression.inside_content()

    if isinstance(expression, DoubleDotElement):
      replacer = Replacer(expression.text, expression.start, expression.end)
      replacer.update((expression.expression.start, expression.expression.end, self.transpile_expression(expression.expression)))
      for i in range(len(expression.arms)):
        arm = expression.arms[i]
        double_dots = arm[0]
        replacer.update((double_dots.start, double_dots.start+1, "tmp"))
      replacer.update((expression.arms.start, expression.arms.start, "/* "))
      replacer.update((expression.arms.end, expression.arms.end, " */"))
      self.error_messages.extend(replacer.error_messages)
      return replacer.digest()

    return expression.content()

  def transpile_function_invocation(self, function_invocation):
    expression = function_invocation
    replacer = Replacer(expression.text, expression.start, expression.end)
    replacer.update((expression.name.start, expression.name.end, self.transpile_func_name(expression.name)))
    if expression.arguments is not None:
      for i in range(len(expression.arguments)):
        replacer.update((expression.arguments[i].value.start, expression.arguments[i].value.end, self.transpile_expression(expression.arguments[i].value)))
    if expression.modifier is not None:
      if expression.modifier.content() == "const":
        if is_capitalized(expression.pure_name()):
          replacer.update((expression.modifier.start, expression.modifier.end, "new"))
        else:
          replacer.update((expression.modifier.start, expression.modifier.end, ""))
    else:
      if is_capitalized(expression.pure_name()):
        replacer.update((expression.name.start, expression.name.start, "new "))
    self.error_messages.extend(replacer.error_messages)
    return replacer.digest()

  def deduce_type(self, value):
    expression = value.expression

    if isinstance(expression, NumberElement):
      if expression.frac_part is not None:
        if self.double_to_float:
          return "float"
        else:
          return "double"
      else:
        return "int"

    if isinstance(expression, StringElement):
      return "string"

    if isinstance(expression, DartListElement):
      if expression.typename is not None:
        return "List<%s>" % self.transpile_typename(expression.typename)
      return "List"

    if isinstance(expression, FunctionInvocationElement):
      if is_capitalized(expression.pure_name()):
        return expression.name.content()
      pcn = expression.possible_class_name()
      if pcn is not None:
        return pcn
      return None

    if expression.content() == "true" or expression.content() == "false":
      return "bool"

    if expression.content().endswith(".length"):
      return "int"

    return None

  def indented(self, text, steps=1):
    return "%s%s" % (self.indent, text.replace("\n", "\n%s" % self.indent * steps))
