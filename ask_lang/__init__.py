# coding=utf-8

# Ask 1.0.0
# Copyright 2020, 2021 Edvard Busck-Nielsen
#
#     Ask is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     Ask is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with Ask.  If not, see <https://www.gnu.org/licenses/>.

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

