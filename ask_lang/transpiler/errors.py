# coding=utf-8
import os
import difflib

from ask_lang import cfg
from ask_lang.utilities import utils
from ask_lang.utilities import file_utils


def parse_and_print_error(err: dict):
	# This function tries to figure out on which line the error is coming from.
	# This is complicated since the error is coming from the transpiled code and not the source code.

	matches = []
	skip_to_printing = False

	message = ''
	code = ''
	line_nr = 0

	if err['msg'] == 48:
		# Address already in use eror:
		message = 'Address already in use.'
		skip_to_printing = True

	if not skip_to_printing:
		try:
			message = err['msg'].capitalize()
		except AttributeError:
			message = err['msg']

		transpiled_line_nr = err['line']
		code = err['code'].replace('\t', '')

		line_nr = None

		# Looks for the most similar line in the Ask code.
		with open(cfg.source_file_name, 'r') as f:
			raw_lines = f.readlines()

		matches = list(difflib.get_close_matches(code, raw_lines))

		if cfg.is_dev:
			# Prints out the "real" line number.
			utils.style_print('\t- DEV: ', color='blue', end=' ')
			print(f'{message} on line: {transpiled_line_nr} in: {file_utils.get_output_file_destination_path()}')

	# No matching line was found, this most likely means that it's not a syntax error.
	if skip_to_printing or not matches:
		utils.style_print('\t- Error!', color='red', end=' ')
		print('Something went wrong!')
		print(f'\t\t- {message}')

		return

	# Gets the correct line number.
	for line_index, line in enumerate(raw_lines):
		if line == str(matches[0]):
			line_nr = line_index
			break

	# Prints out a customized error message based on the original.
	# Format: Error! ([file name]) [message] on line [nr] [\n] - in/at: [error line code].
	utils.style_print('\t- Error!', color='red', end=' ')
	utils.style_print(f'({cfg.source_file_name})', color='gray', end=' ')
	utils.style_print(message, styles=['bold'], end=' ')
	print('on line', end=' ')
	utils.style_print(f'{line_nr},', color='blue')
	print('\t\t- in/at: ', end='')
	utils.style_print(code, styles=['bold'])


def error_while_running(e: Exception, source_lines: list, time_result: float):
	# Catches e.g. syntax errors.
	try:
		msg, data = e.args
		_, line, _, code = data
	except ValueError:
		msg = e.args[0]
		line = ''
		code = ''

	# Prints out the error.
	# Clears the screen and re-prints the transpilation result.
	os.system('cls' if os.name == 'nt' else 'clear')

	utils.initial_print()
	utils.style_print('Transpiling...', styles=['bold'], end='')
	print('\t❌ ')
	utils.print_transpilation_result(source_lines, time_result, True)

	parse_and_print_error({
		'msg': msg,
		'line': line,
		'code': code
	})
