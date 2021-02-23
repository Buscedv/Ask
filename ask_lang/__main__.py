# coding=utf-8

import os
import sys

from ask_lang import cfg
from ask_lang.transpiler import transpiler
from ask_lang.utilities import utils


def main():
	utils.initial_print()

	if len(sys.argv) > 1:
		param_file_name, no_valid_flags = utils.parse_sys_args(sys.argv)

		cfg.source_file_name = param_file_name
		if os.path.isfile(f'{os.getcwd()}/{cfg.source_file_name}'):
			# Transpiles.
			with open(cfg.source_file_name) as f:
				source_lines = f.readlines()

			transpiler.transpile(source_lines)

			# Starts server
			utils.run_server()
		else:
			if no_valid_flags:
				utils.style_print('- The file could not be found!', color='red')
	else:
		# TODO: Launch Repl.
		utils.style_print('- Please provide a script file!', color='red')


if __name__ == '__main__':
	main()

