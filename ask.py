import sys
import os


def transpile_var(var):
	vars = {
		'_body': 'request.json'
	}

	try:
		return vars[var]
	except KeyError:
		return var


def route_path_to_func_name(route_str):
	final = ''

	for char in route_str:
		if char not in ['/', '<', '>']:
			final += char
			continue
		final += '_'

	return final


def maybe_place_space_before(parsed, token_val):
	prefix = ' '

	if parsed and parsed[-1] in ['\n', '\t', '(', ' ', '.']:
		prefix = ''
	parsed += prefix + token_val + ' '

	return parsed


def transpile_decorator(decorator):
	decorators = {
		'protected': 'check_for_token',
		'limit': 'limiter.limit',
	}

	try:
		return '\n@' + decorators[decorator]
	except KeyError:
		for key, value in decorators.items():
			if decorator[:len(key)] == key:
				return '\n@' + value + decorator[len(key):]
		return ''


def route_params(route_path):
	is_param = False
	tmp = ''
	params_str = ''

	for char in route_path:
		if char == '<':
			is_param = True
		elif char == '>':
			is_param = False
			params_str += tmp + ', '
			tmp = ''
		elif is_param and char not in [' ' + '\t', '\n']:
			tmp += char

	if len(params_str) > 2 and params_str[-2:] == ', ':
		params_str = params_str[:-2]

	return params_str


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
		'all': 'query.all',
		'get': 'query.get',
		'save': 'db.session.commit',
		'delete': 'db.session.delete',
		'get_by': 'query.filter_by',
		'add': 'db.session.add'
	}

	try:
		if action in needs_commit:
			return [actions[action], True]

		return [actions[action], False]
	except KeyError:
		return ''


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

	is_skip = False
	needs_db_commit = False
	is_decorator = False
	decorator = ''
	add_parenthesese_at_en_of_line = False
	parsed = ''

	for token_index, token in enumerate(tokens):
		if is_skip:
			is_skip = False
			continue

		token_type = token[0]
		token_val = token[1]

		if token_type in ['FORMAT', 'ASSIGN', 'NUM']:
			if token_val == '\n' and add_parenthesese_at_en_of_line:
				parsed += ')'
				add_parenthesese_at_en_of_line = False
			parsed += token_val
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
		elif token_type == 'STR':
			parsed += '"' + token_val + '"'
		elif token_type == 'KEYWORD':
			parsed = maybe_place_space_before(parsed, token_val)
		elif token_type == 'VAR':
			if token_val not in built_in_vars:
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

					parsed += '@app.route(\'' + next_token_val + '\', methods=[\'' + token_val[1:] + '\'])' + suffix

					if is_decorator:
						parsed += decorator + '\n'

					parsed += 'def ' + token_val[1:] + route_path_to_func_name(next_token_val) + '(' + route_params(
						next_token_val)
					is_skip = True
					is_decorator = False
			elif token_val in ['quickSet', 'deep']:
				parsed += 'AskLibrary.' + token_val + '('
			elif token_val == 'respond':
				parsed += 'return jsonify('
			elif token_val == 'status':
				parsed += 'abort(Response('
				add_parenthesese_at_en_of_line = True
			else:
				parsed += token_val + '('
		elif token_type == 'DB_CLASS':
			parsed += '\nclass ' + token_val + '(db.Model)'
		elif token_type == 'FUNC_DEF':
			if token_val == '_init':
				token_val = '__init__'
			parsed += 'def ' + token_val + '('
		elif token_type == 'KEY':
			parsed += '\'' + token_val + '\''
		elif token_type == 'DEC':
			is_decorator = True
			decorator = transpile_decorator(token_val)
		elif token_type == 'DB_ACTION':
			transpiled = transpile_db_action(token_val)
			parsed += transpiled[0]
			if transpiled[1]:
				needs_db_commit = True

		if len(parsed) > 3 and parsed[-1] == ' ' and parsed[-2] == '=' and parsed[-3] == ' ' and parsed[-4] == '=':
			parsed = parsed[:-4]
			parsed += ' == '

	return parsed


