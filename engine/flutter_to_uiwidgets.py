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
			"package:flutter/animation.dart": "Unity.UIWidgets.animation",
			"package:flutter/cupertino.dart": "Unity.UIWidgets.cupertino",
			"package:flutter/scheduler.dart": "Unity.UIWidgets.scheduler",
		}
		self.keyword_namespace_map = {
			"TextStyle" : "Unity.UIWidgets.painting",
			"TextSpan": "Unity.UIWidgets.paiting",
			"GestureRecognizer": "Unity.UIWidgets.gestures",
			"Color": "Unity.UIWidgets.ui",
		}
		self.word_map = {
		}

	def get_namespace(self, dart_package):
		if dart_package in self.package_namespace_map:
			return self.package_namespace_map[dart_package]
		return None

	def require_namespace(self, word):
		if word in self.keyword_namespace_map:
			return self.keyword_namespace_map[word]
		return None

	def map_word(self, word):
		if word in self.word_map:
			return self.word_map[word]
		return None