from ask import cfg
from ask.transpiler.utilities import parser_utils, translators


def parser(tokens):
	is_skip = False
	needs_db_commit = False
	is_decorator = False
	add_tabs_to_inner_group = False
	indention_depth_counter = 0
	decorator = ''
	add_parenthesis_at_en_of_line = False
	basic_decorator_collection_might_end = False
	on_next_run_uses_basic_decorator = False
	parsed = ''
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

		if cfg.uses_basic_decorator and token_type == 'FORMAT' and token_val == '\n' and past_lines_tokens:
			if basic_decorator_collection_might_end:
				if past_lines_tokens == [['DEC', 'basic']]:
					on_next_run_uses_basic_decorator = True
					cfg.basic_decorator_collector = cfg.previous_basic_decorator_collector

				if not parser_utils.is_db_column_in_past_line(past_lines_tokens):
					basic_decorator_collection_might_end = False
					cfg.uses_basic_decorator = False

					parsed = parser_utils.insert_basic_decorator_code_to_insert(parsed, ignored_due_to_basic_decorator)
					cfg.basic_decorator_collector = []
					ignored_due_to_basic_decorator = []
			else:
				basic_decorator_collection_might_end = True

		if token_type == 'FORMAT' and token_val == '\n':
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

		if token_type in ['FORMAT', 'ASSIGN', 'NUM']:
			if token_val == '\n' and add_parenthesis_at_en_of_line:
				parsed += ')'
				add_parenthesis_at_en_of_line = False
			parsed += token_val
			if token_type == 'FORMAT' and token_val == '\n' and add_tabs_to_inner_group:
				parsed += '\t'
		elif token_type == 'OP':
			if token_val in ['.', ')', ',', ':'] and parsed and parsed[-1] == ' ':
				parsed = parsed[:-1]

			parsed += token_val

			if token_val in [',', '=']:
				parsed += ' '

			if needs_db_commit and token_val == ')':
				needs_db_commit = False

				tab_level = parser_utils.get_current_tab_level(parsed)
				parsed += '\n' + tab_level + 'db.session.commit()'
		elif token_type == 'STR':
			parsed += f'\"{token_val}\"'
		elif token_type == 'KEYWORD':
			parsed = parser_utils.maybe_place_space_before(parsed, token_val)
		elif token_type == 'VAR':
			if token_val not in cfg.built_in_vars and token_index > 0:
				parsed = parser_utils.maybe_place_space_before(parsed, token_val)
			else:
				parsed += translators.transpile_var(token_val)
		elif token_type == 'FUNC':
			if token_val[0] == '@':
				new_line = '\n'
				suffix = new_line

				if token_index > 2 and tokens[token_index - 2][0] == 'DEC':
					suffix = ''

				if token_index < len(tokens) and tokens[token_index + 1][0] == 'STR':
					next_token_val = tokens[token_index + 1][1]

					parsed += f'@app.route(\'{next_token_val}\', methods=[\'{token_val[1:]}\']){suffix}'

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

					parsed += f'def {token_val[1:]}{parser_utils.route_path_to_func_name(next_token_val)}({parser_utils.parse_route_params_str(next_token_val)}'
					is_skip = True
					is_decorator = False
			elif token_val in cfg.ask_library_methods:
				prefix = 'AskLibrary.'
				if token_val == 'respond':
					prefix = f'return {prefix}'
				parsed += f'{prefix}{token_val}('
			elif token_val == 'status':
				parsed += translators.transpile_function(token_val)
				add_parenthesis_at_en_of_line = True
			else:
				parsed += translators.transpile_function(token_val)
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
			decorator = translators.transpile_decorator(token_val)
			if not decorator:
				parsed += f'@{token_val}'

			if decorator != '---':
				is_decorator = True
		elif token_type == 'DB_ACTION':
			transpiled = translators.transpile_db_action(token_val)

			if cfg.uses_basic_decorator:
				if transpiled[0] in ['primary_key=True', 'ignored']:
					ignored_due_to_basic_decorator.append(
						parser_utils.get_first_variable_token_value_of_line(past_lines_tokens))

				if transpiled[0] == 'db.Column':
					var = parser_utils.get_first_variable_token_value_of_line(past_lines_tokens)
					cfg.basic_decorator_collector.append(var)

					for ignored in ignored_due_to_basic_decorator:
						if ignored in cfg.basic_decorator_collector:
							cfg.basic_decorator_collector.remove(ignored)

			if transpiled[0] != 'ignored':
				parsed += transpiled[0]
			if transpiled[1]:
				needs_db_commit = True

		if len(parsed) > 3 and parsed[-1] == ' ' and parsed[-2] == '=' and parsed[-3] == ' ' and parsed[-4] == '=':
			parsed = parsed[:-4]
			parsed += ' == '

	return parsed


def parse(tokens_list):
	# Parses tokens and adds the end boilerplate to the output code.
	parsed = parser(tokens_list)
	parsed = f'{cfg.flask_boilerplate}\n{parsed}'
	parsed += cfg.flask_end_boilerplate

	return parsed
