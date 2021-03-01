# coding=utf-8
import os
from pprint import pprint
import time
from types import ModuleType
from typing import List

from ask_lang import cfg
from ask_lang.transpiler import lexer, translator, errors
from ask_lang.utilities import askfile, file_utils, printing, utils


def verify_and_load_db(source_lines: list, time_result: float):  # sourcery skip: move-assign
	try:
		# Imports app.py for two reasons:
		# 1. To catch syntax errors.
		# 2. To load the database (if it's used).
		app: ModuleType = utils.import_app()

		if cfg.uses_db:
			print('\t- Loading database...', end='')
			app.db.create_all()
			print('\t✅')
	except Exception as e:  # Exception is used here to capture all exception types.
		errors.error_while_running(e, source_lines, time_result)

		exit(1)


def build_db(file_name: str):
	if not cfg.uses_db:
		return

	printing.style_print('Database:', styles=['bold'])

	if not askfile.get(['db', 'custom'], False) and not os.path.exists(file_utils.get_db_file_path()):
		print('\t- Building database...', end='')
		db_root = file_utils.get_root_from_file_path(file_utils.get_db_file_path())
		print('\t✅')

		if db_root and db_root != file_name and not os.path.exists(db_root):
			print('\t- Building Folder Structure...', end='')
			os.makedirs(db_root)
			print('\t✅')


def transpile(source_lines: List[str]):
	# Transpilation time capture start.
	start_time = time.time()

	if not cfg.is_repl:
		printing.style_print('Transpiling...', styles=['bold'], end='')

	# Load Askfile.
	askfile.load()

	# Lexing.
	tokens_list = lexer.lexer(source_lines)

	# Parsing.
	translated = translator.translator(tokens_list)

	# Saves the transpiled code to the build/output file
	with open(file_utils.output_file_path(), 'w+') as f:
		f.write('')
		f.write(translated)

	# The transpilation is done.
	end_time = time.time()
	time_result = round(end_time - start_time, 3)

	if not cfg.is_repl:
		# Checkmark for the 'Transpiling...' message at the start of this function.
		print('\t✅')

	if cfg.is_dev:
		pprint(tokens_list)

	if not cfg.is_repl:
		printing.transpilation_result(source_lines, time_result)

	# Database setup & build.
	build_db(cfg.source_file_name)

	# Verify transpilation
	verify_and_load_db(source_lines, time_result)

	# Stores the result in the global store.
	cfg.transpilation_result = {
		'source_lines': source_lines,
		'time_result': time_result
	}
