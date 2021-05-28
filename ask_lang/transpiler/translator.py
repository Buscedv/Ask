# coding=utf-8
from typing import List
from re import findall

from ask_lang import cfg
from ask_lang.transpiler.utilities import translator_utils, small_transpilers, transpiler_utils
from ask_lang.transpiler.utilities.translator_utils import include_module


def prepare_init_vars(vars: list, ignored: List[str]) -> list:
	return [var for var in vars if var not in ignored]


def insert_basic_decorator_code_to_insert(translated: str, ignored_db_vars: List[str]) -> str:
	translated_lines_reversed = translated.split('\n')[::-1]
	tab_count = 0
	line_to_place_code_at = 0
	code_lines = []

	# Inserts an id/primary key column if the model is missing one.
	if not cfg.basic_decorator_has_primary_key:
		code_lines.append('id = db.Column(db.Integer, primary_key=True)\n')
		cfg.basic_decorator_collector.insert(0, 'id')
		ignored_db_vars.append('id')

	for line_index, line in enumerate(translated_lines_reversed):
		if 'db.Column(' in line:
			tab_count = len(translator_utils.get_tab_count(line))
			line_to_place_code_at = line_index + 1
			break

	code_lines.append(f'def __init__(self, {", ".join(prepare_init_vars(cfg.basic_decorator_collector, ignored_db_vars))}):')

	for var in prepare_init_vars(cfg.basic_decorator_collector, ignored_db_vars):
		code_lines.append(f'\tself.{var} = {var}')

	code_lines.append('')
	code_lines.append('def s(self):')
	code_lines.append('\treturn {')

	for var_index, var in enumerate(ignored_db_vars + prepare_init_vars(cfg.basic_decorator_collector, ignored_db_vars)):
		code_lines.append(f'\t\t\'{var}\': self.{var},')
	code_lines.append('\t}\n')

	tab_char = '\t'
	code = f'\n{tab_char * tab_count}'.join([line for line in code_lines])

	return '\n'.join(
		translated_lines_reversed[line_to_place_code_at - 1:][::-1]
	) + f'\n\n{tab_char * tab_count}{code}' + '\n'.join(
		translated_lines_reversed[:line_to_place_code_at - 1][::-1]
	)


