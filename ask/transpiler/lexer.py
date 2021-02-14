from pprint import pprint

import ask.cfg as cfg
from ask.transpiler.utilities import lexer_utils


def lexer(raw):
	tmp = ''
	is_collector = False
	collector_ends = []
	include_collector_end = False
	is_dict = []

	tokens = []

	for line in raw:
		line = lexer_utils.fix_up_code_line(line)
		for char_index, char in enumerate(line):
			if char == '#':
				# tokens.append(['FORMAT', '\n'])
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

					if tmp not in cfg.variables:
						cfg.variables.append(tmp)

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
				tokens, tmp, is_collector, collector_ends, include_collector_end = lexer_utils.lex_var_keyword(tokens, tmp)

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
			elif char in cfg.operators:
				if char == ':' and is_dict and tmp:
					tokens.append(['KEY', tmp])
					tmp = ''

				tokens, tmp, is_collector, collector_ends, include_collector_end = lexer_utils.lex_var_keyword(tokens, tmp)
				tokens.append(['OP', char])
			elif char not in ['\n', '\t', ' ']:
				tmp += char
			elif char in ['\n', '\t']:
				tokens, tmp, is_collector, collector_ends, include_collector_end = lexer_utils.lex_var_keyword(tokens, tmp)
				tokens.append(['FORMAT', char])
			else:
				tokens, tmp, is_collector, collector_ends, include_collector_end = lexer_utils.lex_var_keyword(tokens, tmp)

			if len(tokens) > 2 and tokens[-2][0] == 'VAR' and tokens[-2][1] in ['db', '_db']:
				# Removes both the VAR: _db and the OP: .
				tokens.pop(-1)
				tokens.pop(-1)
				is_collector = True
				collector_ends = ['(', ',', ')']
				include_collector_end = True
				tmp = ''
				tokens.append(['DB_ACTION', ''])
				cfg.uses_db = True
	return tokens


def insert_indention_group_markers(tokens):
	lines = lexer_utils.tokens_grouped_by_lines(tokens)

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


def lex(source_lines):
	tokens_list = lexer(source_lines)
	tokens_list = insert_indention_group_markers(tokens_list)

	if cfg.is_dev:
		print('\n')
		pprint(tokens_list)
		print('\n')

	return tokens_list
