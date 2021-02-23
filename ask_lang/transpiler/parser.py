# coding=utf-8
from typing import List

from ask_lang import cfg
from ask_lang.transpiler.utilities import parser_utils, small_transpilers, transpiler_utils


def insert_basic_decorator_code_to_insert(parsed: str, ignored_db_vars: List[str]) -> str:
	parsed_lines_reversed = parsed.split('\n')[::-1]
	tab_count = 0
	line_to_place_code_at = 0
	code_lines = []

	# Inserts an id/primary key column if the model is missing one.
	if not cfg.basic_decorator_has_primary_key:
		code_lines.append('id = db.Column(db.Integer, primary_key=True)\n')
		cfg.basic_decorator_collector.insert(0, 'id')

	for line_index, line in enumerate(parsed_lines_reversed):
		if 'db.Column(' in line:
			tab_count = len(parser_utils.get_tab_count(line))
			line_to_place_code_at = line_index + 1
			break

	code_lines.append(f'def __init__(self, {", ".join(cfg.basic_decorator_collector)}):')

	for var in cfg.basic_decorator_collector:
		code_lines.append(f'\tself.{var} = {var}')

	code_lines.append('')
	code_lines.append('def s(self):')
	code_lines.append('\treturn {')

	for var_index, var in enumerate(ignored_db_vars + cfg.basic_decorator_collector):
		code_lines.append(f'\t\t\'{var}\': self.{var},')
	code_lines.append('\t}\n')

	tab_char = '\t'
	code = f'\n{tab_char * tab_count}'.join([line for line in code_lines])

	return '\n'.join(
		parsed_lines_reversed[line_to_place_code_at - 1:][::-1]
	) + f'\n\n{tab_char * tab_count}{code}' + '\n'.join(
		parsed_lines_reversed[:line_to_place_code_at - 1][::-1]
	)


