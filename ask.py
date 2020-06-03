import sys


def transpile_keyword(keyword):
	keywords = {
		'def': 'def',
	}

	indents, keyword_stripped = separate_indents_and_content(keyword)

	if keyword_stripped in keywords.keys():
		return indents + keywords[keyword_stripped]

	return False


def transpile_function(function):
	functions = {
		'respond': 'return jsonify',
		'deep': 'AskLibrary.deep',
		'quickPut': 'AskLibrary.quickPut',
	}

	indents, function_name = separate_indents_and_content(function)

	if function_name in functions.keys():
		return indents + functions[function_name]

	return False


def get_vars_used_by_route(url):
	var = ''
	collect = False

	for char in url:
		if char == '<':
			collect = True
		elif collect and char != '>':
			var += char
		elif collect and char == '>':
			collect = False
			break

	return var


def route_url_parser(raw_url):
	if '$' in raw_url:
		head = ''
		tail = ''
		var = ''

		collect = False

		for char_index, char in enumerate(raw_url):
			if char == '$':
				head = raw_url[:char_index]
				collect = True
			elif collect:
				if char != '/':
					var += char
				else:
					tail = raw_url[char_index:]
					collect = False

		return head + '<' + var + '>' + tail

	return raw_url


def separate_indents_and_content(string):
	tmp_indents = ''
	tmp_string = ''

	for tmp_char in string:
		if tmp_char == '\t':
			tmp_indents += '\t'
		else:
			tmp_string += tmp_char

	return tmp_indents, tmp_string


def parser(tokens, current_token):
	global parsed
	global return_run
	global is_route
	global function_in_route_name
	global vars_used_by_route

	token = tokens[current_token]

	token_type = token[0]
	token_val = token[1]

	if return_run:
		return_run = False
		return token_val
	else:
		if token_type == 'FUNCTION':
			if token_val.replace('\t', '')[0] == '@':
				return_run = True
				parsed.append('@app.route(\'' + route_url_parser(parser(tokens, current_token + 1)) + '\', methods=[\'' + token_val.replace('\t', '')[1:].upper() + '\']')

				# Prep. for function in route (used by flask)
				is_route = True

				return_run = True
				function_in_route_name = parser(tokens, current_token + 1).replace('/', '_').replace('$', '').replace('.', '_')
				function_in_route_name += token_val.replace('\t', '')[1:]

				return_run = True
				vars_used_by_route = get_vars_used_by_route(route_url_parser(parser(tokens, current_token + 1)))

				current_token += 1
			elif transpile_function(token_val):
				parsed.append(transpile_function(token_val) + '(')
			else:
				parsed.append(token_val + '(')
		elif token_type == 'KEYWORD' and transpile_keyword(token_val):
			parsed.append(transpile_keyword(token_val))
		elif token_type == 'KEYWORD':
			parsed.append(' ' + token_val + ' ')
		elif token_type in ['STRING', 'DICT_KEY']:
			tmp_indents, tmp_content = separate_indents_and_content(token_val)
			parsed.append(tmp_indents + '\'' + tmp_content + '\'')
		elif token_type in ['VAR', 'NUMBER', 'OPERATOR', 'LIST_START', 'LIST_END', 'PROPERTY']:
			parsed.append(token_val)
		elif token_type in ['DICT_START', 'DICT_END']:
			parsed.append(token_val)

		if token_type == 'LINE':
			parsed.append('\n')

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
	global active_dict
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
		elif char == '{':
			tokens.append(['DICT_START', '{'])
			active_dict = True
		elif char == '}':
			tokens.append(['DICT_END', '}'])
			active_dict = False
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
			elif active_dict and char == ':':
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
						tamp_keyword_length = 0

						if tmp[-2:] in ['in', 'or']:
							tamp_keyword_length = -2
						elif tmp[-3:] in ['and']:
							tamp_keyword_length = -3

						if tamp_keyword_length:
							tokens.append(['VAR', tmp[:tamp_keyword_length]])
							tokens.append(['KEYWORD', tmp[tamp_keyword_length:]])
							is_var = False
							tmp = ''
					elif tmp in keywords and not is_var:
						tokens.append(['KEYWORD', tmp])
						if tmp == 'def':
							is_waiting_for_function_start = True
						tmp = ''
	return tokens


# Global variables set up
active_dict = False
is_waiting_for_function_start = False
parsed = []
return_run = False
is_route = False
function_in_route_name = ''
vars_used_by_route = ''

# Start
is_multi_line_comment = False

is_dev = False

flask_boilerplate = '# -- FLASK BOILERPLATE HERE --\n'

filename = sys.argv[1]

with open(filename) as f:
	source_lines = f.readlines()

tokenized_lines = []

for line in source_lines:
	# Ignores multi-line comments
	if line.replace('\t', '')[:2] == '/*':
		is_multi_line_comment = True
		continue
	elif line.replace('\t', '')[:2] == '*/':
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
	tokens.append(['LINE', '\n'])

if is_dev:
	print('--TOKENS:')
	for token in tokens:
		print(token)

parser(tokens, 0)
parsed.insert(0, flask_boilerplate)
print(''.join(parsed))
