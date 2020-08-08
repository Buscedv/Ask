import sys
from pprint import pprint


def clean(string):
	return string.replace('\t', '')


def lex(raw):
	is_string = False
	is_dict = False
	is_route = False
	is_route_path = False
	tmp = ''
	tmp_2 = ''

	operators = ['=', '-', '+', '*', '/', '%', ',', ')', '.', ':', '{', '}']
	keywords = ['if', 'else', 'elif', 'not', 'and', 'return', 'in']

	tokens = []

	for line in raw:
		for char_index, char in enumerate(line):
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
				elif char in ['"', '\''] and is_string:
					is_string = False
					tokens.append(['STRING', tmp])
					tmp = ''
				elif is_string is False and char == '(':
					if clean(tmp)[:3] == 'def':
						tmp = tmp[4:]
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
								tmp = ''
								tokens.append(['OPERATOR', '=='])
								continue
						tokens.append(['VAR', tmp])
					if char in [',', ')', '.'] and tmp:
						tokens.append(['VAR', tmp])
					elif char == ':' and is_dict is False:
						if tmp[:8] == 'db_class':
							tmp = tmp[8:]
							tokens.append(['DB_CLASS', tmp])
					elif char == '{':
						is_dict = True
					elif char == '}' and is_dict:
						is_dict = False
					tmp = ''
					tokens.append(['OPERATOR', char])
				else:
					if char == ' ' and is_string is False:
						if tmp in keywords:
							tokens.append(['KEYWORD', tmp])
							tmp = ''
					if is_string or is_string is False and char not in ['\n', ' ']:
						tmp += char
					else:
						if char_index == len(line) - 1 and tmp:
							if clean(tmp) in keywords:
								tokens.append(['KEYWORD', tmp])
							else:
								tokens.append(['VAR', tmp])
							tmp = ''

	return tokens


file_name = sys.argv[1]

with open(file_name) as f:
	raw_code = f.readlines()

pprint(lex(raw_code))
