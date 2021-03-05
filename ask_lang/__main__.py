# coding=utf-8

import os
import sys
from typing import List, Tuple

from tabulate import tabulate

from ask_lang import cfg
from ask_lang.transpiler import transpiler
from ask_lang.utilities import files, serve_run, printing, askfile


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
				printing.style_print('Extra Dev Mode Activated!', 'red', ['bold'])
			elif param in ['-v', '--version']:
				printing.style_print('- Version:', color='blue', end=' ')
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


def repl(first_time: bool = False):
	cfg.is_repl = True

	if first_time:
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
	printing.initial_print()

	if len(sys.argv) > 1:
		param_file_name, no_valid_flags = parse_sys_args(sys.argv)

		if not param_file_name and True in [x in sys.argv for x in ['-d', '--dev', '-xd', '--extra-dev']]:
			repl(True)

		cfg.source_file_name = param_file_name
		if os.path.isfile(f'{os.getcwd()}/{cfg.source_file_name}'):
			# Transpiles.
			with open(cfg.source_file_name) as f:
				source_lines = f.readlines()

			if not source_lines:
				printing.style_print('\t- The file is empty!', color='red')
				exit(1)

			transpiler.transpile(source_lines)

			if askfile.get(['system', 'server'], True):
				# Starts server
				serve_run.run_server()
			else:
				printing.style_print('\nAuto start server is turned OFF.', styles=['bold'])
				print('\t - The transpiled code can be found in:', end=' ')
				printing.style_print(askfile.get(['system', 'output_path'], 'app.py'), color='blue', end='')
				print('.')
		else:
			if no_valid_flags:
				printing.style_print('- The file could not be found!', color='red')
	else:
		repl(True)


if __name__ == '__main__':
	main()