def translate(tokens: List[List[str]]) -> str:
	translated = ''

	is_skip = False
	needs_db_commit = False
	is_decorator = False
	add_tabs_to_inner_group = False
	indention_depth_counter = 0
	decorator = ''
	add_parenthesis_at_en_of_line = False
	basic_decorator_collection_might_end = False
	on_next_run_uses_basic_decorator = False
	past_lines_tokens = []
	ignored_due_to_basic_decorator = []
	is_import = False
	is_include = False
	included_module_name = ''

	for token_index, token in enumerate(tokens):
		if is_skip:
			is_skip = False
			continue

		token_type = token[0]
		token_val = token[1]

		# Used when "postponing" the setting of uses_basic_decorator to true.
		if on_next_run_uses_basic_decorator:
			on_next_run_uses_basic_decorator = False
			cfg.uses_basic_decorator = True

		if cfg.uses_basic_decorator and transpiler_utils.token_check(token, 'FORMAT', '\n') and past_lines_tokens:
			if basic_decorator_collection_might_end:
				if past_lines_tokens == [['DEC', 'basic']]:
					on_next_run_uses_basic_decorator = True
					cfg.basic_decorator_collector = cfg.previous_basic_decorator_collector

				if not translator_utils.is_db_column_or_model_in_past_line(past_lines_tokens):
					translated = insert_basic_decorator_code_to_insert(translated, ignored_due_to_basic_decorator)

					# Re-setting to defaults.
					basic_decorator_collection_might_end = False
					cfg.uses_basic_decorator = False
					cfg.basic_decorator_collector = []
					ignored_due_to_basic_decorator = []
					cfg.basic_decorator_has_primary_key = False
			else:
				basic_decorator_collection_might_end = True

		if transpiler_utils.token_check(token, 'FORMAT', '\n'):
			past_lines_tokens = []
		else:
			past_lines_tokens.append(token)

		if add_tabs_to_inner_group and token_type == 'GROUP':
			if token_val == 'end':
				indention_depth_counter -= 1

				if indention_depth_counter == 0:
					add_tabs_to_inner_group = False
					translated += '\n\treturn wrapper'
			elif token_val == 'start':
				indention_depth_counter += 1

		if token_type == 'FORMAT':
			if token_val == '\n' and is_include:
				is_include = False
				cfg.included_module_code += include_module(included_module_name)
				included_module_name = ''

				continue

			if token_val == '\n' and add_parenthesis_at_en_of_line:
				translated += ')'
				add_parenthesis_at_en_of_line = False

			translated += token_val

			if transpiler_utils.token_check(token, 'FORMAT', '\n') and add_tabs_to_inner_group:
				translated += '\t'
		elif token_type == 'NUM':
			translated += f'{translator_utils.space_prefix(translated, token_val)}{token_val}'
		elif token_type == 'OP':
			if is_include:
				included_module_name += token_val
				continue

			translated += f'{translator_utils.space_prefix(translated, token_val)}{token_val}'

			if needs_db_commit and token_val == ')':
				needs_db_commit = False

				tab_level = translator_utils.get_tab_count(translated)
				translated += f'\n{tab_level}db.session.commit()'
		elif token_type == 'STR':
			translated += f'{translator_utils.space_prefix(translated, token_val)}{token_val}'
		elif token_type == 'WORD':
			if is_include:
				included_module_name += token_val
				continue

			if is_import:
				is_import = False
				to_append, _ = translator_utils.might_be_ask_import(token_val)
				if to_append:
					for line in to_append:
						translated += f'{translator_utils.space_prefix(translated, token_val)}{line}\n'

				continue

			if token_val == 'extend':
				is_import = True
				continue
			elif token_val == 'include':
				is_include = True
				included_module_name = ''
				continue

			translated += f'{translator_utils.space_prefix(translated, token_val)}{small_transpilers.transpile_word(token_val, translated)}'
		elif token_type == 'FUNC':
			if token_val[0] == '@':
				new_line = '\n'
				suffix = new_line

				if token_index > 2 and tokens[token_index - 2][0] == 'DEC':
					suffix = ''

				if token_index < len(tokens) and tokens[token_index + 1][0] == 'STR':
					next_token_val = tokens[token_index + 1][1]

					translated += f'@app.route({next_token_val}, methods=[\'{token_val[1:]}\']){suffix}'
					cfg.uses_routes = True

					# Flask-selfdoc decorator
					translated += f'{new_line if suffix == "" else ""}@auto.doc(\''
					default_doc_end = f'public\'){suffix}'

					if is_decorator:
						# Group type for the auto docs decorator. (private if the route is protected else public)
						if decorator == '\n@check_for_token':
							translated += f'private\'){suffix}'
						else:
							translated += default_doc_end

						translated += decorator + '\n'
					else:
						translated += default_doc_end

					translated += ''.join([
						f'def {token_val[1:]}',
						f'{translator_utils.uri_to_func_name(next_token_val)}',
						f'({translator_utils.extract_params_from_uri(next_token_val)}'
					])

					is_skip = True
					is_decorator = False

			elif token_val in cfg.ask_library_methods:
				prefix = 'AskLibrary.'
				if token_val == 'respond':
					prefix = f'return {prefix}'
				translated += f'{translator_utils.space_prefix(translated, to_add=token_val)}{prefix}{token_val}('

			else:
				translated += f'{translator_utils.space_prefix(translated, to_add=token_val)}{small_transpilers.transpile_function(token_val)}'

				if token_val == 'status':
					add_parenthesis_at_en_of_line = True

		elif token_type == 'DB_MODEL':
			translated += f'\nclass {token_val}(db.Model)'
		elif token_type == 'FUNC_DEF':
			translated += f'def {token_val if token_val not in ["init", "_init"] else "__init__"}('
		elif token_type == 'DEC_DEF':
			translated += f'def {token_val}(func):'
			translated += f'\n\tdef wrapper(*args, **kwargs):'
			add_tabs_to_inner_group = True
		elif token_type == 'KEY':
			translated += f'\'{token_val}\''
		elif token_type == 'DEC':
			decorator = small_transpilers.transpile_decorator(token_val)
			if not decorator:
				translated += f'@{token_val}'

			if decorator != '---':
				is_decorator = True
		elif token_type == 'DB_ACTION':
			transpiled_action, needs_commit = small_transpilers.transpile_db_action(token_val)

			if cfg.uses_basic_decorator:
				if transpiled_action == 'primary_key=True':
					cfg.basic_decorator_has_primary_key = True

				if transpiled_action == 'ignored':
					ignored_due_to_basic_decorator.append(
						translator_utils.previous_non_keyword_word_tok(past_lines_tokens)
					)

				if transpiled_action == 'db.Column':
					cfg.basic_decorator_collector.append(
						translator_utils.previous_non_keyword_word_tok(past_lines_tokens)
					)

					for ignored in ignored_due_to_basic_decorator:
						if ignored in cfg.basic_decorator_collector:
							cfg.basic_decorator_collector.remove(ignored)

			if transpiled_action != 'ignored':
				translated += f'{translator_utils.space_prefix(translated, transpiled_action)}{transpiled_action}'
			if needs_commit:
				needs_db_commit = True

	return translated


def translator(tokens_list: List[List[str]]) -> str:
	# Translates tokens and adds the end boilerplate to the output code.
	translated = translate(tokens_list)

	if not cfg.is_repl:
		# Boilerplate setup.
		transpiler_utils.set_boilerplate()

	# Put the output code into a main function if the app doesn't use routes, and prevent it from running multiple
	# times since the output file is imported multiple times.
	if not cfg.uses_routes and not cfg.is_module_transpile:
		translated_with_main_func = '\n\ndef main():\n'

		if cfg.is_repl and cfg.repl_previous_transpiled:
			for line in cfg.repl_previous_transpiled.split('\n'):
				if bool(findall(r'^[\t\s]*[\w]+[\s]*=[\s]*.+', line)):
					translated_with_main_func += f'\t{line}\n'

		# Insert included modules.
		if cfg.included_module_code:
			for line in cfg.included_module_code.split('\n'):
				translated_with_main_func += f'\t{line}\n'

		# Insert "main" transpiled lines.
		for line in translated.split('\n'):
			translated_with_main_func += f'\t{line}\n'

		if cfg.is_repl:
			cfg.repl_previous_transpiled += f'\n{translated}'

		translated = translated_with_main_func
	elif cfg.included_module_code:
		translated = f'{cfg.included_module_code}\n{translated}'

	translated = f'{cfg.flask_boilerplate}\n{translated}'

	translated += cfg.flask_end_boilerplate

	return translated
