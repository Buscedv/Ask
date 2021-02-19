# coding=utf-8
from typing import List, Tuple

from ask import cfg
from ask.transpiler.utilities import small_transpilers


def group_tokens_by_lines(tokens: List[list]) -> List[list]:
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


# Figures out if a given name should be lexed as a keyword or variable token.
def var_or_keyword_token(tokens: List[list], tmp: str) -> Tuple[List[list], str, bool, list, bool]:
	collect = False
	collect_ends = []
	include_collect_end = False

	if tmp:
		if tmp in cfg.keywords:
			tokens.append(['KEYWORD', small_transpilers.transpile_keyword(tmp)])
		elif tmp in cfg.special_keywords.keys():
			tokens.append([cfg.special_keywords[tmp]['type'], tmp])

			collect = cfg.special_keywords[tmp]['collect']
			collect_ends = cfg.special_keywords[tmp]['collect_ends']
			include_collect_end = cfg.special_keywords[tmp]['include_collect_end']
		else:
			tokens.append(['VAR', tmp])
		tmp = ''
	return tokens, tmp, collect, collect_ends, include_collect_end


# This function is part of fix_up_code_line().
def add_part(parts: list, is_string: bool, code: str) -> Tuple[list, str, bool]:
	parts.append({
		'is_string': is_string,
		'code': code
	})

	is_string = True

	if code[-1] == '\n':
		is_string = False

	return parts, '', is_string


# Removes the spaces between function names and '(' characters.
# Replaces 4 & 2 spaces with tab characters.
def fix_up_code_line(statement: str) -> str:
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
			part['code'] = part['code'] \
				.replace('    ', '\t') \
				.replace('  ', '\t') \
				.replace(' (', '(')

		statement += part['code']

	return statement
