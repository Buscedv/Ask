# coding=utf-8

# Ask 1.0
# Copyright 2020 Edvard Busck-Nielsen
# This file is part of Ask.
#
#     Ask is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     Ask is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with Ask.  If not, see <https://www.gnu.org/licenses/>.

import sys
import os
import time


class AskLibrary:
	# Selecting an object from a list of objects, by value.
	@staticmethod
	def deep(obj, rule):
		rule_key = rule.keys()[0]
		rule_val = rule[rule_key]

		for element in obj:
			if str(element[rule_key]) == str(rule_val):
				return element

	@staticmethod
	def quickPut(target, source):
		for key in source.keys():
			if key in target.keys():
				target[key] = source[key]

		return target

	@staticmethod
	def status(code):
		from flask import jsonify

		return jsonify({
			'status': code
		})


def transpile_db_action(action):
	actions = {
		'col': 'db.Column',
		'int': 'db.Integer',
		'pk': 'primary_key=True',
		'unique': 'unique=True',
		'str': 'db.String',
		'float': 'db.Float',
		'all': '.query.all',
		'get': '.query.get',
	}

	indents, only_action = separate_indents_and_content(action)

	if only_action in actions.keys():
		return actions[only_action]

	return False


def transpile_special_keyword(keyword):
	keywords = {
		'db_class': 'class ',
		'class': 'class ',
		'def': 'def ',
	}

	indents, only_keyword = separate_indents_and_content(keyword)

	if only_keyword in keywords.keys():
		return keywords[only_keyword]

	return False


def transpile_var(var):
	var_names = {
		'_body': 'request.json',
	}

	indents, var_name = separate_indents_and_content(var)

	if var_name in var_names.keys():
		return indents + var_names[var_name]

	return False


