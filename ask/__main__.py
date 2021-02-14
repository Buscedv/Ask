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

from ask import cfg, errors, lexer, parser
from ask.utilities import file_utils, utils, transpiler_utils


def run_app(source_lines, time_result):
	try:
		# Imports app.py for two reasons:
		# 1. To catch syntax errors.
		# 2. To load the database (if it's used).
		from importlib.machinery import SourceFileLoader
		app = SourceFileLoader("app", file_utils.get_output_file_destination_path()).load_module()

		if cfg.uses_db:
			utils.style_print('Loading database...', styles=['bold'], end='')
			app.db.create_all()
			print('\t✅')

		# TODO: ALso support running the app in a production ready server.
		utils.style_print('Running Flask app:', styles=['bold'])
		os.environ['FLASK_APP'] = file_utils.get_output_file_destination_path()
		if cfg.is_dev:
			os.environ['FLASK_ENV'] = 'development'

		# Starts the server.

		app.app.run()
	except Exception as e:
		errors.error_while_running(e, source_lines, time_result)


def transpile(file_name):
	import time

	# Transpilation time capture start.
	start_time = time.time()

	utils.style_print('Transpiling...', styles=['bold'], end='')

	# Boilerplate setup.
	transpiler_utils.set_boilerplate()

	# Lexing.
	with open(file_name) as f:
		source_lines = f.readlines()
	tokens_list = lexer.lex(source_lines)

	if tokens_list:
		# Parsing.
		parsed = parser.parse(tokens_list)

		# Saves the transpiled code to the build/output file
		with open(file_utils.get_output_file_destination_path(), 'w+') as f:
			f.write('')
			f.write(parsed)

		# The transpilation is done.
		end_time = time.time()
		time_result = round(end_time - start_time, 3)
		# Checkmark for the 'Transpiling...' message at the start of this function.
		print('\t✅')
		utils.print_transpilation_result(source_lines, time_result)

		# Database setup & build.
		transpiler_utils.build_db(file_name)

		# Runs the app.
		run_app(source_lines, time_result)
	else:
		utils.style_print('\t- The file is empty!', color='red')


def main():
	utils.initial_print()

	# DEV mode activation, (-d) flag.
	if len(sys.argv) > 1:
		utils.set_dev_status()

		cfg.source_file_name = sys.argv[1]
		if os.path.isfile(f'{os.getcwd()}/{cfg.source_file_name}'):
			cfg.ask_config = file_utils.get_ask_config(file_utils.get_root_from_file_path(cfg.source_file_name))

			transpile(cfg.source_file_name)
		else:
			utils.style_print('- The file could not be found!', color='red')
	else:
		utils.style_print('- Please provide a script file!', color='red')


if __name__ == '__main__':
	main()
