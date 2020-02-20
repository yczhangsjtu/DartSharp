class FlutterToUIWidgetsEngine(object):
	def __init__(self):
		super(FlutterToUIWidgetsEngine, self).__init__()
		self.package_namespace_map = {
			"package:flutter/widgets.dart": "Unity.UIWidgets.widgets",
			"package:flutter/gestures.dart": "Unity.UIWidgets.gestures",
			"package:flutter/painting.dart": "Unity.UIWidgets.painting",
			"package:flutter/rendering.dart": "Unity.UIWidgets.rendering",
			"package:flutter/foundation.dart": "Unity.UIWidgets.foundation",
			"package:flutter/material.dart": "Unity.UIWidgets.material",
		}
		self.keyword_namespace_map = {
			"TextStyle" : "Unity.UIWidgets.painting"
		}

	def get_namespace(self, dart_package):
		if dart_package in self.package_namespace_map:
			return self.package_namespace_map[dart_package]
		return None

	def require_namespace(self, word):
		if word in self.keyword_namespace_map:
			return self.keyword_namespace_map[word]
		return None