def lex_var_keyword(tokens, tmp):
	global variables
	global keywords
	global special_keywords

	collect = False
	collect_ends = []
	include_collect_end = False

	if tmp:
		if tmp in keywords:
			tokens.append(['KEYWORD', tmp])
		elif tmp in special_keywords.keys():
			tokens.append([special_keywords[tmp]['type'], tmp])
			collect = special_keywords[tmp]['collect']
			collect_ends = special_keywords[tmp]['collect_ends']
			include_collect_end = special_keywords[tmp]['include_collect_end']
		else:
			tokens.append(['VAR', tmp])
		tmp = ''
	return tokens, tmp, collect, collect_ends, include_collect_end


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
					tokens.append(['FUNC', tmp])
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
				is_dict.pop(0)
				tokens.append(['OP', char])
			elif char.isdigit():
				tmp = ''
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
				else:
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


def parse_and_prepare(tokens):
	global flask_boilerplate
	global flask_end_boilerplate

	parsed = parser(tokens)
	parsed = flask_boilerplate + '\n' + parsed
	parsed += flask_end_boilerplate

	return parsed


def build(parsed):
	with open('app.py', 'w+') as f:
		f.write('')
		f.write(parsed)


def startup(file_name):
	import time

	global uses_db

	print('\033[1m' + 'Transpiling...' + '\033[0m')

	# Execution time
	start_time = time.time()

	with open(file_name) as f:
		source_lines = f.readlines()

	tokens_list = lexer(source_lines)
	if tokens_list:
		parsed = parse_and_prepare(tokens_list)
		build(parsed)

		# Done!
		end_time = time.time()
		time_result = round(end_time - start_time, 3)
		print('\033[92m' + '\t- Transpiled ' + '\033[0m' + str(len(source_lines)) + ' lines in ~' + '\033[94m' + str(
			time_result) + '\033[0m' + ' seconds')
		if uses_db and not os.path.isfile('db.db'):
			print('\33[1m' + 'Building database...' + '\033[0m', end='')
			from app import db
			db.create_all()
			print(' DONE')
		print('\33[1m' + 'Running Flask app...' + '\033[0m')
		os.system('export FLASK_APP=app.py')
		os.system('flask run')
	else:
		print('\033[91m' + '\t- The file is empty!' + '\033[0m')


# Globals
built_in_vars = ['_body', '_auth', '_env', '_db']
variables = built_in_vars
keywords = ['if', 'else', 'elif', 'in', 'return', 'not', 'or']
special_keywords = {
	'db_class': {
		'type': 'DB_CLASS',
		'collect': True,
		'collect_ends': [':'],
		'include_collect_end': True
	},
	'def': {
		'type': 'FUNC_DEF',
		'collect': True,
		'collect_ends': ['('],
		'include_collect_end': False
	},
}
operators = [':', ')', '!', '+', '-', '*', '/', '%', '.', ',', '[', ']', '&']
uses_db = False

# Setup
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
flask_boilerplate += 'from flask_sqlalchemy import SQLAlchemy\n'

flask_boilerplate += 'app = Flask(__name__)\n'

flask_boilerplate += 'CORS(app)\n'

flask_boilerplate += 'project_dir = os.path.dirname(os.path.abspath(__file__))\n'
flask_boilerplate += 'database_file = "sqlite:///{}".format(os.path.join(project_dir, "db.db"))\n'
flask_boilerplate += 'app.config["SQLALCHEMY_DATABASE_URI"] = database_file\n'
flask_boilerplate += 'app.config[\'SQLALCHEMY_TRACK_MODIFICATIONS\'] = False\n'
flask_boilerplate += 'db = SQLAlchemy(app)\n'

flask_boilerplate += '\n\nclass AskLibrary:\n'
flask_boilerplate += '\t@staticmethod\n'
flask_boilerplate += '\tdef deep(obj, rule):\n'
flask_boilerplate += '\t\trule_key = list(rule.keys())[0]\n'
flask_boilerplate += '\t\trule_val = rule[rule_key]\n'
flask_boilerplate += '\n\t\tfor element in obj:\n'
flask_boilerplate += '\t\t\tif str(element[rule_key]) == str(rule_val):\n'
flask_boilerplate += '\t\t\t\treturn element\n'
flask_boilerplate += '\n\t@staticmethod\n'
flask_boilerplate += '\tdef quickSet(target, source):\n'
flask_boilerplate += '\t\tfor key in source.keys():\n'
flask_boilerplate += '\t\t\tif key in target.keys():\n'
flask_boilerplate += '\t\t\t\ttarget[key] = source[key]\n'
flask_boilerplate += '\n\t\treturn target\n'
flask_boilerplate += '\n\t@staticmethod\n'
flask_boilerplate += '\tdef respond(response):\n'
flask_boilerplate += '\t\treturn jsonify(response)\n'
flask_boilerplate += '\n\t@staticmethod\n'
flask_boilerplate += '\tdef status(message, code):\n'
flask_boilerplate += '\t\treturn Response(message, status=code)\n'
flask_boilerplate += '\n\t@staticmethod\n'
flask_boilerplate += '\tdef halt(message, code):\n'
flask_boilerplate += '\t\tabort(Response(message, code))\n'

