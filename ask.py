import sys
import os
from pprint import pprint


# Prints out text colorized and (optionally) as bold.
def style_print(text, color=None, styles=[], end='\n'):
	prefix = '\033['
	suffix = prefix + '0m'

	available_styles = {
		'bold': '1m'
	}

	colors = {
		'red': '91m',
		'green': '92m',
		'yellow': '93m',
		'blue': '94m',
		'pink': '95m',
	}

	result = str(text)

	if color in colors:
		result = prefix + colors[color] + result + suffix

	for style in styles:
		result = prefix + available_styles[style] + result + suffix

	print(result, end=end)


def get_root_from_file_path(file_path):
	final_path = ''
	adder = False

	for char in file_path[::-1]:
		if adder:
			final_path += char
		elif char == '/':
			adder = True

	if not file_path:
		final_path = file_path

	return final_path[::-1]


def get_ask_config(source_root):
	import json

	if source_root:
		source_root += '/'

	if os.path.isfile(f'{source_root}Askfile'):
		with open(f'{source_root}Askfile', 'r') as f:
			return json.loads(''.join(f.readlines()))

	return {}


def get_db_file_path():
	global ask_config

	if ask_config and 'db' in ask_config and 'path' in ask_config['db']:
		return ask_config['db']['path']

	return 'db.db'


def transpile_var(var):
	vars = {
		'_body': 'request.json',
		'_form': 'request.form',
		'_args': 'request.args',
		'_req': 'AskLibrary.get_all_req()',
		'_datetime': 'datetime.datetime'
	}

	try:
		return vars[var]
	except KeyError:
		return var


def transpile_keyword(keyword):
	keywords = {
		'respond': 'return'
	}

	try:
		return keywords[keyword]
	except KeyError:
		return keyword


def transpile_decorator(decorator):
	global uses_basic_decorator
	global basic_decorator_collector

	decorators = {
		'protected': 'check_for_token',
		'limit': 'limiter.limit',
	}

	if decorator == 'basic':
		uses_basic_decorator = True
		basic_decorator_collector = []

		# "---" is interpreted as an ignored decorator.
		return '---'

	try:
		return f'\n@{decorators[decorator]}'
	except KeyError:
		for key, value in decorators.items():
			if decorator[:len(key)] == key:
				return f'\n@{value}{decorator[len(key):]}'
	return ''


def transpile_db_action(action):
	needs_commit = ['add', 'delete']

	actions = {
		'col': 'db.Column',
		'int': 'db.Integer',
		'pk': 'primary_key=True',
		'unique': 'unique=True',
		'nullable': 'nullable=True',
		'str': 'db.String',
		'float': 'db.Float',
		'bool': 'db.Boolean',
		'bytes': 'db.LargeBinary',
		'datetime': 'db.DateTime',
		'all': 'query.all',
		'get': 'query.get',
		'save': 'db.session.commit',
		'delete': 'db.session.delete',
		'get_by': 'query.filter_by',
		'add': 'db.session.add',
		'exists': 'AskLibrary.exists',
		'desc': 'db.desc',
		'list_id': 'db.Integer',
		'list': 'generic_list_creator',
		'basic_ignore': '_ignored',  # Ignored in the basic _init() boilerplate.
	}

	try:
		if action in needs_commit:
			return [actions[action], True]

		return [actions[action], False]
	except KeyError:
		return ''


def insert_basic_decorator_code_to_insert(parsed, ignored_db_vars):
	global basic_decorator_collector
	global additional_line_count

	parsed_lines_reversed = parsed.split('\n')[::-1]
	tab_count = 0
	line_to_place_code_at = None

	for line_index, line in enumerate(parsed_lines_reversed):
		if 'db.Column(' in line:
			tab_count = len(get_current_tab_level(line))
			line_to_place_code_at = line_index + 1
			break

	code_lines = [f'def __init__(self, {", ".join(basic_decorator_collector)}):']
	for var in basic_decorator_collector:
		code_lines.append(f'\tself.{var} = {var}')
	code_lines.append('')
	code_lines.append('def s(self):')
	code_lines.append('\treturn {')
	for var_index, var in enumerate(ignored_db_vars + basic_decorator_collector):
		code_lines.append(f'\t\t\'{var}\': self.{var},')
	code_lines.append('\t}\n')

	additional_line_count += len('\n'.join(code_lines).split('\n'))

	tab_char = '\t'
	code = f'\n{tab_char * tab_count}'.join([line for line in code_lines])

	return '\n'.join(parsed_lines_reversed[line_to_place_code_at - 1:][::-1]) + f'\n\n{tab_char * tab_count}{code}' + '\n'.join(parsed_lines_reversed[:line_to_place_code_at - 1][::-1])


def is_db_column_in_past_line(tokens):
	for token in tokens[::-1]:
		token_type = token[0]
		token_val = token[1]

		if token_type == 'FORMAT' and token_val == '\n':
			break

		if token_type == 'DB_ACTION' and token_val == 'col' or token_type == 'DB_CLASS':
			return True

	return False


