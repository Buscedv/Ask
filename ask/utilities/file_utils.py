import os

from ask import cfg


def get_root_from_file_path(file_path):
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


def get_ask_config(source_root):
	import json

	if source_root:
		source_root += '/'

	askfile_path = f'{source_root}Askfile'

	if os.path.isfile(askfile_path):
		with open(askfile_path, 'r') as f:
			return json.loads(''.join(f.readlines()))

	return {}


def get_full_db_file_path(is_boilerplate_insertion_use=False):
	prefix = 'sqlite:///'

	if cfg.ask_config and 'db' in cfg.ask_config and 'custom' in cfg.ask_config['db'] and cfg.ask_config['db']['custom']:
		prefix = ''

	return f'{prefix}{get_db_file_path(is_boilerplate_insertion_use)}'


def get_db_file_path(is_boilerplate_insertion_use=False):
	end = 'db.db'

	path = get_output_file_destination_path()[:-6]

	if is_boilerplate_insertion_use:
		path = f'{os.getcwd()}/{path}'

	if cfg.ask_config and 'db' in cfg.ask_config and 'path' in cfg.ask_config['db']:
		custom_path = cfg.ask_config['db']['path']
		if not path or path[0] != '/':
			end = custom_path
		else:
			return custom_path

	return path + end


# Returns the path to be used for the app.py file.
def get_output_file_destination_path():
	prefix = ''
	if '/' in cfg.source_file_name:
		prefix = f'{get_root_from_file_path(cfg.source_file_name)}/'

	return f'{prefix}app.py'
