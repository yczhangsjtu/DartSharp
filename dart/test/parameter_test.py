import unittest
from dart.parameter import NormalParameterItemElement,\
  NormalParameterItemParser, ThisParameterItemElement,\
  ThisParameterItemParser, ParameterItemParser,\
  SingleParameterListParser, ParameterListParser

lazy_set_func="""
NodeMetadata lazySet(
  NodeMetadata meta, {
  BuildOp buildOp,
  Color color,
  bool decoOver,
  bool decoStrike,
  bool decoUnder,
  TextDecorationStyle decorationStyle,
  CssBorderStyle decorationStyleFromCssBorderStyle,
  String fontFamily = null,
  String fontSize,
  bool fontStyleItalic = false,
  FontWeight fontWeight,
  double size = 1.0,
  bool isBlockElement,
  bool isNotRenderable,
  Iterable<BuildOp> parentOps,
  Iterable<String> styles,
  Iterable<String> stylesPrepend = null,
}) {
  meta ??= NodeMetadata();

  if (buildOp != null) {
    meta._buildOps ??= [];
    final ops = meta._buildOps as List<BuildOp>;
    if (ops.indexOf(buildOp) == -1) {
      ops.add(buildOp);
    }
  }

  if (color != null) meta.color = color;

  if (decoStrike != null) meta.decoStrike = decoStrike;
  if (decoOver != null) meta.decoOver = decoOver;
  if (decoUnder != null) meta.decoUnder = decoUnder;

  if (decorationStyle != null) meta.decorationStyle = decorationStyle;
  if (decorationStyleFromCssBorderStyle != null) {
    switch (decorationStyleFromCssBorderStyle) {
      case CssBorderStyle.dashed:
        meta.decorationStyle = TextDecorationStyle.dashed;
        break;
      case CssBorderStyle.dotted:
        meta.decorationStyle = TextDecorationStyle.dotted;
        break;
      case CssBorderStyle.double:
        meta.decorationStyle = TextDecorationStyle.double;
        break;
      case CssBorderStyle.solid:
        meta.decorationStyle = TextDecorationStyle.solid;
        break;
    }
  }

  if (fontFamily != null) meta.fontFamily = fontFamily;
  if (fontSize != null) meta.fontSize = fontSize;
  if (fontStyleItalic != null) meta.fontStyleItalic = fontStyleItalic;
  if (fontWeight != null) meta.fontWeight = fontWeight;

  if (isBlockElement != null) meta._isBlockElement = isBlockElement;
  if (isNotRenderable != null) meta.isNotRenderable = isNotRenderable;

  if (parentOps != null) {
    assert(meta._parentOps == null);
    meta._parentOps = parentOps;
  }

  if (stylesPrepend != null) {
    styles = stylesPrepend;
  }
  if (styles != null) {
    assert(styles.length % 2 == 0);
    assert(!meta._stylesFrozen);
    meta._styles ??= [];
    if (styles == stylesPrepend) {
      meta._styles.insertAll(0, styles);
    } else {
      meta._styles.addAll(styles);
    }
  }

  return meta;
}
"""

build_op_class="""
class BuildOp {
  final bool isBlockElement;

  // op with lower priority will run first
  final int priority;

  final BuildOpDefaultStyles _defaultStyles;
  final BuildOpOnChild _onChild;
  final BuildOpOnPieces _onPieces;
  final BuildOpOnWidgets _onWidgets;

  BuildOp({
    BuildOpDefaultStyles defaultStyles,
    bool isBlockElement,
    BuildOpOnChild onChild,
    BuildOpOnPieces onPieces,
    BuildOpOnWidgets onWidgets,
    this.width,
    this.size = 1.0,
    this.offset = -5.0,
    this.name = "FirstOp",
    this.priority = 10,
  })  : _defaultStyles = defaultStyles,
        this.isBlockElement = isBlockElement ?? onWidgets != null,
        _onChild = onChild,
        _onPieces = onPieces,
        _onWidgets = onWidgets;

  bool get hasOnChild => _onChild != null;

  List<String> defaultStyles(NodeMetadata meta, dom.Element e) =>
      _defaultStyles != null ? _defaultStyles(meta, e) : null;

  NodeMetadata onChild(NodeMetadata meta, dom.Element e) =>
      _onChild != null ? _onChild(meta, e) : meta;

  Iterable<BuiltPiece> onPieces(
    NodeMetadata meta,
    Iterable<BuiltPiece> pieces,
  ) =>
      _onPieces != null ? _onPieces(meta, pieces) : pieces;

  Iterable<Widget> onWidgets(NodeMetadata meta, Iterable<Widget> widgets) =>
      (_onWidgets != null ? _onWidgets(meta, widgets) : null) ?? widgets;
}
"""