def get_first_variable_token_value_of_line(tokens):
	for token in tokens:
		token_type = token[0]
		if token_type == 'VAR':
			# Returns the token value
			return token[1]

	return None


def route_path_to_func_name(route_str):
	return route_str.replace('/', '_').replace('<', '_').replace('>', '_').replace('-', '_')


def maybe_place_space_before(parsed, token_val):
	prefix = ' '

	if parsed and parsed[-1] in ['\n', '\t', '(', ' ', '.']:
		prefix = ''
	parsed += f'{prefix}{token_val} '

	return parsed


def parse_route_params_str(route_path):
	is_param = False
	tmp = ''
	params_str = ''

	for char in route_path:
		if char == '<':
			tmp = ''
			is_param = True
		elif char == '>':
			is_param = False
			if tmp:
				params_str += f'{tmp}, '
				tmp = ''
		elif is_param and char not in [' ' + '\t', '\n']:
			tmp += char

	if len(params_str) > 2 and params_str[-2:] == ', ':
		params_str = params_str[:-2]

	return params_str


def get_current_tab_level(parsed):
	parsed = parsed[::-1]

	indents = ''

	for char in parsed:
		if char == '\t':
			indents += char
		elif char == '\n':
			break

	return indents


def parser(tokens):
	global built_in_vars
	global ask_library_methods
	global uses_basic_decorator
	global basic_decorator_collector
	global additional_line_count

	is_skip = False
	needs_db_commit = False
	is_decorator = False
	add_tabs_to_inner_group = False
	indention_depth_counter = 0
	decorator = ''
	add_parenthesis_at_en_of_line = False
	basic_decorator_collection_might_end = False
	parsed = ''
	past_lines_tokens = []
	ignored_due_to_basic_decorator = []

	for token_index, token in enumerate(tokens):
		if is_skip:
			is_skip = False
			continue

		token_type = token[0]
		token_val = token[1]

		if uses_basic_decorator and token_type == 'FORMAT' and token_val == '\n' and past_lines_tokens:
			if basic_decorator_collection_might_end:
				if not is_db_column_in_past_line(past_lines_tokens):
					basic_decorator_collection_might_end = False
					uses_basic_decorator = False
					parsed = insert_basic_decorator_code_to_insert(parsed, ignored_due_to_basic_decorator)
			else:
				basic_decorator_collection_might_end = True

		if token_type == 'FORMAT' and token_val == '\n':
			past_lines_tokens = []
		else:
			past_lines_tokens.append(token)

		if add_tabs_to_inner_group and token_type == 'GROUP':
			if token_val == 'end':
				indention_depth_counter -= 1

				if indention_depth_counter == 0:
					add_tabs_to_inner_group = False
					parsed += '\n\treturn wrapper'
					additional_line_count += 1
			elif token_val == 'start':
				indention_depth_counter += 1

		if token_type in ['FORMAT', 'ASSIGN', 'NUM']:
			if token_val == '\n' and add_parenthesis_at_en_of_line:
				parsed += ')'
				add_parenthesis_at_en_of_line = False
			parsed += token_val
			if token_type == 'FORMAT' and token_val == '\n' and add_tabs_to_inner_group:
				parsed += '\t'
		elif token_type == 'OP':
			if token_val in ['.', ')', ',', ':'] and parsed and parsed[-1] == ' ':
				parsed = parsed[:-1]

			parsed += token_val

			if token_val in [',', '=']:
				parsed += ' '

			if needs_db_commit and token_val == ')':
				needs_db_commit = False

				tab_level = get_current_tab_level(parsed)
				parsed += '\n' + tab_level + 'db.session.commit()'
				additional_line_count += 1
		elif token_type == 'STR':
			parsed += f'\"{token_val}\"'
		elif token_type == 'KEYWORD':
			parsed = maybe_place_space_before(parsed, token_val)
		elif token_type == 'VAR':
			if token_val not in built_in_vars and token_index > 0:
				parsed = maybe_place_space_before(parsed, token_val)
			else:
				parsed += transpile_var(token_val)
		elif token_type == 'FUNC':
			if token_val[0] == '@':
				suffix = '\n'

				if token_index > 2 and tokens[token_index - 2][0] == 'DEC':
					suffix = ''

				if token_index < len(tokens) and tokens[token_index + 1][0] == 'STR':
					next_token_val = tokens[token_index + 1][1]

					parsed += f'@app.route(\'{next_token_val}\', methods=[\'{token_val[1:]}\']){suffix}'

					if is_decorator:
						parsed += decorator + '\n'
						additional_line_count += 1

					parsed += f'def {token_val[1:]}{route_path_to_func_name(next_token_val)}({parse_route_params_str(next_token_val)}'
					is_skip = True
					is_decorator = False
			elif token_val in ask_library_methods:
				prefix = 'AskLibrary.'

				if token_val in ['respond']:
					prefix = f'return {prefix}'

				parsed += f'{prefix}{token_val}('
			elif token_val == 'respond':
				parsed += 'return jsonify('
			elif token_val == 'status':
				parsed += 'abort(Response('
				add_parenthesis_at_en_of_line = True
			elif token_val == '_inner':
				parsed += 'func(*args, **kwargs'
			else:
				parsed += f'{token_val}('
		elif token_type == 'DB_CLASS':
			parsed += f'\nclass {token_val}(db.Model)'
			additional_line_count += 1
		elif token_type == 'FUNC_DEF':
			if token_val == '_init':
				token_val = '__init__'
			parsed += f'def {token_val}('
		elif token_type == 'DEC_DEF':
			parsed += f'def {token_val}(func):'
			parsed += f'\n\tdef wrapper(*args, **kwargs):'
			add_tabs_to_inner_group = True
		elif token_type == 'KEY':
			parsed += f'\'{token_val}\''
		elif token_type == 'DEC':
			decorator = transpile_decorator(token_val)
			if not decorator:
				parsed += f'@{token_val}'

			if decorator != '---':
				is_decorator = True
		elif token_type == 'DB_ACTION':
			transpiled = transpile_db_action(token_val)

			if uses_basic_decorator:
				if transpiled[0] in ['primary_key=True', '_ignored']:
					ignored_due_to_basic_decorator.append(get_first_variable_token_value_of_line(past_lines_tokens))

				if transpiled[0] == 'db.Column':
					var = get_first_variable_token_value_of_line(past_lines_tokens)
					basic_decorator_collector.append(var)

					for ignored in ignored_due_to_basic_decorator:
						if ignored in basic_decorator_collector:
							basic_decorator_collector.remove(ignored)

			if transpiled[0] != '_ignored':
				parsed += transpiled[0]
			if transpiled[1]:
				needs_db_commit = True

		if len(parsed) > 3 and parsed[-1] == ' ' and parsed[-2] == '=' and parsed[-3] == ' ' and parsed[-4] == '=':
			parsed = parsed[:-4]
			parsed += ' == '

	return parsed


