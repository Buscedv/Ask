# coding=utf-8

import os
import sys

from ask_lang import cfg
from ask_lang.transpiler import transpiler
from ask_lang.utilities import file_utils, utils, printing, askfile


def repl(first_time: bool = False):
	cfg.is_repl = True

	if first_time:
		printing.style_print('Type "q" to quit.', color='gray')

	line = input('Ask >>> ')

	# Quit/Exit
	if line == 'q':
		file_utils.maybe_delete_app(True)
		return

	transpiler.transpile([line])
	utils.run_server()

	repl()


def main():
	printing.initial_print()

	if len(sys.argv) > 1:
		param_file_name, no_valid_flags = utils.parse_sys_args(sys.argv)

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
				utils.run_server()
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
