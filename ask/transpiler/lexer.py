# coding=utf-8
from typing import List

import ask.cfg as cfg
from ask.utilities import utils
from ask.transpiler.utilities import lexer_utils, transpiler_utils


def lexer(raw: List[str]) -> List[List[str]]:
	tmp = ''
	is_collector = False
	collector_ends = []
	include_collector_end = False
	is_dict = []

	tokens = []

	for line in raw:
		line = lexer_utils.fix_up_code_line(line)
		for char_index, char in enumerate(line):
			# Ignores comments
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

			# Function call.
			elif char == '(':
				if tmp:
					tokens.append(['FUNC', tmp.replace(' ', '')])
					tmp = ''

			# Variable assignment.
			elif char == '=':
				if tmp:
					tokens.append(['VAR', tmp])
					tokens.append(['ASSIGN', char])

					if tmp not in cfg.variables:
						cfg.variables.append(tmp)

					tmp = ''
				else:
					tokens.append(['OP', char])

			# String.
			elif char in ['"', '\'']:
				is_collector = True
				collector_ends = ['"', '\'']
				include_collector_end = False
				tmp = ''
				tokens.append(['STR', ''])

			# Dict open.
			elif char == '{':
				is_dict.append(True)
				tokens.append(['OP', char])

			# Dict close.
			elif char == '}':
				tokens, tmp, is_collector, collector_ends, include_collector_end = lexer_utils.var_or_keyword_token(
					tokens, tmp)

				is_dict.pop(0)
				tokens.append(['OP', char])

			# Number (on its own).
			elif char.isdigit() and not tmp:
				if tokens and tokens[-1][0] == 'NUM':
					tokens[-1][1] += char
					continue
				tokens.append(['NUM', char])

			# Decorator.
			elif char == '&':
				is_collector = True
				collector_ends = ['\n']
				include_collector_end = True
				tmp = ''
				tokens.append(['DEC', ''])

			# Operator (special character).
			elif char in cfg.operators:
				if char == ':' and is_dict and tmp:
					tokens.append(['KEY', tmp])
					tmp = ''

				tokens, tmp, is_collector, collector_ends, include_collector_end = lexer_utils.var_or_keyword_token(
					tokens, tmp)
				tokens.append(['OP', char])

			# Formating.
			elif char in ['\n', '\t']:
				tokens, tmp, is_collector, collector_ends, include_collector_end = lexer_utils.var_or_keyword_token(
					tokens, tmp)
				tokens.append(['FORMAT', char])

			# Character isn't anything specific, meaning it's e.g. a letter. These get collected for later use.
			elif char not in ['\n', '\t', ' ']:
				tmp += char
			else:
				# There might be a full variable or keyword in tmp.
				tokens, tmp, is_collector, collector_ends, include_collector_end = lexer_utils.var_or_keyword_token(
					tokens, tmp)

			if len(tokens) > 2 and transpiler_utils.token_check(
					tokens[-2],
					'VAR',
					transpiler_utils.add_underscores_to_elements(['db'])
					if utils.get_config_rule(['rules', 'underscores'], True)
					else 'db'
			):
				# Removes the VAR 'db'/'_db' and the OP '.'.
				tokens.pop(-1)
				tokens.pop(-1)
				is_collector = True
				collector_ends = ['(', ',', ')']
				include_collector_end = True
				tmp = ''
				tokens.append(['DB_ACTION', ''])
				cfg.uses_db = True

	return tokens


def insert_indention_group_markers(tokens: List[List[str]]) -> List[List[str]]:
	lines = lexer_utils.group_tokens_by_lines(tokens)

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


def lex(source_lines: List[str]) -> List[List[str]]:
	tokens_list = lexer(source_lines)
	return insert_indention_group_markers(tokens_list)