# Figures out if a given name should be lexed as a keyword or variable token.
def lex_var_keyword(tokens, tmp):
	global keywords
	global special_keywords

	collect = False
	collect_ends = []
	include_collect_end = False

	if tmp:
		if tmp in keywords:
			tokens.append(['KEYWORD', transpile_keyword(tmp)])
		elif tmp in special_keywords.keys():
			tokens.append([special_keywords[tmp]['type'], tmp])
			collect = special_keywords[tmp]['collect']
			collect_ends = special_keywords[tmp]['collect_ends']
			include_collect_end = special_keywords[tmp]['include_collect_end']
		else:
			tokens.append(['VAR', tmp])
		tmp = ''
	return tokens, tmp, collect, collect_ends, include_collect_end


def add_part(parts, is_string, code):
	parts.append({
		'is_string': is_string,
		'code': code
	})

	is_string = True

	if code[-1] == '\n':
		is_string = False

	return parts, '', is_string


# Remove spaces between function names and '('.
# Replaces four & two spaces with tab.
def fix_up_code_line(statement):
	statement = statement.replace("'", '"')

	parts = []
	is_string = False
	tmp = ''

	for char in statement:
		tmp += char

		if char == '"' and is_string:
			parts, tmp, is_string = add_part(parts, True, tmp)
			is_string = False
		elif char in ['"', '\n']:
			parts, tmp, is_string = add_part(parts, False, tmp)

	statement = ''
	for part in parts:
		if not part['is_string']:
			part['code'] = part['code'].replace('    ', '\t').replace('  ', '\t').replace(' (', '(')
		statement += part['code']

	return statement


def lexer(raw):
	tmp = ''
	is_collector = False
	collector_ends = []
	include_collector_end = False
	is_dict = []

	global keywords
	global operators
	global variables

	global uses_db

	tokens = []

	for line in raw:
		line = fix_up_code_line(line)
		for char_index, char in enumerate(line):
			if char == '#':
				tokens.append(['FORMAT', '\n'])
				break

			if is_collector:
				if char not in collector_ends:
					tmp += char
				else:
					tokens[-1][1] = tmp

					if include_collector_end:
						tokens.append(['OP', char])

					is_collector = False
					include_collector_end = False
					tmp = ''

			elif char == '(':
				if tmp:
					tokens.append(['FUNC', tmp.replace(' ', '')])
					tmp = ''
			elif char == '=':
				if tmp:
					tokens.append(['VAR', tmp])
					tokens.append(['ASSIGN', char])

					if tmp not in variables:
						variables.append(tmp)

					tmp = ''
				else:
					tokens.append(['OP', char])
			elif char in ['"', '\'']:
				is_collector = True
				collector_ends = ['"', '\'']
				include_collector_end = False
				tmp = ''
				tokens.append(['STR', ''])
			elif char == '{':
				is_dict.append(True)
				tokens.append(['OP', char])
			elif char == '}':
				tokens, tmp, is_collector, collector_ends, include_collector_end = lex_var_keyword(tokens, tmp)

				is_dict.pop(0)
				tokens.append(['OP', char])
			elif char.isdigit() and not tmp:
				if tokens and tokens[-1][0] == 'NUM':
					tokens[-1][1] += char
					continue
				tokens.append(['NUM', char])
			elif char == '&':
				is_collector = True
				collector_ends = ['\n']
				include_collector_end = True
				tmp = ''
				tokens.append(['DEC', ''])
			elif char in operators:
				if char == ':' and is_dict and tmp:
					tokens.append(['KEY', tmp])
					tmp = ''

				tokens, tmp, is_collector, collector_ends, include_collector_end = lex_var_keyword(tokens, tmp)
				tokens.append(['OP', char])
			elif char not in ['\n', '\t', ' ']:
				tmp += char
			elif char in ['\n', '\t']:
				tokens, tmp, is_collector, collector_ends, include_collector_end = lex_var_keyword(tokens, tmp)
				tokens.append(['FORMAT', char])
			else:
				tokens, tmp, is_collector, collector_ends, include_collector_end = lex_var_keyword(tokens, tmp)

			if len(tokens) > 2 and tokens[-2][0] == 'VAR' and tokens[-2][1] == '_db':
				# Removes both the VAR: _db and the OP: .
				tokens.pop(-1)
				tokens.pop(-1)
				is_collector = True
				collector_ends = ['(', ',', ')']
				include_collector_end = True
				tmp = ''
				tokens.append(['DB_ACTION', ''])
				uses_db = True
	return tokens


