# coding=utf-8
import os
import sys
from typing import List

from ask_lang import cfg
from ask_lang.utilities import files
from ask_lang.transpiler.utilities import transpiler_utils


def include_module(module_name: str) -> str:
	_, transpiled_file_name = might_be_ask_import(module_name.replace('.', '/'), '--include-transpile')

	with open(transpiled_file_name, 'r') as f:
		to_return = ''.join(f.readlines())

	os.remove(transpiled_file_name)

	return to_return


def might_be_ask_import(module: str, flags: str = '') -> (list, str):
	# Checks if the imported module is a local .ask file.
	# If it is transpile it.
	# Otherwise ignore it and just append it to the output, it can be a python module for instance.

	if module in cfg.imported_ask_modules_to_delete:
		return []

	try:
		if os.path.isfile(f'{files.get_root_from_file_path(files.output_file_path())}/{module}.ask'):
			print('\t✅\n\t- Transpiling external module...', end='')
			os.system(
				f'python3 {sys.argv[0]} {f"{files.get_root_from_file_path(cfg.source_file_name)}/{module}.ask"} --module-transpile {flags}')

		cfg.imported_ask_modules_to_delete.append(module)

		module_file = f'"{files.get_root_from_file_path(files.output_file_path())}/{module}.py"'

		return [
			f'spec = importlib.util.spec_from_file_location("{module}", {module_file})',
			f'{module} = importlib.util.module_from_spec(spec)',
			f'spec.loader.exec_module({module})',
		], module_file[1:-1]
	except Exception:
		return []


# Is there a db column or model defined in the most recent/current line (in tokens).
def is_db_column_or_model_in_past_line(tokens: List[list]) -> bool:
	for token in tokens[::-1]:
		if transpiler_utils.token_check(token, 'FORMAT', '\n', ):
			break
		if transpiler_utils.token_check(token, 'DB_ACTION', 'col') or transpiler_utils.token_check(token, 'DB_MODEL'):
			return True

	return False


def previous_non_keyword_word_tok(tokens: List[list]) -> str or None:
	for token in tokens:
		token_type = token[0]
		token_val = token[1]
		if token_type == 'WORD' and token_val not in cfg.keywords:
			return token_val

	return None


# Converts URI strings to a format that can be used as a Python function name.
def uri_to_func_name(route: str) -> str:
	return route.replace('/', '_').replace('<', '_').replace('>', '_').replace('-', '_').replace('\'', '').replace('"', '')


# Is the symbol a letter or underscore.
def is_word_char(thing):
	try:
		return thing.isalpha() or thing == '_'
	except AttributeError:
		return False


# Returns either a space or an empty string based on if the translated token to append should have a space before it.
def space_prefix(translated: str, to_add: str = '') -> str:
	prefix = ' '

	# No space at the beginning.
	if not translated:
		prefix = ''

	# No Space before specific characters.
	if to_add in [':', ',', '(', ')', '.', '[', ']', '{', '}']:
		prefix = ''

	if translated:
		# No space after specific characters.
		if translated[-1] in ['(', '.', ' ', '\t', '\n']:
			prefix = ''

		# Space after specific characters.
		if translated[-1] in [',']:
			prefix = ' '

		# No space between specific charters and words:
		if translated[-1] in ['['] and is_word_char(to_add):
			prefix = ''

		# Space between words
		if is_word_char(translated[-1]) and is_word_char(to_add):
			prefix = ' '

	return prefix


# Finds parameters in URI strings.
def extract_params_from_uri(route_path: str) -> str:
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


def get_tab_count(translated: str) -> str:
	translated = translated[::-1]

	indents = ''
	for char in translated:
		if char == '\t':
			indents += char
		elif char == '\n':
			break

	return indents


def add_underscores_to_dict_keys(dictionary: dict) -> dict:
	with_underscores = {f'_{key}': dictionary[key] for key in dictionary}

	return {**dictionary, **with_underscores}
