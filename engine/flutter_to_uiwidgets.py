class FlutterToUIWidgetsEngine(object):
	def __init__(self):
		super(FlutterToUIWidgetsEngine, self).__init__()
		self.namespace_map = {
			"package:flutter/widgets.dart": "Unity.UIWidgets.widgets",
			"package:flutter/gestures.dart": "Unity.UIWidgets.gestures",
			"package:flutter/paintings.dart": "Unity.UIWidgets.paintings",
			"package:flutter/rendering.dart": "Unity.UIWidgets.rendering",
			"package:flutter/foundation.dart": "Unity.UIWidgets.foundation",
			"package:flutter/material.dart": "Unity.UIWidgets.material",
		}

	def get_namespace(self, dart_package):
		if dart_package in self.namespace_map:
			return self.namespace_map[dart_package]
		return None