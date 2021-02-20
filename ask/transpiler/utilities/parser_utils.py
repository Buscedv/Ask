# coding=utf-8
from typing import List

from ask import cfg
from ask.transpiler.utilities import transpiler_utils


def is_db_column_in_past_line(tokens: List[list]) -> bool:
	for token in tokens[::-1]:
		if transpiler_utils.token_check(token, 'FORMAT', '\n', ):
			break
		if transpiler_utils.token_check(token, 'DB_ACTION', 'col') or transpiler_utils.token_check(token, 'DB_MODEL'):
			return True

	return False


def get_first_non_keyword_word_token_value_of_line(tokens: List[list]) -> str or None:
	for token in tokens:
		token_type = token[0]
		token_val = token[1]
		if token_type == 'WORD' and token_val not in cfg.keywords:
			return token_val

	return None


def route_path_to_func_name(route: str) -> str:
	return route.replace('/', '_').replace('<', '_').replace('>', '_').replace('-', '_')


def is_part_of_word(thing):
	try:
		return thing.isalpha() or thing == '_'
	except AttributeError:
		return False


def space_prefix(parsed: str, to_add: str = '') -> str:
	prefix = ' '

	# No space at the beginning.
	if not parsed:
		prefix = ''

	# No Space before specific characters.
	if to_add in [':', ',', '(', ')', '.', '[', ']', '{', '}']:
		prefix = ''

	# No space after specific characters.
	if parsed and parsed[-1] in ['(', '.', ' ', '\t', '\n']:
		prefix = ''

	# Space after specific characters.
	if parsed and parsed[-1] in [',']:
		prefix = ' '

	# No space between specific charters and words:
	if parsed and parsed[-1] in ['['] and is_part_of_word(to_add):
		prefix = ''

	# Space between words
	if parsed and is_part_of_word(parsed[-1]) and is_part_of_word(to_add):
		prefix = ' '

	return prefix


def parse_route_params_str(route_path: str) -> str:
	is_param = False
	tmp = ''
	params_str = ''

	for char in route_path:
		if char == '<':
			tmp = ''
			is_param = True
		elif char == '>':
			is_param = False
			if tmp:
				params_str += f'{tmp}, '
				tmp = ''
		elif is_param and char not in [' ' + '\t', '\n']:
			tmp += char

	if len(params_str) > 2 and params_str[-2:] == ', ':
		params_str = params_str[:-2]

	return params_str


def get_current_tab_level(parsed: str) -> str:
	parsed = parsed[::-1]

	indents = ''
	for char in parsed:
		if char == '\t':
			indents += char
		elif char == '\n':
			break

	return indents


def add_underscores_to_dict_keys(dictionary: dict) -> dict:
	with_underscores = {f'_{key}': dictionary[key] for key in dictionary}

	return {**dictionary, **with_underscores}
