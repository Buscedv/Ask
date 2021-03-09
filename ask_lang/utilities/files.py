# coding=utf-8
import os

from ask_lang import cfg
from ask_lang.utilities import askfile


def get_root_from_file_path(file_path: str) -> str:
	final_path = ''
	adder = False

	for char in file_path[::-1]:
		if adder:
			final_path += char
		elif char == '/':
			adder = True

	if not file_path:
		final_path = file_path

	return final_path[::-1]


def get_file_of_file_path(file_path: str):
	return file_path[len(get_root_from_file_path(file_path)):]


def get_ask_config(source_root: str) -> dict:
	import toml

	if source_root:
		source_root += '/'

	askfile_path = f'{source_root}Askfile'

	# JSON (backwards compatibility).
	if os.path.isfile(askfile_path):
		import json

		with open(askfile_path, 'r') as f:
			return json.loads(''.join(f.readlines()))

	# TOML (recommended).
	askfile_path += '.toml'
	if os.path.isfile(askfile_path):
		with open(askfile_path, 'r') as f:
			return dict(toml.loads(''.join(f.readlines())))

	return {}


def db_path_with_prefix() -> str:
	prefix = 'sqlite:///'

	if askfile.get(['db', 'custom'], False):
		prefix = ''

	return f'{prefix}{get_db_file_path()}'


def generic_construct_output_file_path(file_name_or_path):
	prefix = f'{os.getcwd()}/'

	if askfile.get(['db', 'custom'], False):
		prefix = ''

	if '/' in cfg.source_file_name:
		prefix += f'{get_root_from_file_path(cfg.source_file_name)}/'

	if file_name_or_path[0] == '/':
		file_name_or_path = file_name_or_path[1:]

	return prefix + file_name_or_path


def get_db_file_path() -> str:
	return generic_construct_output_file_path(askfile.get(['db', 'path'], 'db.db'))


# Returns the path to be used for the app.py file.
def output_file_path() -> str:
	return generic_construct_output_file_path(askfile.get(['system', 'output_path'], 'app.py'))


def maybe_delete_app(force: bool = False):
	if not askfile.get(['system', 'keep_app'], True) or force:
		try:
			os.remove(output_file_path())

			for module in cfg.imported_ask_modules_to_delete:
				os.remove(f'{get_root_from_file_path(output_file_path())}/{module}.py')
		except FileNotFoundError:
			return
