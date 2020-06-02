import sys


class Class:
	value = None

	def __init__(self, value):
		self.value = value

	def get_value(self):
		return self.value

	def set_value(self, value):
		self.value = value


class Function:
	value = None

	def __init__(self, value):
		self.value = value

	def get_value(self):
		return self.value

	def set_value(self, value):
		self.value = value


class Keyword:
	value = ''

	def __init__(self, value):
		self.value = value

	def get_value(self):
		return self.value

	def set_value(self, value):
		self.value = value


class Operator:
	value = None

	def __init__(self, value):
		self.value = value

	def get_value(self):
		return self.value

	def set_value(self, value):
		self.value = value


class Number:
	value = ''

	def __init__(self, value):
		self.value = value

	def get_value(self):
		return self.value

	def set_value(self, value):
		self.value = value

	def add_to_value(self, to_add):
		self.set_value(
			int(
				str(
					self.get_value()
				) + to_add
			)
		)


class String:
	value = ''

	def __init__(self, value):
		self.value = value

	def get_value(self):
		return self.value

	def set_value(self, value):
		self.value = value


class Variable:
	value = None,
	data_type = None,

	def __init__(self, data_type, value):
		self.data_type = data_type
		self.value = value

	def get_value(self):
		return self.value

	def get_data_type(self):
		return self.data_type

	def set_value(self, value):
		self.value = value

	def set_data_type(self, data_type):
		self.data_type = data_type


def is_class(possible):
	if len(possible) >= 1:
		return possible[0].isupper()
	return False


# Splits line up into keywords and data
def pre_tokenizer(source_line):
	tokens = []

	tmp = ''

	# Switches
	is_var = False
	is_string = False

	operators = ['=', '+', ')', '{', '}', ',', '#']
	keywords = ['in', 'import', 'export', 'use']

	for char_index, char in enumerate(source_line):
		if char == '$':
			tokens.append(Variable(None, None))
			is_var = True
		elif char == '\'' or char == '"':
			if is_string:
				tokens[-1].set_value(tmp)
			else:
				tokens.append(String(None))

			is_string = not is_string
		elif char == '(':
			tokens.append(Function(tmp))
			tmp = ''
		elif char in operators or char_index == len(source_line) - 1:
			if is_var:
				tokens[-1].set_data_type('VAR')
				tokens[-1].set_value(tmp)
				is_var = False
				tmp = ''

			if char in operators:
				if char == '{' and is_class(tmp):
					tokens.append(Class(tmp))

				if char == '#':
					break

				tokens.append(Operator(char))
		elif not is_string and char.isnumeric() or char == '-':
			if tokens:
				if isinstance(tokens[-1], Number):
					tokens[-1].add_to_value(char)
					continue
			tokens.append(Number(char))
		else:
			if char == ' ' and is_string or char != ' ':
				tmp += char
				if tmp[-2:] == 'in' and is_var:
					tokens[-1].set_data_type('VAR')
					tokens[-1].set_value(tmp[:-2])
					is_var = False
					tmp = ''

					tokens.append(Keyword('IN'))
				# Keyword check
				if not is_string and not is_var:
					if tmp in keywords:
						tokens.append(Keyword(tmp))
						tmp = ''

	return tokens


def fix_up_line(source_line):
	return source_line.replace('\t', '')


filename = sys.argv[1]

with open(filename) as f:
	source_lines = f.readlines()


tokenized_lines = []

for line in source_lines:
	tokenized_lines.append(pre_tokenizer(fix_up_line(line)))

for line in tokenized_lines:
	for token in line:
		print('Class:')
		print(token)
		print('Class value:')
		print(token.get_value())
