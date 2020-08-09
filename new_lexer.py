import sys
from pprint import pprint


def clean(string):
	return string.replace('\t', '').replace(' ', '')


def keyword_at_end_lexer(tmp, tokens):
	global variables

	tmp = clean(tmp)
	if len(tmp) > 2:
		if tmp[-2:] in ['or', 'in']:
			if tmp[:-2] in variables:
				tokens.append(['VAR', tmp[:-2]])
				tokens.append(['KEYWORD', tmp[-2:]])

	return tokens


def lex(raw):
	is_string = False
	is_dict = []
	is_list = []
	is_route = False
	is_route_path = False
	tmp = ''
	tmp_2 = ''

	global variables

	operators = ['=', '-', '+', '*', '/', '%', ',', ')', '.', ':', '{', '}', '[', ']']
	keywords = ['if', 'else', 'elif', 'not', 'and', 'or', 'return', 'in', 'for']

	tokens = []

	for line in raw:
		for char_index, char in enumerate(line):
			if len(tokens) > 2:
				if tokens[-1][0] == 'OPERATOR' and tokens[-2][0] == 'OPERATOR':
					if len(tokens[-1][1]) == 1 and len(tokens[-2][1]) == 1:
						if tokens[-1][1] in ['!', '|', '&']:
							tokens.pop(-1)
							tokens[-1][1] = tokens[-1][1] + tokens[-1][1]

			if is_route:
				if is_route_path:
					if char in ['"', '\'']:
						if is_string:
							is_string = False
							is_route_path = False
							is_route = False
							tokens.append([tmp_2.upper() + '_ROUTE', tmp])
							tmp = ''
							tmp_2 = ''
						else:
							is_string = True
					else:
						tmp += char
				else:
					if char != '(':
						tmp += char
					else:
						tmp_2 = tmp
						tmp = ''
						is_route_path = True
			else:
				if is_dict and char == ':' and is_string is False:
					tokens.append(['KEY', tmp])
					tmp = ''
				if char == '#' and is_string is False:
					break
				elif char == '@':
					is_route = True
					tmp = ''
				elif char in ['"', '\''] and is_string is False:
					is_string = True
					if tmp:
						if clean(tmp) in operators:
							tokens.append(['OPERATOR', tmp])
						elif clean(tmp) in keywords:
							tokens.append(['KEYWORD', tmp])
						tmp = ''
				elif char in ['"', '\''] and is_string:
					is_string = False
					tokens.append(['STRING', tmp])
					tmp = ''
				elif is_string is False and char == '(':
					if clean(tmp)[:3] == 'def':
						tmp = clean(tmp)[3:]
						tokens.append(['KEYWORD', 'def'])
					tokens.append(['FUNCTION', tmp])
					tmp = ''
				elif is_string is False and char in operators:
					if clean(tmp) in keywords:
						tokens.append(['KEYWORD', tmp])
						tmp = ''

					if char == '=':
						if tokens:
							if tokens[-1][1] == '==' and tokens[-1][0] == 'OPERATOR':
								continue
						if char_index < len(line):
							if line[char_index + 1] == '=':
								tokens.append(['VAR', tmp])
								variables.append(clean(tmp))
								tmp = ''
								tokens.append(['OPERATOR', '=='])
								continue
						tokens.append(['VAR', tmp])
						variables.append(clean(tmp))
					if char in [',', ')', '.'] and tmp:
						tokens.append(['VAR', tmp])
						variables.append(clean(tmp))
					elif char == ':' and is_dict == []:
						if tmp[:8] == 'db_class':
							tmp_tmp = tmp[8:]
							tokens.append(['DB_CLASS', tmp_tmp])
						else:
							if tmp:
								if clean(tmp) in keywords:
									tokens.append(['KEYWORD', tmp])
								elif clean(tmp) in variables:
									tokens.append(['VAR', tmp])
									variables.append(clean(tmp))
								tmp = ''
					elif char == '{':
						is_dict.append(True)
					elif char == '}' and is_dict:
						is_dict.pop(-1)
					elif char == '[':
						if tmp:
							if clean(tmp) in variables:
								tokens.append(['VAR', tmp])
							tmp = ''
						is_list.append(True)
					elif char == ']' and is_list:
						is_list.pop(-1)
					tmp = ''
					tokens.append(['OPERATOR', char])
				else:
					if char == ' ' and is_string is False:
						if tmp:
							if clean(tmp) in keywords:
								tokens.append(['KEYWORD', tmp])
								tmp = ''
							elif len(clean(tmp)) > 2:
								tokens = keyword_at_end_lexer(tmp, tokens)
					if is_string or is_string is False and char not in ['\n', '']:
						tmp += char

					elif len(clean(tmp)) > 2:
						tokens = keyword_at_end_lexer(tmp, tokens)
					else:
						if char_index == len(line) - 1 and tmp:
							if clean(tmp) in keywords:
								tokens.append(['KEYWORD', tmp])
							else:
								tokens.append(['VAR', tmp])
								variables.append(clean(tmp))
							tmp = ''

	return tokens


variables = ['_body', '_auth', '_env', '_db']

file_name = sys.argv[1]

with open(file_name) as f:
	raw_code = f.readlines()

pprint(lex(raw_code))