def tokens_grouped_by_lines(tokens):
	tmp = []
	lines = []

	for token_index, token in enumerate(tokens):
		token_type = token[0]
		token_val = token[1]

		if token_type == 'OP' and token_val in ['\n', '\t']:
			token_type = 'FORMAT'

		if token_type == 'FORMAT' and token_val == '\n':
			lines.append(tmp)
			tmp = []

		tmp.append([token_type, token_val])

	if tmp:
		lines.append(tmp)

	return lines


def insert_indention_group_markers(tokens):
	lines = tokens_grouped_by_lines(tokens)

	marked = []
	previous_line_tabs = 0
	current_line_tabs = 0
	group_start_counter = 0

	for line in lines:
		previous_line_tabs = current_line_tabs
		current_line_tabs = 0

		# Counts the number of indents at the start of the line.
		for token_index, token in enumerate(line):
			token_type = token[0]
			token_val = token[1]

			# The line has "started", meaning no more leading tabs.
			if token_type != 'FORMAT':
				break

			# Is FORMAT, meaning \n or \t
			if token_val == '\t':
				current_line_tabs += 1

		# Insert group start/end markings
		if current_line_tabs < previous_line_tabs:
			marked.append(['GROUP', 'end'])
			group_start_counter -= 1
		elif current_line_tabs > previous_line_tabs:
			marked.append(['GROUP', 'start'])
			group_start_counter += 1

		# Inserts the rest of the lines token after the marking(s)
		for token in line:
			marked.append(token)

	# Inserts a leading marker
	marked.insert(0, ['GROUP', 'start'])
	group_start_counter += 1

	# Inserts missing group end markings:
	for _ in range(group_start_counter):
		marked.append(['GROUP', 'end'])

	return marked


# Parses tokens and adds the end boilerplate to the output code.
def parse_and_prepare(tokens):
	global flask_boilerplate
	global flask_end_boilerplate

	parsed = parser(tokens)
	parsed = f'{flask_boilerplate}\n{parsed}'
	parsed += flask_end_boilerplate

	return parsed


def build(parsed):
	# Saves the transpiled code to the build/output file
	with open('app.py', 'w+') as f:
		f.write('')
		f.write(parsed)


def parse_and_print_error(err):
	import difflib

	global additional_line_count
	global source_file_name

	message = err['msg'].capitalize()
	transpiled_line_nr = err['line']
	code = err['code'].replace('\t', '')

	line_nr = None

	with open(source_file_name, 'r') as f:
		raw_lines = f.readlines()

	matches = list(difflib.get_close_matches(code, raw_lines))
	for line_index, line in enumerate(raw_lines):
		if line == str(matches[0]):
			line_nr = line_index
			break

	if is_dev:
		# Prints out the "real" line number.
		print(f'\t- DEV: {message} on line: {transpiled_line_nr} in: app.py')

	style_print('\t- Error!', color='red', end=' ')
	style_print(message, styles=['bold'], end=' ')
	print('on line', end=' ')
	style_print(line_nr, color='blue', end='')
	print(', in/at: ', end='')
	style_print(code, styles=['bold'])


def print_transpilation_result(source_lines, time_result, for_error=False):
	color = 'green' if not for_error else 'red'

	style_print('\t- Transpiled ', color, end='')
	print(f'{len(source_lines)} lines in ~', end='')
	style_print(time_result, color='blue', end='')
	print(' seconds.')


