# coding=utf-8
import os
from importlib.machinery import SourceFileLoader
from types import ModuleType
from typing import Any, List, Tuple

import waitress
from paste.translogger import TransLogger
import datetime
from tabulate import tabulate

from ask_lang import cfg
from ask_lang.utilities import file_utils
from ask_lang.transpiler import errors


# Prints out text colorized and (optionally) as bold.
def style_print(text, color: str = None, styles: List[str] = None, end: str = '\n'):
	if styles is None:
		styles = []

	prefix = '\033['
	suffix = prefix + '0m'

	available_styles = {
		'bold': '1m'
	}

	colors = {
		'red': '91m',
		'green': '92m',
		'blue': '94m',
		'gray': '90m'
	}

	result = str(text)

	if color in colors:
		result = prefix + colors[color] + result + suffix

	for style in styles:
		result = prefix + available_styles[style] + result + suffix

	print(result, end=end)


def initial_print():
	style_print('🌳Ask', styles=['bold'], color='green', end=' ')
	print(f'{cfg.project_information["version"]}')


def print_transpilation_result(source_lines: str, time_result: float, for_error: bool = False):
	color = 'green' if not for_error else 'red'

	style_print('\t- Transpiled ', color, end='')
	print(f'{len(source_lines)} lines in ~', end='')
	style_print(time_result, color='blue', end='')
	print(' seconds.')


def parse_sys_args(sys_args: List[str]) -> Tuple[str, bool]:
	flags = ['-d', '--dev', '-xd', '--extra-dev', '-v', '--version', '-h', '--help']

	file_name = ''
	no_valid_flags = True

	for param in sys_args[1:]:
		if param in flags:
			no_valid_flags = False

			if param in ['-d', '--dev']:
				cfg.is_dev = True
			if param in ['-xd', '--extra-d']:
				cfg.is_extra_dev = True
				style_print('Extra Dev Mode Activated!', 'red', ['bold'])
			elif param in ['-v', '--version']:
				style_print('- Version:', color='blue', end=' ')
				print(cfg.project_information["version"])
			elif param in ['-h', '--help']:
				print('Usage: ask_lang [OPTIONS] [FILE]...', end='\n\n')
				print(tabulate(
					[
						['-h', '--help', 'Show this message.'],
						['-v', '--version', 'Show version information.'],
						['-d', '--d', 'Turn on developer/debug mode.'],
					],
					headers=['Option', 'Long Format', 'Description']
				))
				print()
				print('Other configurations can be added to a file called `Askfile.toml`.')
				print('Go to: https://docs.ask-lang.org for more information', end='\n\n')
		else:
			file_name = param

	if cfg.is_dev and file_name == '':
		no_valid_flags = True

	return file_name, no_valid_flags


def import_app() -> ModuleType:
	return SourceFileLoader("app", file_utils.get_output_file_destination_path()).load_module('app')


def run_server():
	app: ModuleType = import_app()

	# Starts the server or runs the main function if the app isn't using routes, meaning it's just a script.
	try:
		style_print('Running the app...', styles=['bold'], end=' ')
		print('(Press Ctrl+C to stop)')

		if not cfg.uses_routes:
			# The app is just a script. Ask is used like a general purpose language.
			app.main()

		# The app uses routes, so it's an API, the app needs to run in a web server.
		elif get_config_rule(['server', 'production'], True) is True and cfg.is_dev is False:
			# Run in the production server.
			print('\033[91m\t- ', end='')
			waitress.serve(
				TransLogger(
					app.app,
					logger_name='Ask Application',
					format=' '.join([
						f'\033[37m\t- {datetime.datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")}\033[0m',
						'\033[1m%(REQUEST_METHOD)s\033[0m:'
						'"\033[32m%(REMOTE_ADDR)s%(REQUEST_URI)s\033[0m"',
						'→',
						'\033[94m%(status)s\033[0m',
					])
				),
				host=get_config_rule(['server', 'host'], '127.0.0.1'),
				port=get_config_rule(['server', 'port'], '5000'),
				ident='Ask Application',
			)
		else:
			# Run in the development server.
			os.environ['FLASK_APP'] = file_utils.get_output_file_destination_path()
			if cfg.is_dev:
				os.environ['FLASK_ENV'] = 'development'

			app.app.run()
	except Exception as e:  # Exception is used here to capture all exception types.
		errors.error_while_running(e, cfg.transpilation_result['source_lines'], cfg.transpilation_result['time_result'])

		exit()


def load_askfile_config():
	cfg.ask_config = file_utils.get_ask_config(file_utils.get_root_from_file_path(cfg.source_file_name))


def get_config_rule(key_tree: List[str], not_found) -> Any:
	try:
		current_position = cfg.ask_config[key_tree[0]]

		if len(key_tree) > 1:
			for key in key_tree[1:]:
				current_position = current_position[key]

		return current_position
	except Exception:
		return not_found