def parse(tokens: List[List[str]]) -> str:
	parsed = ''

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

	for token_index, token in enumerate(tokens):
		if is_skip:
			is_skip = False
			continue

		token_type = token[0]
		token_val = token[1]

		if on_next_run_uses_basic_decorator:
			on_next_run_uses_basic_decorator = False
			cfg.uses_basic_decorator = True

		if cfg.uses_basic_decorator and transpiler_utils.token_check(token, 'FORMAT', '\n') and past_lines_tokens:
			if basic_decorator_collection_might_end:
				if past_lines_tokens == [['DEC', 'basic']]:
					on_next_run_uses_basic_decorator = True
					cfg.basic_decorator_collector = cfg.previous_basic_decorator_collector

				if not parser_utils.is_db_column_or_model_in_past_line(past_lines_tokens):
					basic_decorator_collection_might_end = False
					cfg.uses_basic_decorator = False

					parsed = insert_basic_decorator_code_to_insert(parsed, ignored_due_to_basic_decorator)
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
					parsed += '\n\treturn wrapper'
			elif token_val == 'start':
				indention_depth_counter += 1

		if token_type == 'FORMAT':
			if token_val == '\n' and add_parenthesis_at_en_of_line:
				parsed += ')'
				add_parenthesis_at_en_of_line = False

			parsed += token_val

			if transpiler_utils.token_check(token, 'FORMAT', '\n') and add_tabs_to_inner_group:
				parsed += '\t'
		elif token_type == 'NUM':
			parsed += f'{parser_utils.space_prefix(parsed, token_val)}{token_val}'
		elif token_type == 'OP':
			parsed += f'{parser_utils.space_prefix(parsed, token_val)}{token_val}'

			if needs_db_commit and token_val == ')':
				needs_db_commit = False

				tab_level = parser_utils.get_tab_count(parsed)
				parsed += f'\n{tab_level}db.session.commit()'
		elif token_type == 'STR':
			parsed += f'{parser_utils.space_prefix(parsed, token_val)}\"{token_val}\"'
		elif token_type == 'WORD':
			parsed += f'{parser_utils.space_prefix(parsed, token_val)}{small_transpilers.transpile_word(token_val)}'
		elif token_type == 'FUNC':
			if token_val[0] == '@':
				new_line = '\n'
				suffix = new_line

				if token_index > 2 and tokens[token_index - 2][0] == 'DEC':
					suffix = ''

				if token_index < len(tokens) and tokens[token_index + 1][0] == 'STR':
					next_token_val = tokens[token_index + 1][1]

					parsed += f'@app.route(\'{next_token_val}\', methods=[\'{token_val[1:]}\']){suffix}'
					cfg.uses_routes = True

					# Flask-selfdoc decorator
					parsed += f'{new_line if suffix == "" else ""}@auto.doc(\''
					default_doc_end = f'public\'){suffix}'

					if is_decorator:
						# Group type for the auto docs decorator. (private if the route is protected else public)
						if decorator == '\n@check_for_token':
							parsed += f'private\'){suffix}'
						else:
							parsed += default_doc_end

						parsed += decorator + '\n'
					else:
						parsed += default_doc_end

					parsed += ''.join([
						f'def {token_val[1:]}',
						f'{parser_utils.uri_to_func_name(next_token_val)}',
						f'({parser_utils.extract_params_from_uri(next_token_val)}'
					])

					is_skip = True
					is_decorator = False

			elif token_val in cfg.ask_library_methods:
				prefix = 'AskLibrary.'
				if token_val == 'respond':
					prefix = f'return {prefix}'
				parsed += f'{parser_utils.space_prefix(parsed, to_add=token_val)}{prefix}{token_val}('

			else:
				parsed += f'{parser_utils.space_prefix(parsed, to_add=token_val)}{small_transpilers.transpile_function(token_val)}'

				if token_val == 'status':
					add_parenthesis_at_en_of_line = True

		elif token_type == 'DB_MODEL':
			parsed += f'\nclass {token_val}(db.Model)'
		elif token_type == 'FUNC_DEF':
			parsed += f'def {token_val if token_val not in ["init", "_init"] else "__init__"}('
		elif token_type == 'DEC_DEF':
			parsed += f'def {token_val}(func):'
			parsed += f'\n\tdef wrapper(*args, **kwargs):'
			add_tabs_to_inner_group = True
		elif token_type == 'KEY':
			parsed += f'\'{token_val}\''
		elif token_type == 'DEC':
			decorator = small_transpilers.transpile_decorator(token_val)
			if not decorator:
				parsed += f'@{token_val}'

			if decorator != '---':
				is_decorator = True
		elif token_type == 'DB_ACTION':
			transpiled_action, needs_commit = small_transpilers.transpile_db_action(token_val)

			if cfg.uses_basic_decorator:
				if transpiled_action == 'primary_key=True':
					cfg.basic_decorator_has_primary_key = True

				if transpiled_action == 'ignored':
					ignored_due_to_basic_decorator.append(
						parser_utils.previous_non_keyword_word_tok(past_lines_tokens)
					)

				if transpiled_action == 'db.Column':
					cfg.basic_decorator_collector.append(
						parser_utils.previous_non_keyword_word_tok(past_lines_tokens)
					)

					for ignored in ignored_due_to_basic_decorator:
						if ignored in cfg.basic_decorator_collector:
							cfg.basic_decorator_collector.remove(ignored)

			if transpiled_action != 'ignored':
				parsed += f'{parser_utils.space_prefix(parsed, transpiled_action)}{transpiled_action}'
			if needs_commit:
				needs_db_commit = True

	return parsed


def parser(tokens_list: List[List[str]]) -> str:
	# Parses tokens and adds the end boilerplate to the output code.
	parsed = parse(tokens_list)

	# Put the output code into a main function if the app doesn't use routes, and prevent it from running multiple
	# times since the output file is imported multiple times.
	if not cfg.uses_routes:
		parsed_with_main_func = '\n\ndef main():\n'
		for line in parsed.split('\n'):
			parsed_with_main_func += f'\t{line}\n'
		parsed = parsed_with_main_func

	# Boilerplate setup.
	transpiler_utils.set_boilerplate()

	parsed = f'{cfg.flask_boilerplate}\n{parsed}'
	parsed += cfg.flask_end_boilerplate

	return parsed