def startup(file_name):
	import time

	global uses_db
	global is_dev

	style_print('Transpiling...', styles=['bold'], end='')

	# Execution time capture start.
	start_time = time.time()

	# Lexing.
	with open(file_name) as f:
		source_lines = f.readlines()
	tokens_list = lexer(source_lines)
	tokens_list = insert_indention_group_markers(tokens_list)

	if is_dev:
		print('\n')
		pprint(tokens_list)
		os.environ['FLASK_ENV'] = 'development'

	if tokens_list:
		# Parsing.
		parsed = parse_and_prepare(tokens_list)
		build(parsed)

		# Transpilation done.
		end_time = time.time()
		time_result = round(end_time - start_time, 3)

		# Mark for the 'Transpiling...' message at the start of this function.
		print('\t✅')

		# Prints out result and builds the database.
		print_transpilation_result(source_lines, time_result)

		if uses_db and not os.path.exists(get_db_file_path()):
			style_print('Building database...', styles=['bold'], end='')
			db_root = get_root_from_file_path(get_db_file_path())
			print('\t✅')

			if db_root and db_root != file_name and not os.path.exists(db_root):
				print('\t- Building Folder Structure...', end='')
				os.makedirs(db_root)
				print('\t✅')

		# Runs the transpiled code.	
		try:
			# Imports app.py for two reasons:
			# 1. To catch syntax errors.
			# 2. To load the database (if it's used).
			from importlib.machinery import SourceFileLoader
			app = SourceFileLoader("app", f'{os.getcwd()}/app.py').load_module()

			if uses_db:
				style_print('Loading database...', styles=['bold'], end='')
				app.db.create_all()
				print('\t✅')

			# TODO: ALso support running the app in a production ready server.
			style_print('Running Flask app:', styles=['bold'])
			os.environ['FLASK_APP'] = 'app.py'
			os.system('flask run')
		except Exception as e:
			# Catches e.g. syntax errors.
			msg, data = e.args
			_, line, _, code = data

			# Prints out the error
			os.system('clear' if os.name != 'nt' else 'cls')

			print('🌳', end='')
			style_print('Ask', color='green')
			style_print('Transpiling...', styles=['bold'], end='')
			print('\t❌ ')
			print_transpilation_result(source_lines, time_result, True)

			parse_and_print_error({
				'msg': msg,
				'line': line,
				'code': code
			})
	else:
		style_print('\t- The file is empty!', color='red')