node_meta_data_class="""
class NodeMetadata {
  Iterable<BuildOp> _buildOps;
  dom.Element _domElement;
  Iterable<BuildOp> _parentOps;
  TextStyleBuilders _tsb;

  Color color;
  bool decoOver;
  bool decoStrike;
  bool decoUnder;
  TextDecorationStyle decorationStyle;
  String fontFamily;
  String fontSize;
  bool fontStyleItalic;
  FontWeight fontWeight;
  bool _isBlockElement;
  bool isNotRenderable;
  List<String> _styles;
  bool _stylesFrozen = false;

  dom.Element get domElement => _domElement;

  bool get hasOps => _buildOps != null;

  bool get hasParents => _parentOps != null;

  Iterable<BuildOp> get ops => _buildOps;

  Iterable<BuildOp> get parents => _parentOps;

  TextStyleBuilders get tsb => _tsb;

  set domElement(dom.Element e) {
    assert(_domElement == null);
    _domElement = e;

    if (_buildOps != null) {
      final ops = _buildOps as List;
      ops.sort((a, b) => a.priority.compareTo(b.priority));
      _buildOps = List.unmodifiable(ops);
    }
  }

  set tsb(TextStyleBuilders tsb) {
    assert(_tsb == null);
    _tsb = tsb;
  }

  bool get isBlockElement {
    if (_isBlockElement == true) return true;
    return _buildOps?.where((o) => o.isBlockElement)?.length?.compareTo(0) == 1;
  }

  void styles(void f(String key, String value)) {
    _stylesFrozen = true;
    if (_styles == null) return;

    final iterator = _styles.iterator;
    while (iterator.moveNext()) {
      final key = iterator.current;
      if (!iterator.moveNext()) return;
      f(key, iterator.current);
    }
  }
}
"""

