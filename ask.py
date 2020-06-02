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


def tokenizer(line):
	tokens = []

	tmp = ''

	is_string = False
	is_number = False
	is_var = False
	is_property = False
	global active_start

	operators = ['+', '-', '*', '/', '%', '<', '>', '=', '!', '.', ':', ',', ')', ';']
	keywords = ['True', 'False', 'in', 'break', 'continue', 'return', 'respond', 'not', 'pass', 'else', 'and', 'or', 'global']

	for char_index, char in enumerate(line):
		if char == '"' or char == '\'':
			if is_string:
				is_string = False
				tokens.append(['STRING', tmp])
				tmp = ''
			else:
				is_string = True
				tmp = ''
		elif char == '$' and is_string is False:
			is_var = True
		elif char == '{':
			tokens.append(['START', char])
			active_start = True
		elif char == '}':
			active_start = False
			if is_var:
				if is_property:
					tokens.append(['PROPERTY', tmp])
					is_property = False
					tmp = ''
					tokens.append(['END', char])
					continue

				tokens.append(['VAR', tmp])
				is_var = False
				tmp = ''

			tokens.append(['END', char])
		elif char == '(':
			tokens.append(['FUNCTION', tmp])
			tmp = ''
		elif not is_string and not is_var and char.isnumeric() or char == '-' and not is_number:
			is_number = True
			tmp += char

			if not line[char_index+1].isnumeric() and line[char_index+1] != '-':
				tokens.append(['NUMBER', tmp])
				tmp = ''
				is_number = False

		elif char == '[':
			if is_var:
				if is_property:
					tokens.append(['PROPERTY', tmp])
					is_property = False
					tmp = ''
					continue

				tokens.append(['VAR', tmp])
				is_var = False
				tmp = ''
			tokens.append(['LIST_START', '['])
		elif char == ']':
			tokens.append(['LIST_END', ']'])
		elif char in operators and is_string is False or char_index == len(line) - 1 and is_string is False:
			if is_var:
				is_var = False
				if is_property:
					tokens.append(['PROPERTY', tmp])
					is_property = False
					tmp = ''

					if char != '\n':
						tokens.append(['OPERATOR', char])
					continue

				tokens.append(['VAR', tmp])
				tmp = ''
			elif active_start and char == ':':
				tokens.append(['DICT_KEY', tmp])
				tmp = ''

			if char == '.':
				is_property = True
				is_var = True

			if char != '\n':
				tokens.append(['OPERATOR', char])
		else:
			if char != ' ' or char == ' ' and is_string:
				if char == '#':
					break
				else:
					tmp += char

					# Checks for keyword
					if is_var and len(tmp) >= 2:
						if tmp[-2:] in ['in', '||', '&&']:
							tokens.append(['VAR', tmp[:-2]])
							tokens.append(['KEYWORD', tmp[-2:]])
							is_var = False
							tmp = ''
					elif tmp in keywords and not is_var:
						tokens.append(['KEYWORD', tmp])
						tmp = ''
	return tokens


def fix_up_line(source_line):
	return source_line.replace('\t', '')


active_start = False

is_multi_line_comment = False

filename = sys.argv[1]

with open(filename) as f:
	source_lines = f.readlines()


tokenized_lines = []

for line in source_lines:
	line = fix_up_line(line)
	if line[:2] == '/*':
		is_multi_line_comment = True
		continue
	elif line[:2] == '*/':
		is_multi_line_comment = False
		continue

	if not is_multi_line_comment:
		tokenized_line = tokenizer(line)
		if tokenized_line:
			tokenized_lines.append(tokenized_line)

print(tokenized_lines)