def set_boilerplate():
	global flask_boilerplate
	global flask_end_boilerplate
	global additional_line_count

	# Imports & initial setup
	flask_boilerplate = ''
	flask_boilerplate += 'from flask import Flask, jsonify, abort, request, Response\n'
	flask_boilerplate += 'from flask_limiter import Limiter\n'
	flask_boilerplate += 'from flask_limiter.util import get_remote_address\n'
	flask_boilerplate += 'from flask_cors import CORS\n'
	flask_boilerplate += 'from functools import wraps\n'
	flask_boilerplate += 'import jwt\n'
	flask_boilerplate += 'import datetime\n'
	flask_boilerplate += 'import os\n'
	flask_boilerplate += 'import hashlib\n'
	flask_boilerplate += 'import random\n'
	flask_boilerplate += 'import pickle\n'
	flask_boilerplate += 'from flask_sqlalchemy import SQLAlchemy\n'

	flask_boilerplate += 'app = Flask(__name__)\n'
	flask_boilerplate += 'CORS(app)\n'

	# Database connection
	flask_boilerplate += 'project_dir = os.path.dirname(os.path.abspath(__file__))\n'
	flask_boilerplate += 'database_file = "sqlite:///{}".format(os.path.join(project_dir, "' + get_db_file_path() + '"))\n'
	flask_boilerplate += 'app.config["SQLALCHEMY_DATABASE_URI"] = database_file\n'
	flask_boilerplate += 'app.config[\'SQLALCHEMY_TRACK_MODIFICATIONS\'] = False\n'
	flask_boilerplate += 'db = SQLAlchemy(app)\n'

	# Generic database list {table(s)}.
	# Generic list table
	flask_boilerplate += '\n\nclass GenericList(db.Model):\n'
	flask_boilerplate += '\tid = db.Column(db.Integer, primary_key=True)\n'

	flask_boilerplate += '\n\tdef set_list(self, entry):\n'
	flask_boilerplate += '\t\tif entry:\n'
	flask_boilerplate += '\t\t\tfor item in entry:\n'
	flask_boilerplate += '\t\t\t\tself.push(item)\n'

	flask_boilerplate += '\n\tdef s(self):\n'
	flask_boilerplate += '\t\treturn {\n'
	flask_boilerplate += '\t\t\t\'id\': self.id,\n'
	flask_boilerplate += '\t\t\t\'list\': self.list()\n'
	flask_boilerplate += '\t\t}\n'

	flask_boilerplate += '\n\tdef list(self):\n'
	flask_boilerplate += '\t\treturn [self.get(item.index) for item in GenericListItem.query.filter_by(parent_id=self.id)]\n'

	flask_boilerplate += '\n\tdef push(self, item):\n'
	flask_boilerplate += '\t\tnew_item = GenericListItem(item, self.id)\n'
	flask_boilerplate += '\t\tdb.session.add(new_item)\n'
	flask_boilerplate += '\t\tdb.session.commit()\n'
	flask_boilerplate += '\n\t\treturn self.s()\n'

	flask_boilerplate += '\n\tdef get(self, index):\n'
	flask_boilerplate += '\t\titem = GenericListItem.query.filter_by(parent_id=self.id, index=index).first()\n'
	flask_boilerplate += '\n\t\treturn item.in_type()\n'

	flask_boilerplate += '\n\tdef remove(self, index):\n'
	flask_boilerplate += '\t\titem = GenericListItem.query.filter_by(parent_id=self.id, index=index).first()\n'
	flask_boilerplate += '\t\tdb.session.delete(item)\n'
	flask_boilerplate += '\t\tdb.session.commit()\n'

	# Generic list item table
	flask_boilerplate += '\n\nclass GenericListItem(db.Model):\n'
	flask_boilerplate += '\tid = db.Column(db.Integer, primary_key=True)\n'
	flask_boilerplate += '\tindex = db.Column(db.Integer)\n'
	flask_boilerplate += '\titem = db.Column(db.LargeBinary)\n'
	flask_boilerplate += '\tparent_id = db.Column(db.Integer)\n'

	flask_boilerplate += '\n\tdef __init__(self, item, parent_id):\n'
	flask_boilerplate += '\t\tself.item = pickle.dumps(item)\n'
	flask_boilerplate += '\t\tself.parent_id = parent_id\n'
	flask_boilerplate += '\t\tself.index = self.get_last_index() + 1\n'

	flask_boilerplate += '\n\tdef s(self):\n'
	flask_boilerplate += '\t\treturn {\n'
	flask_boilerplate += '\t\t\t\'id\': self.id,\n'
	flask_boilerplate += '\t\t\t\'index\': self.index,\n'
	flask_boilerplate += '\t\t\t\'item\': self.in_type(),\n'
	flask_boilerplate += '\t\t\t\'parent_id\': self.parent_id\n'
	flask_boilerplate += '\t\t}\n'

	flask_boilerplate += '\n\tdef get_last_index(self):\n'
	flask_boilerplate += '\t\tlast_item = GenericListItem.query.filter_by(parent_id=self.parent_id).order_by(db.desc(GenericListItem.id)).first()\n'

	flask_boilerplate += '\n\t\tif AskLibrary.exists(last_item):\n'
	flask_boilerplate += '\t\t\treturn last_item.index\n'
	flask_boilerplate += '\n\t\treturn -1\n'

	flask_boilerplate += '\n\tdef in_type(self):\n'
	flask_boilerplate += '\t\treturn pickle.loads(self.item)\n'

	# GenericList creation function
	flask_boilerplate += '\n\ndef generic_list_creator(entry=[]):\n'
	flask_boilerplate += '\tgeneric_list = GenericList()\n'
	flask_boilerplate += '\tdb.session.add(generic_list)\n'
	flask_boilerplate += '\tdb.session.commit()\n'
	flask_boilerplate += '\n\tif entry:\n'
	flask_boilerplate += '\t\tgeneric_list.set_list(entry)\n'
	flask_boilerplate += '\n\treturn generic_list\n'

	# Ask's built-in functions
	flask_boilerplate += '\n\nclass AskLibrary:\n'

	flask_boilerplate += '\t@staticmethod\n'
	flask_boilerplate += '\tdef deep(obj, rule):\n'
	flask_boilerplate += '\t\trule_key = list(rule.keys())[0]\n'
	flask_boilerplate += '\t\trule_val = rule[rule_key]\n'
	flask_boilerplate += '\n\t\tfor element in obj:\n'
	flask_boilerplate += '\t\t\tif str(element[rule_key]) == str(rule_val):\n'
	flask_boilerplate += '\t\t\t\treturn element\n'

	flask_boilerplate += '\n\t@staticmethod\n'
	flask_boilerplate += '\tdef quick_set(target, source):\n'
	flask_boilerplate += '\t\tfor key in source.keys():\n'
	flask_boilerplate += '\t\t\tif key in target.keys():\n'
	flask_boilerplate += '\t\t\t\ttarget[key] = source[key]\n'
	flask_boilerplate += '\n\t\treturn target\n'

	flask_boilerplate += '\n\t# Deprecated method\n'
	flask_boilerplate += '\tdef quickSet(self, target, source):\n'
	flask_boilerplate += '\t\treturn self.quick_set(target, source)\n'

	flask_boilerplate += '\n\t@staticmethod\n'
	flask_boilerplate += '\tdef status(message, code):\n'
	flask_boilerplate += '\t\treturn Response(message, status=code)\n'

	flask_boilerplate += '\n\t@staticmethod\n'
	flask_boilerplate += '\tdef respond(response):\n'
	flask_boilerplate += '\t\treturn jsonify(response)\n'

	flask_boilerplate += '\n\t@staticmethod\n'
	flask_boilerplate += '\tdef get_all_req():\n'
	flask_boilerplate += '\t\treq = {}\n'
	flask_boilerplate += '\t\tif request.json:\n'
	flask_boilerplate += '\t\t\tfor thing in request.json.keys():\n'
	flask_boilerplate += '\t\t\t\treq[thing] = request.json[thing]\n\n'
	flask_boilerplate += '\t\tif request.form:\n'
	flask_boilerplate += '\t\t\tfor thing in request.form.keys():\n'
	flask_boilerplate += '\t\t\t\treq[thing] = request.form[thing]\n\n'
	flask_boilerplate += '\t\tif request.args:\n'
	flask_boilerplate += '\t\t\tfor thing in request.args.keys():\n'
	flask_boilerplate += '\t\t\t\treq[thing] = request.args[thing]\n\n'
	flask_boilerplate += '\t\treturn req\n'

	flask_boilerplate += '\n\t@staticmethod\n'
	flask_boilerplate += '\tdef serialize(db_data):\n'
	flask_boilerplate += '\t\treturn [data.s() for data in db_data]\n'

	flask_boilerplate += '\n\t@staticmethod\n'
	flask_boilerplate += '\tdef exists(query):\n'
	flask_boilerplate += '\t\tif query is not None:\n'
	flask_boilerplate += '\t\t\tresult = False\n'
	flask_boilerplate += '\t\t\ttry:\n'
	flask_boilerplate += '\t\t\t\tresult = bool(query.scalar())\n'
	flask_boilerplate += '\t\t\texcept Exception:\n'
	flask_boilerplate += '\t\t\t\tresult = bool(query)\n'
	flask_boilerplate += '\t\t\treturn result\n'
	flask_boilerplate += '\t\treturn False\n'

	# Env, Environment variables, etc.
	flask_boilerplate += "\n\nclass Env:\n"

	flask_boilerplate += '\t@staticmethod\n'
	flask_boilerplate += "\tdef get(key):\n"
	flask_boilerplate += "\t\treturn os.environ.get(key)\n"

	# Auth, the JWT authentication system.
	flask_boilerplate += "\n\nclass Auth:\n"

	flask_boilerplate += "\tdef __init__(self):\n"
	flask_boilerplate += "\t\timport uuid\n"
	flask_boilerplate += "\n\t\tself.secret_key = uuid.uuid4().hex\n"
	flask_boilerplate += "\t\tself.token = jwt.encode({}, self.secret_key)\n"

	flask_boilerplate += "\n\tdef set_token(self, req_token):\n"
	flask_boilerplate += "\t\tself.token = req_token\n"

	flask_boilerplate += "\n\tdef login(self, user, expiry):\n"
	flask_boilerplate += "\t\tpayload = {\n"
	flask_boilerplate += "\t\t	'user': user,\n"
	flask_boilerplate += "\t\t	'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expiry)\n"
	flask_boilerplate += "\t\t}\n"
	flask_boilerplate += "\t\tself.encode(payload)\n"

	flask_boilerplate += "\n\tdef encode(self, payload):\n"
	flask_boilerplate += "\t\tself.token = jwt.encode(payload, str(self.secret_key))\n"

	flask_boilerplate += "\n\tdef decode(self):\n"
	flask_boilerplate += '\t\treturn jwt.decode(self.token, str(self.secret_key))\n'

	flask_boilerplate += "\n\tdef user(self):\n"
	flask_boilerplate += '\t\treturn self.decode()[\'user\']\n'

	flask_boilerplate += "\n\tdef get_token(self):\n"
	flask_boilerplate += '\t\treturn self.token.decode(\'utf-8\')\n'

	flask_boilerplate += "\n\tdef is_valid(self):\n"
	flask_boilerplate += "\t\ttry:\n"
	flask_boilerplate += "\t\t\t_ = self.decode()\n"
	flask_boilerplate += "\t\t\treturn True\n"
	flask_boilerplate += "\t\texcept:\n"
	flask_boilerplate += "\t\t\treturn False\n"

	# Hash, sha256 hashing.
	flask_boilerplate += '\n\nclass Hash:\n'

	flask_boilerplate += '\t@staticmethod\n'
	flask_boilerplate += '\tdef hash(to_hash):\n'
	flask_boilerplate += '\t\treturn hashlib.sha256(to_hash.encode(\'utf-8\')).hexdigest()\n'

	flask_boilerplate += '\n\t@staticmethod\n'
	flask_boilerplate += '\tdef check(the_hash, not_hashed_to_check):\n'
	flask_boilerplate += '\t\treturn Hash.hash(not_hashed_to_check) == the_hash\n'

	# Random, random number & choice generators.
	flask_boilerplate += '\n\nclass Random:\n'

	flask_boilerplate += '\t@staticmethod\n'
	flask_boilerplate += '\tdef int(start, end, count=1):\n'
	flask_boilerplate += '\t\tif end - start < count:\n'
	flask_boilerplate += '\t\t\traise ValueError("Integer count greater than the input range!")\n'
	flask_boilerplate += '\t\tif count > 1:\n'
	flask_boilerplate += '\t\t\treturn random.sample(range(start, end), count)\n'
	flask_boilerplate += '\n\t\treturn random.randint(start, end)\n'

	flask_boilerplate += '\n\t@staticmethod\n'
	flask_boilerplate += '\tdef __random_float(start, end, decimals):\n'
	flask_boilerplate += '\t\treturn round(random.uniform(start, end), decimals)\n'

	flask_boilerplate += '\n\tdef float(self, start, end, count=1, decimals=16, unique=False):\n'
	flask_boilerplate += '\t\tif count <= 1:\n'
	flask_boilerplate += '\t\t\treturn self.__random_float(start, end, decimals)\n'
	flask_boilerplate += '\n\t\tfloats = []\n'
	flask_boilerplate += '\t\tfor _ in range(1, count + 1):\n'
	flask_boilerplate += '\t\t\tn = self.__random_float(start, end, decimals)\n'
	flask_boilerplate += '\t\t\tif unique:\n'
	flask_boilerplate += '\t\t\t\twhile n in floats:\n'
	flask_boilerplate += '\t\t\t\t\tn = self.__random_float(start, end, decimals)\n'
	flask_boilerplate += '\t\t\tfloats.append(n)\n'
	flask_boilerplate += '\n\t\treturn floats\n'

	flask_boilerplate += '\n\t@staticmethod\n'
	flask_boilerplate += '\tdef element(iterable, count=1, weights=None, unique=False):\n'
	flask_boilerplate += '\t\tif unique:\n'
	flask_boilerplate += '\t\t\treturn random.sample(iterable, k=count)\n'
	flask_boilerplate += '\n\t\treturn random.choices(iterable, weights=weights, k=count)\n'

	# Setting up global instances of the library classes.
	flask_boilerplate += "\n\n_auth = Auth()\n"
	flask_boilerplate += "_env = Env()\n"
	flask_boilerplate += "_hash = Hash()\n"
	flask_boilerplate += "_random = Random()\n"

	# Decorator function for checking & validating the passed in token for protected routes.
	flask_boilerplate += "\n\ndef check_for_token(func):\n"
	flask_boilerplate += "\t@wraps(func)\n"
	flask_boilerplate += "\tdef wrapped(*args, **kwargs):\n"
	flask_boilerplate += "\t\ttoken = request.args.get('token')\n"
	flask_boilerplate += "\t\t_auth.set_token(token)\n"
	flask_boilerplate += "\t\tif not token:\n"
	flask_boilerplate += "\t\t\treturn jsonify({'message': 'Missing token!'}), 400\n"
	flask_boilerplate += "\t\ttry:\n"
	flask_boilerplate += "\t\t\tdata = jwt.decode(token, _auth.secret_key)\n"
	flask_boilerplate += "\t\texcept:\n"
	flask_boilerplate += "\t\t\treturn jsonify({'message': 'Invalid token!'}), 401\n"
	flask_boilerplate += "\t\treturn func(*args, **kwargs)\n"
	flask_boilerplate += "\treturn wrapped\n"

	# Flask limiter setup.
	flask_boilerplate += '\n\nlimiter = Limiter(app, key_func=get_remote_address)'

	# Boilerplate code a the end of the output file (app.py).
	flask_end_boilerplate = '\n\nif __name__ == \'__main__\':\n\tapp.run()\n'

	additional_line_count += len(flask_boilerplate.split('\n'))


