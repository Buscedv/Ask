# coding=utf-8
import os

from ask_lang import cfg
from ask_lang.utilities import utils


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
			return toml.loads(''.join(f.readlines()))

	return {}


def get_full_db_file_path(is_boilerplate_insertion_use: bool = False) -> str:
	prefix = 'sqlite:///'

	if utils.get_config_rule(['db', 'custom'], False):
		prefix = ''

	return f'{prefix}{get_db_file_path(is_boilerplate_insertion_use)}'


def get_db_file_path(is_boilerplate_insertion_use: bool = False) -> str:
	end = 'db.db'

	path = get_output_file_destination_path()[:-6]

	if is_boilerplate_insertion_use:
		path = f'{os.getcwd()}/{path}'

	if utils.get_config_rule(['db', 'path'], ''):
		custom_path = cfg.ask_config['db']['path']
		if not path or path[0] != '/':
			end = custom_path
		else:
			return custom_path

	return f'{path}{end}'


# Returns the path to be used for the app.py file.
def get_output_file_destination_path() -> str:
	prefix = ''
	if '/' in cfg.source_file_name:
		prefix = f'{get_root_from_file_path(cfg.source_file_name)}/'

	return f'{prefix}app.py'