def transpile_function(function):
	functions = {
		'respond': 'return jsonify',
		'deep': 'AskLibrary.deep',
		'quickPut': 'AskLibrary.quickPut',
		'status': 'AskLibrary.status'
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
				parsed.append('@app.route(\'' + route_url_parser(parser(tokens, current_token + 1)) + '\', methods=[\'' + token_val.replace('\t', '')[1:].upper() + '\'])')

				# Prep. for function in route (used by flask)
				return_run = True
				function_in_route_name = parser(tokens, current_token + 1).replace('/', '_').replace('$', '').replace('.', '_')
				function_in_route_name += '_' + token_val.replace('\t', '')[1:]

				return_run = True
				vars_used_by_route = get_vars_used_by_route(route_url_parser(parser(tokens, current_token + 1)))

				parsed.append('\ndef ' + function_in_route_name + '(' + vars_used_by_route)

				current_token += 1
			elif token_val.replace('\t', '') == '_init':
				parsed[-1] = '\t' + parsed[-1]
				parsed.append('__init__(')
			elif transpile_function(token_val):
				parsed.append(transpile_function(token_val) + '(')
			else:
				parsed.append(token_val + '(')
		elif token_type == 'KEYWORD':
			if not transpile_special_keyword(token_val):
				parsed.append(' ' + token_val + ' ')
			else:
				parsed.append(transpile_special_keyword(token_val))
		elif token_type in ['STRING', 'DICT_KEY']:
			tmp_token_val_indents, tmp_token_val = separate_indents_and_content(token_val)
			parsed.append(tmp_token_val_indents + '\'' + tmp_token_val + '\'')
		elif token_type in ['NUMBER', 'OPERATOR', 'PROPERTY', 'DICT_START', 'DICT_END', 'LIST_START', 'LIST_END']:
			parsed.append(token_val)
		elif token_type == 'CLASS_REFERENCE':
			parsed.append(token_val.replace('\t', ''))
		elif token_type == 'VAR':
			if token_val.replace('\t', '') in ['_body']:
				parsed.append(transpile_var(token_val))
			else:
				parsed.append(token_val)
		elif token_type == 'DB_CLASS':
			return_run = True
			parsed.append('class ' + parser(tokens, current_token + 1) + '(db.Model)')
		elif token_type == 'DB_ACTION':
			if transpile_db_action(token_val):
				parsed.append(transpile_db_action(token_val))
			elif token_val.replace('\t', '') in ['add', 'delete']:
				next_up_collected = ''
				not_end_yet = True

				tmp_current_token = current_token + 1

				while not_end_yet:
					tmp_token = tokens[tmp_current_token]
					if tmp_token[1] != ')':
						next_up_collected += tmp_token[1]
					else:
						not_end_yet = False

					if len(tokens) - 1 > tmp_current_token:
						tmp_current_token += 1
					else:
						break

				current_token = tmp_current_token

				tmp_indents, tmp_token_val = separate_indents_and_content(token_val)

				parsed.append(tmp_indents + 'db.session.' + tmp_token_val + next_up_collected + ')\n' + tmp_indents + 'db.session.commit()\n')
			elif token_val == 'init':
				global flask_boilerplate

				flask_app_init = 'app = Flask(__name__)\n'

				flask_boilerplate = flask_boilerplate.replace(flask_app_init, '')
				flask_boilerplate += 'from flask_sqlalchemy import SQLAlchemy\n'
				flask_boilerplate += 'import os\n'
				flask_boilerplate += flask_app_init
				flask_boilerplate += 'basedir = os.path.abspath(os.path.dirname(__file__))\n'
				flask_boilerplate += 'app.config[\'SQLALCHEMY_DATABASE_URI\'] = \'sqlite:///\' + os.path.join(basedir, \'db.sqlite\')\n'
				flask_boilerplate += 'app.config[\'SQLALCHEMY_TRACK_MODIFICATIONS\'] = False\n'
				flask_boilerplate += 'db = SQLAlchemy(app)\n'

				tokens.pop(current_token + 1)
				tokens.pop(current_token + 1)

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
	is_class = False
	is_db_action = False
	global active_dict
	global is_waiting_for_function_start
	global db_action_indents

	operators = ['+', '-', '*', '/', '%', '<', '>', '=', '!', '.', ':', ',', ')', ';']
	keywords = ['True', 'False', 'in', 'break', 'continue', 'return', 'not', 'pass', 'else', 'and', 'or', 'global', 'def', 'class', 'db_class', 'use']

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
			if not is_db_action:
				tokens.append(['FUNCTION', tmp])
			else:
				tokens.append(['DB_ACTION', db_action_indents + tmp])
				is_db_action = False
				tmp = ''
				tokens.append(['OPERATOR', char])
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
					if tmp[-3:] == '_db':
						tokens.append(['CLASS_REFERENCE', db_action_indents + tmp[:-3]])
						is_db_action = True
						is_property = False
						if len(tokens) >= 2:
							if tokens[-2][0] == 'OPERATOR' and tokens[-2][1] == '.':
								tokens.pop(-2)
					else:
						tokens.append(['PROPERTY', tmp])
						is_property = False
					tmp = ''
					continue

				if tmp.replace('\t', '') != '_db':
					tokens.append(['VAR', tmp])
				else:
					is_db_action = True
					db_action_indents, _ = separate_indents_and_content(tmp)
				is_var = False
				tmp = ''
			tokens.append(['LIST_START', char])
		elif char == ']':
			tokens.append(['LIST_END', char])
		elif char == '{':
			tokens.append(['DICT_START', char])
			active_dict = True
		elif char == '}':
			if is_var:
				is_var = False
				if is_property:
					if tmp[-3:] == '_db':
						tokens.append(['CLASS_REFERENCE', db_action_indents + tmp[:-3]])
						is_db_action = True
						is_property = False
						if len(tokens) >= 2:
							if tokens[-2][0] == 'OPERATOR' and tokens[-2][1] == '.':
								tokens.pop(-2)
					else:
						tokens.append(['PROPERTY', tmp])
						is_property = False
					tmp = ''

				if tmp.replace('\t', '') != '_db':
					tokens.append(['VAR', tmp])
				else:
					is_db_action = True
					db_action_indents, _ = separate_indents_and_content(tmp)
				tmp = ''

			tokens.append(['DICT_END', char])
			active_dict = False
		elif char in operators and is_string is False or char_index == len(line) - 1 and is_string is False:
			if is_var:
				is_var = False
				if is_property:
					if tmp[-3:] == '_db':
						tokens.append(['CLASS_REFERENCE', db_action_indents + tmp[:-3]])
						is_db_action = True
						is_property = False
						if len(tokens) >= 2:
							if tokens[-2][0] == 'OPERATOR' and tokens[-2][1] == '.':
								tokens.pop(-2)
					else:
						tokens.append(['PROPERTY', tmp])
						is_property = False
					tmp = ''

					if char != '\n' and not is_db_action:
						tokens.append(['OPERATOR', char])
					continue

				if tmp.replace('\t', '') != '_db':
					tokens.append(['VAR', tmp])
				else:
					is_db_action = True
					db_action_indents, _ = separate_indents_and_content(tmp)
				tmp = ''
			elif active_dict and char == ':':
				tokens.append(['DICT_KEY', tmp])
				tmp = ''
			elif is_class:
				tokens.append(['CLASS_NAME', tmp])
				tmp = ''

			if char == '.' and not is_db_action:
				is_property = True
				is_var = True

			if char != '\n' and not is_db_action:
				tokens.append(['OPERATOR', char])
			elif char in [',', ')'] and is_db_action:
				tokens.append(['DB_ACTION', db_action_indents + tmp])
				is_db_action = False
				tmp = ''
				tokens.append(['OPERATOR', char])
		else:
			if char != ' ' or char == ' ' and is_string:
				if char == '#':
					break
				else:
					tmp += char

					# Checks for keyword
					tmp_tmp_indents, tmp_tmp = separate_indents_and_content(tmp)

					if is_var and len(tmp_tmp) >= 2:
						tmp_keyword_length = 0

						if tmp_tmp[-2:] in ['in', 'or'] and not is_db_action:
							tmp_keyword_length = -2
						elif tmp_tmp[-3:] in ['and'] and not is_db_action:
							tmp_keyword_length = -3

						if tmp_keyword_length:
							if tmp_tmp != '_db':
								tokens.append(['VAR', tmp_tmp_indents + tmp_tmp[:tmp_keyword_length]])
							else:
								is_db_action = True
								db_action_indents = tmp_tmp_indents
							tokens.append(['KEYWORD', tmp_tmp[tmp_keyword_length:]])

							tmp = ''

					elif tmp_tmp in keywords and not is_var and not is_db_action:
						if tmp_tmp in ['db_class', 'class']:
							tokens.append([tmp_tmp.upper(), tmp])
							tmp = ''
							is_class = True
						else:
							tokens.append(['KEYWORD', tmp])
							tmp = ''

	return tokens


def build():
	global parsed

	str_parsed = ''.join(parsed)

	with open('app.py', 'w+') as f:
		f.write('')
		f.write(str_parsed)

	parsed = []


def parse_and_prepare(tokens):
	global parsed
	global flask_boilerplate
	global flask_end_boilerplate

	parser(tokens, 0)
	parsed.insert(0, flask_boilerplate)
	parsed.append(flask_end_boilerplate)


def tokenize(lines):
	global is_multi_line_comment
	global is_dev

	tokens = []
	tokenized_lines = []

	for line in lines:
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

	for line in tokenized_lines:
		for token in line:
			tokens.append(token)
		tokens.append(['LINE', '\n'])

	if is_dev:
		print('--TOKENS:')
		for token in tokens:
			print(token)

	return tokens


def startup(file_name):
	print('\033[1m' + 'Transpiling...' + '\033[0m')

	# Execution time
	start_time = time.time()

	with open(file_name) as f:
		source_lines = f.readlines()

	tokens_list = tokenize(source_lines)
	if tokens_list:
		parse_and_prepare(tokens_list)
		build()

		# Done!
		end_time = time.time()
		time_result = round(end_time - start_time, 3)
		print('\033[92m' + '\t- Transpiled ' + '\033[0m' + str(len(source_lines)) + ' lines in ~' + '\033[94m' + str(time_result) + '\033[0m' + ' seconds')
	else:
		print('\033[91m' + '\t- The file is empty!' + '\033[0m')


# Global variables set up
active_dict = False
is_waiting_for_function_start = False
parsed = []
return_run = False
function_in_route_name = ''
vars_used_by_route = ''
db_action_indents = ''

is_multi_line_comment = False
is_dev = True
flask_boilerplate = 'from flask import Flask, jsonify, abort, request\nfrom ask import AskLibrary\napp = Flask(__name__)\n'
flask_end_boilerplate = '\nif __name__ == \'__main__\':\n\tapp.run()'

if __name__ == '__main__':
	print ('🌳' + '\033[92m' + 'Ask' + '\033[0m')
	if len(sys.argv) > 1:
		source_file_name = sys.argv[1]
		if os.path.isfile(os.getcwd() + '/' + source_file_name):
			startup(source_file_name)
		else:
			print('\033[91m' + 'The file could not be found!' + '\033[0m')
	else:
		print('\033[91m' + 'Please provide a script file!' + '\033[0m')
