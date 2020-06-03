import sys


def transpile_keyword(keyword):
	keywords = {
		'def': 'def'
	}

	if keyword in keywords.keys():
		return keywords[keyword]

	return False


def transpile_function(function):
	functions = {
		'respond': 'return jsonify',
		'deep': 'AskLibrary.deep'
	}

	if function in functions.keys():
		return functions[function]

	return False


def parser(tokens, current_token):
	global parsed
	global return_run
	global start_is_block
	global indent_layers

	token = tokens[current_token]

	token_type = token[0]
	token_val = token[1]

	if return_run:
		return_run = False
		return token_val
	else:
		if token_type == 'FUNCTION':
			if token_val[0] == '@':
				return_run = True
				parsed.append('@app.route(\'' + parser(tokens, current_token + 1) + '\', methods=[\'' + token_val[1:].upper() + '\'])')
				start_is_block = True
			elif transpile_function(token_val):
				parsed.append(transpile_function(token_val) + '(')
		elif token_type == 'KEYWORD' and transpile_keyword(token_val):
			if token_val == 'def':
				start_is_block = True
			parsed.append(transpile_keyword(token_val))
		elif token_type == 'START':
			if start_is_block:
				start_is_block = False
				indent_layers.append('\t')
				parsed.append(':\n')
			else:
				parsed.append('{\n')
		elif token_type == 'END':
			parsed.append('\n}\n')
			if indent_layers:
				indent_layers.pop(-1)
		elif token_type == 'OPERATOR':
			parsed.append(token_val)
		elif token_type == 'DICT_KEY':
			parsed.append('\'' + token_val + '\'')
		elif token_type == 'VAR':
			parsed.append(token_val)

		if indent_layers:
			last_token = parsed[-1]
			last_token = ''.join(indent_layers) + last_token

			parsed[-1] = last_token





	# Recursively calls parser() when there is more code to parse
	if len(tokens) - 1 > current_token:
		parser(tokens, current_token + 1)



def tokenizer(line):
	tokens = []

	tmp = ''

	is_string = False
	is_number = False
	is_var = False
	is_property = False
	global active_start
	global is_waiting_for_function_start

	operators = ['+', '-', '*', '/', '%', '<', '>', '=', '!', '.', ':', ',', ')', ';']
	keywords = ['True', 'False', 'in', 'break', 'continue', 'return', 'not', 'pass', 'else', 'and', 'or', 'global', 'def']

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
			if not is_waiting_for_function_start:
				active_start = True
		elif char == '}':

			if is_waiting_for_function_start:
				is_waiting_for_function_start = False
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
						if tmp == 'def':
							is_waiting_for_function_start = True
						tmp = ''
	return tokens


def fix_up_line(source_line):
	return source_line.replace('\t', '')


# Global variables set up
active_start = False
is_waiting_for_function_start = False
parsed = []
return_run = False
start_is_block = False
indent_layers = []

# Start
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


tokens = []

for line in tokenized_lines:
	for token in line:
		tokens.append(token)

print('--TOKENS:')
for token in tokens:
	print(token)
parser(tokens, 0)
print('\n--PARSED:')
print(''.join(parsed))
