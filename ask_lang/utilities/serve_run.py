# coding=utf-8
import os
from importlib.machinery import SourceFileLoader
from types import ModuleType

import waitress
from paste.translogger import TransLogger
import datetime

from ask_lang import cfg
from ask_lang.utilities import files
from ask_lang.transpiler import errors
from ask_lang.utilities import printing
from ask_lang.utilities import askfile


def import_app() -> ModuleType:
	output_file = files.get_file_of_file_path(files.output_file_path()).replace('.py', '')
	return SourceFileLoader(output_file, files.output_file_path()).load_module(output_file)


def run_server():
	app: ModuleType = import_app()

	# Starts the server or runs the main function if the app isn't using routes, meaning it's just a script.
	try:
		if not cfg.is_repl and not cfg.is_module_transpile:
			printing.style_print('Running the app...', styles=['bold'], end=' ')
			print('(Press Ctrl+C to stop)')

		if not cfg.uses_routes:
			# The app is just a script. Ask is used like a general purpose language.
			app.main()

		# The app uses routes, so it's an API, the app needs to run in a web server.
		elif askfile.get(['server', 'production'], True) is True and cfg.is_dev is False:
			# Run in the production server.
			print('\033[91m\t- ', end='')
			waitress.serve(
				TransLogger(
					app.app,
					logger_name='Ask Application',
					format=' '.join([
						f'\033[37m\t- {datetime.datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")}\033[0m',
						'\033[1m%(REQUEST_METHOD)s\033[0m '
						'"\033[32m%(REMOTE_ADDR)s%(REQUEST_URI)s\033[0m"',
						'→',
						'\033[94m%(status)s\033[0m',
					])
				),
				host=askfile.get(['server', 'host'], '127.0.0.1'),
				port=askfile.get(['server', 'port'], '5000'),
				ident='Ask Application',
			)
		else:
			# Run in the development server.
			os.environ['FLASK_APP'] = files.output_file_path()
			if cfg.is_dev:
				os.environ['FLASK_ENV'] = 'development'

			app.app.run()
	except Exception as e:  # Exception is used here to capture all exception types.
		errors.error_while_running(e, cfg.transpilation_result['source_lines'], cfg.transpilation_result['time_result'])

		if cfg.is_repl:
			# Tries to remove the line the error was on.
			if len(cfg.repl_previous_transpiled.split('\n')) > 2:
				cfg.repl_previous_transpiled = '\n'.join(cfg.repl_previous_transpiled.split('\n')[:-2])
			return

		exit(1)