class TestParameterElements(unittest.TestCase):
  """TestParameterElements"""
  def test_normal_parameter_item(self):
    parser = NormalParameterItemParser()

    pos = lazy_set_func.find("TextDecorationStyle decorationStyle")
    elem = parser.parse(lazy_set_func, pos-2)
    self.assertEqual(elem.content(), "TextDecorationStyle decorationStyle")
    self.assertEqual(elem.textspan(), "  TextDecorationStyle decorationStyle")
    self.assertEqual(elem.typename.content(), "TextDecorationStyle")
    self.assertEqual(elem.name.content(), "decorationStyle")
    self.assertEqual(elem.default_value, None)

    pos = lazy_set_func.find("String fontFamily")
    elem = parser.parse(lazy_set_func, pos-2)
    self.assertEqual(elem.content(), "String fontFamily = null")
    self.assertEqual(elem.textspan(), "  String fontFamily = null")
    self.assertEqual(elem.typename.content(), "String")
    self.assertEqual(elem.name.content(), "fontFamily")
    self.assertEqual(elem.default_value.content(), "null")

    pos = lazy_set_func.find("bool fontStyleItalic")
    elem = parser.parse(lazy_set_func, pos-2)
    self.assertEqual(elem.content(), "bool fontStyleItalic = false")
    self.assertEqual(elem.textspan(), "  bool fontStyleItalic = false")
    self.assertEqual(elem.typename.content(), "bool")
    self.assertEqual(elem.name.content(), "fontStyleItalic")
    self.assertEqual(elem.default_value.content(), "false")

    pos = lazy_set_func.find("double size")
    elem = parser.parse(lazy_set_func, pos-2)
    self.assertEqual(elem.content(), "double size = 1.0")
    self.assertEqual(elem.textspan(), "  double size = 1.0")
    self.assertEqual(elem.typename.content(), "double")
    self.assertEqual(elem.name.content(), "size")
    self.assertEqual(elem.default_value.content(), "1.0")

    pos = lazy_set_func.find("Iterable<String> stylesPrepend")
    elem = parser.parse(lazy_set_func, pos-2)
    self.assertEqual(elem.content(), "Iterable<String> stylesPrepend = null")
    self.assertEqual(elem.textspan(), "  Iterable<String> stylesPrepend = null")
    self.assertEqual(elem.typename.content(), "Iterable<String>")
    self.assertEqual(elem.name.content(), "stylesPrepend")
    self.assertEqual(elem.default_value.content(), "null")

  def test_this_parameter_item(self):
    parser = ThisParameterItemParser()

    pos = build_op_class.find("this.width")
    elem = parser.parse(build_op_class, pos-2)
    self.assertEqual(elem.content(), "this.width")
    self.assertEqual(elem.textspan(), "  this.width")
    self.assertEqual(elem.name.content(), "width")
    self.assertEqual(elem.default_value, None)

    pos = build_op_class.find("this.size = 1.0")
    elem = parser.parse(build_op_class, pos-2)
    self.assertEqual(elem.content(), "this.size = 1.0")
    self.assertEqual(elem.textspan(), "  this.size = 1.0")
    self.assertEqual(elem.name.content(), "size")
    self.assertEqual(elem.default_value.content(), "1.0")

    pos = build_op_class.find("this.offset = -5.0")
    elem = parser.parse(build_op_class, pos-2)
    self.assertEqual(elem.content(), "this.offset = -5.0")
    self.assertEqual(elem.textspan(), "  this.offset = -5.0")
    self.assertEqual(elem.name.content(), "offset")
    self.assertEqual(elem.default_value.content(), "-5.0")

    pos = build_op_class.find('this.name = "FirstOp"')
    elem = parser.parse(build_op_class, pos-2)
    self.assertEqual(elem.content(), 'this.name = "FirstOp"')
    self.assertEqual(elem.textspan(), '  this.name = "FirstOp"')
    self.assertEqual(elem.name.content(), "name")
    self.assertEqual(elem.default_value.content(), '"FirstOp"')

    pos = build_op_class.find("this.priority = 10")
    elem = parser.parse(build_op_class, pos-2)
    self.assertEqual(elem.content(), "this.priority = 10")
    self.assertEqual(elem.textspan(), "  this.priority = 10")
    self.assertEqual(elem.name.content(), "priority")
    self.assertEqual(elem.default_value.content(), "10")

  def test_parameter_item(self):
    parser = ParameterItemParser()

    pos = lazy_set_func.find("double size")
    elem = parser.parse(lazy_set_func, pos-2)
    self.assertEqual(elem.content(), "double size = 1.0")
    self.assertEqual(elem.textspan(), "  double size = 1.0")
    self.assertEqual(elem.typename.content(), "double")
    self.assertEqual(elem.name.content(), "size")
    self.assertEqual(elem.default_value.content(), "1.0")

    pos = lazy_set_func.find("Iterable<String> stylesPrepend")
    elem = parser.parse(lazy_set_func, pos-2)
    self.assertEqual(elem.content(), "Iterable<String> stylesPrepend = null")
    self.assertEqual(elem.textspan(), "  Iterable<String> stylesPrepend = null")
    self.assertEqual(elem.typename.content(), "Iterable<String>")
    self.assertEqual(elem.name.content(), "stylesPrepend")
    self.assertEqual(elem.default_value.content(), "null")

    pos = build_op_class.find('this.name = "FirstOp"')
    elem = parser.parse(build_op_class, pos-2)
    self.assertEqual(elem.content(), 'this.name = "FirstOp"')
    self.assertEqual(elem.textspan(), '  this.name = "FirstOp"')
    self.assertEqual(elem.name.content(), "name")
    self.assertEqual(elem.default_value.content(), '"FirstOp"')

    pos = build_op_class.find("this.priority = 10")
    elem = parser.parse(build_op_class, pos-2)
    self.assertEqual(elem.content(), "this.priority = 10")
    self.assertEqual(elem.textspan(), "  this.priority = 10")
    self.assertEqual(elem.name.content(), "priority")
    self.assertEqual(elem.default_value.content(), "10")

  def test_single_parameter_list(self):
    parser = SingleParameterListParser(allow_trailing_comma=True, curly_brace=True)
    pos = lazy_set_func.find("{")
    elem = parser.parse(lazy_set_func, pos-1)
    self.assertEqual(elem[0].content(), "BuildOp buildOp")
    self.assertEqual(elem[-1].content(), "Iterable<String> stylesPrepend = null")
    self.assertTrue(elem.has_trailing_comma)
    self.assertEqual(elem.content(), lazy_set_func[pos:lazy_set_func.find("}")+1])
    self.assertEqual(elem.textspan(), lazy_set_func[pos-1:lazy_set_func.find("}")+1])

    parser = SingleParameterListParser(allow_trailing_comma=True, curly_brace=False)
    pos = lazy_set_func.find("{")
    elem = parser.parse(lazy_set_func, pos+1)
    self.assertEqual(elem[0].content(), "BuildOp buildOp")
    self.assertEqual(elem[-1].content(), "Iterable<String> stylesPrepend = null")
    self.assertTrue(elem.has_trailing_comma)
    self.assertEqual(elem.content(), lazy_set_func[pos+4:lazy_set_func.find("}")-1])
    self.assertEqual(elem.textspan(), lazy_set_func[pos+1:lazy_set_func.find("}")-1])

  def test_parameter_list(self):
    parser = ParameterListParser()

    pos = lazy_set_func.find("(")
    elem = parser.parse(lazy_set_func, pos+1)
    self.assertEqual(len(elem.positioned), 1)
    self.assertFalse(elem.positioned.has_trailing_comma)
    self.assertEqual(elem.positioned.content(), "NodeMetadata meta")
    self.assertEqual(elem.positioned.textspan(), "\n  NodeMetadata meta")
    self.assertEqual(elem.named[0].content(), "BuildOp buildOp")
    self.assertEqual(elem.named[-1].content(), "Iterable<String> stylesPrepend = null")
    self.assertTrue(elem.named.has_trailing_comma)
    self.assertEqual(elem.named.content(), lazy_set_func[lazy_set_func.find("{"):lazy_set_func.find("}")+1])
    self.assertEqual(elem.named.textspan(), lazy_set_func[lazy_set_func.find("{")-1:lazy_set_func.find("}")+1])

if __name__ == '__main__':
  unittest.main()