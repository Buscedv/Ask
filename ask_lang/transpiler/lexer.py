# coding=utf-8
from typing import List

import ask_lang.cfg as cfg
from ask_lang.utilities import utils
from ask_lang.transpiler.utilities import lexer_utils, transpiler_utils


def lex(raw: List[str]) -> List[List[str]]:
	tmp = ''
	is_collector = False
	collector_ends = []
	include_collector_end = False
	is_dict = []

	tokens = []

	for line in raw:
		line = lexer_utils.reformat_line(line)
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
						tokens.append(['OP' if char not in ['\n', '\t'] else 'FORMAT', char])

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
					tokens.append(['WORD', tmp])
					tokens.append(['OP', char])

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
				tokens, tmp, is_collector, collector_ends, include_collector_end = lexer_utils.word_or_special(
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

				tokens, tmp, is_collector, collector_ends, include_collector_end = lexer_utils.word_or_special(
					tokens, tmp)
				tokens.append(['OP', char])

			# Formating.
			elif char in ['\n', '\t']:
				tokens, tmp, is_collector, collector_ends, include_collector_end = lexer_utils.word_or_special(
					tokens, tmp)
				tokens.append(['FORMAT', char])

			# Character isn't anything specific, meaning it's e.g. a letter. These get collected for later use.
			elif char not in ['\n', '\t', ' ']:
				tmp += char
			else:
				# There might be a word or keyword in tmp.
				tokens, tmp, is_collector, collector_ends, include_collector_end = lexer_utils.word_or_special(
					tokens, tmp)

			if len(tokens) > 2 and transpiler_utils.token_check(
					tokens[-2],
					'WORD',
					transpiler_utils.add_underscores_to_elems(['db'])
					if utils.get_config_rule(['rules', 'underscores'], True)
					else 'db'
			):
				# Removes the WORD 'db'/'_db' and the OP '.'.
				tokens.pop(-1)
				tokens.pop(-1)
				is_collector = True
				collector_ends = ['(', ',', ')']
				include_collector_end = True
				tmp = ''
				tokens.append(['DB_ACTION', ''])
				cfg.uses_db = True

	return tokens


def insert_indent_group_markers(tokens: List[List[str]]) -> List[List[str]]:
	lines = lexer_utils.group_toks_by_lines(tokens)

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


# Merges together operator tokens that are next to each other (e.g = = becomes ==).
def merge_ops(tokens: List[List[str]]) -> List[List[str]]:
	result = []
	tmp = []

	for token in tokens:
		if token[0] == 'OP' and token[1] in ['=', ':', '-', '+', '*', '/', '%', '&', '|', '<', '>', '^', '!']:
			tmp.append(token[1])
		else:
			if tmp:
				result.append(['OP', ''.join(tmp)])
				tmp = []

			result.append(token)

	# Last match
	if tmp:
		result.append(['OP', ''.join(tmp)])

	return result


def lexer(source_lines: List[str]) -> List[List[str]]:
	tokens_list = lex(source_lines)
	tokens_list = merge_ops(tokens_list)
	return insert_indent_group_markers(tokens_list)
