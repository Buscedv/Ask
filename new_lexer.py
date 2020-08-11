import sys
from pprint import pprint


def transpile_var(var):
	vars = {
		'_auth': '_auth',
		'_env': '_env',
		'_db': 'db'
	}

	try:
		return vars[var]
	except Exception:
		return ''


def parser(tokens):
	global built_in_vars

	parsed = ''

	for token in tokens:
		token_type = token[0]
		token_val = token[1]

		if token_type in ['FORMAT', 'OP']:
			parsed += token_val
		elif token_type == 'STR':
			parsed += '"' + token_val + '" '
		elif token_type == 'KEYWORD':
			prefix = ' '

			if parsed:
				if parsed[-1] == '\n':
					prefix = ''
			parsed += prefix + token_val + ' '
		elif token_type == 'VAR':
			if token_val not in built_in_vars:
				parsed += token_val
			else:
				parsed += transpile_var(token_val)
		elif token_type == 'FUNC':
			parsed += token_val + '('
		elif token_type == 'DB_CLASS':
			parsed += 'class ' + token_val
		elif token_type == 'FUNC_DEF':
			parsed += 'def ' + token_val + '('
		elif token_type == 'KEY':
			parsed += '\'' + token_val + '\''

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
			tmp = ''
		elif tmp in special_keywords.keys():
			tokens.append([special_keywords[tmp]['type'], tmp])
			collect = special_keywords[tmp]['collect']
			collect_ends = special_keywords[tmp]['collect_ends']
			include_collect_end = special_keywords[tmp]['include_collect_end']
			tmp = ''
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

	tokens = []

	for line in raw:
		for char_index, char in enumerate(line):
			if char == '#':
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
				if tokens:
					if tokens[-1][0] == 'NUM':
						tokens[-1][1] += char
						continue
				tokens.append(['NUM', char])
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

	return tokens


built_in_vars = ['_body', '_auth', '_env', '_db', 'int', 'pk', 'unique']
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
	}
}
operators = [':', ')', '!', '+', '-', '*', '/', '%', '.', ',', '[', ']']

file_name = sys.argv[1]

with open(file_name) as f:
	raw_code = f.readlines()

pprint(lexer(raw_code))

print(parser(lexer(raw_code)))
