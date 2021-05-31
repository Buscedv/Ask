# coding=utf-8

import os
import sys
from typing import List, Tuple

from tabulate import tabulate

from ask_lang import cfg
from ask_lang.transpiler import transpiler
from ask_lang.utilities import files, serve_run, printing, askfile
from ask_lang.utilities.printing import style_print


def parse_sys_args(sys_args: List[str], is_unittest=False) -> Tuple[str, bool]:
	flags = ['-d', '--dev', '-xd', '--extra-dev', '-v', '--version', '-h', '--help', '--module-transpile', '--include-transpile']

	file_name = ''
	no_valid_flags = True

	for param in sys_args[1:]:
		if param in flags:
			no_valid_flags = False

			if param in ['-d', '--dev']:
				cfg.is_dev = True
			if param in ['-xd', '--extra-d']:
				cfg.is_extra_dev = True

				if is_unittest:
					continue
				printing.style_print('Extra Dev Mode Activated!', 'red', ['bold'])
			elif param in ['-v', '--version']:
				if is_unittest:
					continue

				printing.style_print('- Version:', color='blue', end=' ')
				print(cfg.project_information["version"])
			elif param in ['-h', '--help']:
				if is_unittest:
					continue

				print('Usage: ask_lang [OPTIONS] [FILE]...', end='\n\n')
				print(tabulate(
					[
						['-h', '--help', 'Show this message.'],
						['-v', '--version', 'Show version information.'],
						['-d', '--dev', 'Turn on development & debug mode.'],
					],
					headers=['Option', 'Long Format', 'Description']
				))
				print()
				print('Other configurations can be added to a file called `Askfile.toml`.')
				print('Go to: https://docs.ask-lang.org for more information', end='\n\n')
			elif param == '--module-transpile':
				cfg.ask_config = {
					'system': {
						'output_path': '',
						'server': False
					}
				}

				cfg.is_module_transpile = True
			elif param == '--include-transpile':
				cfg.is_include_transpile = True
		else:
			file_name = param

	if cfg.is_dev and file_name == '':
		no_valid_flags = True

	if cfg.is_module_transpile:
		cfg.ask_config['system']['output_path'] = files.get_file_of_file_path(file_name.replace('.ask', '.py'))

	return file_name, no_valid_flags


def repl(first_time: bool = False):
	cfg.is_repl = True

	if first_time:
		printing.initial_print()
		printing.style_print('Type "q" to quit.', color='gray')

	line = input('Ask >>> ')

	# Quit/Exit
	if line == 'q':
		files.maybe_delete_app(True)
		return

	transpiler.transpile([line])
	serve_run.run_server()

	repl()


def main():
	cfg.set_defaults()

	if len(sys.argv) > 1:
		param_file_name, no_valid_flags = parse_sys_args(sys.argv)
		cfg.source_file_name = param_file_name

		# Load the config if it hasn't been set.
		# This will only be false when running in module transpile mode.
		if not cfg.ask_config:
			askfile.load()

		if not param_file_name and True in [x in sys.argv for x in ['-d', '--dev', '-xd', '--extra-dev']]:
			repl(True)

		if not cfg.is_module_transpile:
			printing.initial_print()

		if os.path.isfile(f'{os.getcwd()}/{cfg.source_file_name}'):
			transpiler.transpile_from_file()

			if askfile.get(['system', 'server'], True):
				# Starts server
				serve_run.run_server()
			elif not cfg.is_module_transpile:
				printing.style_print('\nAuto start server is turned OFF.', styles=['bold'])
				print('\t - The transpiled code can be found in:', end=' ')
				printing.style_print(askfile.get(['system', 'output_path'], 'app.py'), color='blue', end='')
				print('.')
		else:
			if no_valid_flags:
				if param_file_name[0] == '-':
					style_print(f'- Invalid flag "{param_file_name}".', color='yellow')
					exit(1)

				printing.style_print('- The file could not be found!', color='red')
				exit(1)

		# Deletes the output file if configured to.
		files.maybe_delete_app()
	else:
		repl(True)


if __name__ == '__main__':
	cfg.set_defaults()
	main()