# Global variables
built_in_vars = ['_body', '_form', '_args', '_req', '_auth', '_env', '_db', '_datetime']
variables = built_in_vars
keywords = ['if', 'else', 'elif', 'in', 'return', 'not', 'or', 'respond']

# "Special" keywords = keywords that require some sort of data after the keyword it self.
# e.g. Classes have a class name.
db_class = {
	'type': 'DB_CLASS',
	'collect': True,
	'collect_ends': [':'],
	'include_collect_end': True
}
special_keywords = {
	'db_class': db_class,
	'db_model': db_class,
	'def': {
		'type': 'FUNC_DEF',
		'collect': True,
		'collect_ends': ['('],
		'include_collect_end': False
	},
	'decorator': {
		'type': 'DEC_DEF',
		'collect': True,
		'collect_ends': [':'],
		'include_collect_end': False
	}
}
operators = [':', ')', '!', '+', '-', '*', '/', '%', '.', ',', '[', ']', '&']
ask_library_methods = ['quick_set', 'quickSet', 'deep', 'serialize', 'respond']
uses_db = False
ask_config = {}
flask_boilerplate = ''
flask_end_boilerplate = ''
uses_basic_decorator = False
basic_decorator_collector = []
# Used in error messages
additional_line_count = 0

is_dev = False

# Entrypoint
if __name__ == '__main__':
	print('🌳', end='')
	style_print('Ask', color='green')

	# DEV mode activation, (-d) flag.
	if len(sys.argv) > 1:
		if len(sys.argv) > 2:
			flag = sys.argv[2]
			if flag == '-d':
				is_dev = True

		source_file_name = sys.argv[1]
		if os.path.isfile(f'{os.getcwd()}/{source_file_name}'):
			ask_config = get_ask_config(get_root_from_file_path(source_file_name))
			set_boilerplate()
			startup(source_file_name)
		else:
			style_print('- The file could not be found!', color='red')
	else:
		style_print('- Please provide a script file!', color='red')
