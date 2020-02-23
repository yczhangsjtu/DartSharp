import re

class PostProcessor(object):
	"""PostProcessor"""
	def __init__(self):
		super(PostProcessor, self).__init__()
		self.patterns = [
			(re.compile(r"^(\s*)final(\s+\w+\s*=)", flags=re.MULTILINE), r"\1var\2"),
			(re.compile(r"^(\s*)final\s+([_A-Za-z0-9<,>]+\s+\w+\s*=)", flags=re.MULTILINE), r"\1\2"),
			(re.compile(r"^(\s*)for(\s*\(\s*)final(\s+)", flags=re.MULTILINE), r"\1foreach\2var\3"),
			(re.compile(r"([(:]\s*\([_A-Za-z0-9 ,]+\)) ({)"), r"\1 => \2"),
			(re.compile(r",(\n\s*\))"), r"\1"),
			(re.compile(r"^(\s*\w+\s+)'([^']*)'([;:,])$", re.MULTILINE), r"""\1"\2"\3"""),
			(re.compile(r"\['(\w+)'\]"), r"""["\1"]"""),
			(re.compile(r"\('(\w+)'\)"), r"""("\1")"""),
			(re.compile(r"^(\s*)([\w.]+)(\s*)\?\?=(\s*)", re.MULTILINE), r"\1\2\3=\4\2\3??\4"),
			(re.compile(r"<(\w+)>\[\]"), r"new List<\1>()"),
			(re.compile(r"\bsuper\b"), r"base"),
			(re.compile(r"\bString\b"), r"string"),
		]

	def post_process(self, text):
		for pattern in self.patterns:
			text = pattern[0].sub(pattern[1], text)
		return text