flask_boilerplate += "\n\nclass Env:\n"
flask_boilerplate += '\t@staticmethod\n'
flask_boilerplate += "\tdef get(key):\n"
flask_boilerplate += "\t\treturn os.environ.get(key)\n"

flask_boilerplate += "\n\nclass Auth:\n"
flask_boilerplate += "\tdef __init__(self):\n"
flask_boilerplate += "\t\tself.secret_key = ''\n"
flask_boilerplate += "\t\tself.token = jwt.encode({}, self.secret_key)\n"
flask_boilerplate += "\n\tdef login(self, user, expiry):\n"
flask_boilerplate += "\t\tpayload = {\n"
flask_boilerplate += "\t\t	'user': user,\n"
flask_boilerplate += "\t\t	'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expiry)\n"
flask_boilerplate += "\t\t}\n"
flask_boilerplate += "\t\tself.encode(payload)\n"
flask_boilerplate += "\n\tdef encode(self, payload):\n"
flask_boilerplate += "\t\tself.token = jwt.encode(\n"
flask_boilerplate += "\t\t	payload, str(self.secret_key)\n"
flask_boilerplate += "\t\t)\n"
flask_boilerplate += "\n\tdef decode(self):\n"
flask_boilerplate += '\t\treturn jwt.decode(self.token, str(self.secret_key))\n'
flask_boilerplate += "\n\tdef is_valid(self):\n"
flask_boilerplate += "\t\ttry:\n"
flask_boilerplate += "\t\t\t_ = self.decode()\n"
flask_boilerplate += "\t\t\treturn True\n"
flask_boilerplate += "\t\texcept:\n"
flask_boilerplate += "\t\t\treturn False\n"

flask_boilerplate += '\n\nclass Hash:\n'
flask_boilerplate += '\t@staticmethod\n'
flask_boilerplate += '\tdef hash(to_hash):\n'
flask_boilerplate += '\t\treturn hashlib.sha256(to_hash.encode(\'utf-8\')).hexdigest()\n'
flask_boilerplate += '\n\t@staticmethod\n'
flask_boilerplate += '\tdef check(the_hash, not_hashed_to_check):\n'
flask_boilerplate += '\t\treturn Hash.hash(not_hashed_to_check) == the_hash\n'

flask_boilerplate += "\n\n_auth = Auth()\n"
flask_boilerplate += "_env = Env()\n"
flask_boilerplate += "_hash = Hash()\n"

flask_boilerplate += "\n\ndef check_for_token(func):\n"
flask_boilerplate += "\t@wraps(func)\n"
flask_boilerplate += "\tdef wrapped(*args, **kwargs):\n"
flask_boilerplate += "\t\ttoken = request.args.get('token')\n"
flask_boilerplate += "\t\tif not token:\n"
flask_boilerplate += "\t\t\treturn jsonify({'message': 'Missing Token'}), 403\n"
flask_boilerplate += "\t\ttry:\n"
flask_boilerplate += "\t\t\tdata = jwt.decode(token, _auth.secret_key)\n"
flask_boilerplate += "\t\texcept:\n"
flask_boilerplate += "\t\t\treturn jsonify({'message': 'Invalid token'}), 403\n"
flask_boilerplate += "\t\treturn func(*args, **kwargs)\n"
flask_boilerplate += "\treturn wrapped\n\n"

flask_boilerplate += '\nlimiter = Limiter(app, key_func=get_remote_address)\n'

flask_end_boilerplate = '\n\nif __name__ == \'__main__\':\n\tapp.run()\n'

# Start
if __name__ == '__main__':
	print('🌳' + '\033[92m' + 'Ask' + '\033[0m')
	if len(sys.argv) > 1:
		source_file_name = sys.argv[1]
		if os.path.isfile(os.getcwd() + '/' + source_file_name):
			startup(source_file_name)
		else:
			print('\033[91m' + 'The file could not be found!' + '\033[0m')
	else:
		print('\033[91m' + 'Please provide a script file!' + '\033[0m')
