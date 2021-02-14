import os
from importlib.machinery import SourceFileLoader

from ask import cfg
from ask.utilities import file_utils
from ask.transpiler import errors


# Prints out text colorized and (optionally) as bold.
def style_print(text, color=None, styles=[], end='\n'):
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
	print('🌳', end='')
	style_print('Ask', color='green')


def print_transpilation_result(source_lines, time_result, for_error=False):
	color = 'green' if not for_error else 'red'

	style_print('\t- Transpiled ', color, end='')
	print(f'{len(source_lines)} lines in ~', end='')
	style_print(time_result, color='blue', end='')
	print(' seconds.')


def parse_sys_params(sys_args):
	flags = ['-d', '--dev', '-v', '--version', '-h', '--help']

	file_name = ''
	no_valid_flags = True

	for param in sys_args[1:]:
		if param in flags:
			no_valid_flags = False

			if param in ['-d', '--dev']:
				cfg.is_dev = True
			elif param in ['-v', '--version']:
				style_print('- Version:', color='blue', end=' ')
				print(cfg.project_information["version"])
			elif param in ['-h', '--help']:
				# TODO: Add help menu/manual.
				print('Go to: https://ask-lang.org for more information')
		else:
			file_name = param

	if cfg.is_dev and file_name == '':
		# TODO: More info?
		no_valid_flags = True

	return file_name, no_valid_flags


def import_app():
	return SourceFileLoader("app", file_utils.get_output_file_destination_path()).load_module()


def run_dev_server():
	app = import_app()

	style_print('Running Flask app:', styles=['bold'])
	os.environ['FLASK_APP'] = file_utils.get_output_file_destination_path()
	if cfg.is_dev:
		os.environ['FLASK_ENV'] = 'development'

	# Starts the server.
	try:
		app.app.run()
	except Exception as e:  # Exception is used here to capture all exception types.
		errors.error_while_running(e, cfg.transpilation_result['source_lines'], cfg.transpilation_result['time_result'])

		exit()


def load_askfile_config():
	cfg.ask_config = file_utils.get_ask_config(file_utils.get_root_from_file_path(cfg.source_file_name))
