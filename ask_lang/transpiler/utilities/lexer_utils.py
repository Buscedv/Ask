# coding=utf-8
from typing import List, Tuple

from ask_lang import cfg
from ask_lang.transpiler.utilities import transpiler_utils


# Converts list of single tokens into groups (lists) of tokens where newlines are the separators.
def group_toks_by_lines(tokens: List[List[str]]) -> List[List[List[str]]]:
	tmp = []
	lines = []

	for token in tokens:
		if transpiler_utils.token_check(token, 'FORMAT', '\n'):
			lines.append(tmp)
			tmp = []

		tmp.append(token)

	# The last match.
	if tmp:
		lines.append(tmp)

	return lines


# Figures out if a given name is a special keyword or a word/variable.
def word_or_special(tokens: List[list], tmp: str) -> Tuple[List[list], str, bool, list, bool]:
	collect = False
	collect_ends = []
	include_collect_end = False

	if tmp:
		if tmp in cfg.special_keywords:
			# The word is a "special keyword". Collection starts.
			tokens.append([cfg.special_keywords[tmp]['type'], tmp])

			collect = cfg.special_keywords[tmp]['collect']
			collect_ends = cfg.special_keywords[tmp]['collect_ends']
			include_collect_end = cfg.special_keywords[tmp]['include_collect_end']
		else:
			tokens.append(['WORD', tmp])
		tmp = ''
	return tokens, tmp, collect, collect_ends, include_collect_end


# This function is part of reformat_line().
def add_chunk(chunks: list, is_string: bool, code: str) -> Tuple[list, str, bool]:
	chunks.append({
		'is_string': is_string,
		'code': code
	})

	is_string = True

	if code[-1] == '\n':
		is_string = False

	return chunks, '', is_string


# Removes the spaces between function names and '(' characters.
# Replaces 4 & 2 spaces with tab characters.
def reformat_line(statement: str) -> str:
	statement = statement.replace("'", '"')

	if statement and statement[-1] != '\n':
		statement += '\n'

	chunks = []
	is_string = False
	tmp = ''

	# Groups the code into chunks that are labeled as strings and not strings.
	# This way spaces->tabs conversion etc. doesn't interfere with spaces inside strings.
	for char in statement:
		tmp += char

		if char == '"' and is_string:
			chunks, tmp, is_string = add_chunk(chunks, True, tmp)
			is_string = False
		elif char in ['"', '\n']:
			chunks, tmp, is_string = add_chunk(chunks, False, tmp)

	# Fixes indentation based on the generated chucks.
	statement = ''
	for chunk in chunks:
		if not chunk['is_string']:
			chunk['code'] = chunk['code'] \
				.replace('    ', '\t') \
				.replace('  ', '\t') \
				.replace(' (', '(')

		statement += chunk['code']

	return statement
