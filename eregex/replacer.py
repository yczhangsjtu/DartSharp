from eregex.locator import next_line_start, start_of_line

class Replacer(object):
	"""Replacer"""
	def __init__(self, text, start=0, end=-1):
		super(Replacer, self).__init__()
		self.text = text
		self.start = start
		if end < 0:
			end = len(text)
		self.end = end
		self.replaces = []
		self.error_messages = []
		self.line_number_map = self.create_line_number_map()
		if end < 0:
			end = len(text)

	def create_line_number_map(self):
		curr, lineno, m = 0, 1, {}
		while curr < len(self.text):
			m[curr] = lineno
			curr = next_line_start(self.text, curr)
			lineno += 1
		m[curr] = lineno
		return m

	def get_line_number(self, pos):
		return self.line_number_map[start_of_line(self.text, pos)]

	def get_col_number(self, pos):
		return pos - start_of_line(self.text, pos) + 1

	def get_line_col(self, pos):
		return "(line %d, col %d)" % (self.get_line_number(pos), self.get_col_number(pos))

	def update(self, request):
		start, end, replacement = request
		if not self.contains(request):
			self.error_messages.append("Request out of scope: %s\nScope is %s-%s, request is %s-%s\n" %
				(	self.generate_location_message(start, end),\
					self.get_line_col(self.start), self.get_line_col(self.end),\
					self.get_line_col(start), self.get_line_col(end)))
			return False

		for req in self.replaces:
			if self.conflict(req, request):
				self.error_messages.append("Conflicting requests: %s\nand %s\n, requested scopes are %s-%s and %s-%s\n" %
					(self.generate_location_message(req[0], req[1]), self.generate_location_message(request[0], request[1]),\
					self.get_line_col(req[0]), self.get_line_col(req[1]),\
					self.get_line_col(request[0]), self.get_line_col(request[1])))
				return False

		self.replaces.append(request)
		return True

	def digest(self):
		self.replaces.sort(key = lambda req: req[0]*10000+req[1])
		curr, slices = self.start, []
		for replace in self.replaces:
			if curr < replace[0]:
				slices.append(self.text[curr:replace[0]])
			slices.append(replace[2])
			curr = replace[1]
		if curr < self.end:
			slices.append(self.text[curr:self.end])
		return "".join(slices)

	def generate_line_message(self, pos):
		lineno = self.get_line_number(pos)
		linestart = start_of_line(self.text, pos)
		if linestart >= len(self.text):
			return "    eof"
		return "%7d: %s" % (lineno, self.text[linestart:next_line_start(self.text, linestart)])

	def generate_location_message(self, start, end):
		start_lineno = self.get_line_number(start)
		end_lineno = self.get_line_number(end)
		if end == start_of_line(self.text, end):
			end_lineno -= 1
		if end_lineno > start_lineno + 1:
			return "line [%d-%d]\n%s...%s" % (start_lineno, end_lineno,\
				self.generate_line_message(start_lineno), self.generate_line_message(end_lineno))
		if end_lineno > start_lineno:
			return "line [%d-%d]\n%s%s" % (start_lineno, end_lineno,\
				self.generate_line_message(start_lineno), self.generate_line_message(end_lineno))
		return "line %d\n%s" % (start_lineno, self.generate_line_message(start_lineno))

	def contains(self, request):
		return self.start <= request[0] and self.end >= request[1]

	def conflict(self, req1, req2):
		return (req1[0] == req2[0] and req1[1] == req2[1]) or\
				   (req1[1] > req2[0] and req2[1] > req1[0])
