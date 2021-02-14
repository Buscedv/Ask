def is_db_column_in_past_line(tokens):
	for token in tokens[::-1]:
		token_type = token[0]
		token_val = token[1]

		if token_type == 'FORMAT' and token_val == '\n':
			break

		if token_type == 'DB_ACTION' and token_val == 'col' or token_type == 'DB_MODEL':
			return True

	return False


def get_first_variable_token_value_of_line(tokens):
	for token in tokens:
		token_type = token[0]
		if token_type == 'VAR':
			# Returns the token value
			return token[1]

	return None


def route_path_to_func_name(route_str):
	return route_str.replace('/', '_').replace('<', '_').replace('>', '_').replace('-', '_')


def maybe_place_space_before(parsed, token_val):
	prefix = ' '

	if parsed and parsed[-1] in ['\n', '\t', '(', ' ', '.']:
		prefix = ''
	parsed += f'{prefix}{token_val} '

	return parsed


def parse_route_params_str(route_path):
	is_param = False
	tmp = ''
	params_str = ''

	for char in route_path:
		if char == '<':
			tmp = ''
			is_param = True
		elif char == '>':
			is_param = False
			if tmp:
				params_str += f'{tmp}, '
				tmp = ''
		elif is_param and char not in [' ' + '\t', '\n']:
			tmp += char

	if len(params_str) > 2 and params_str[-2:] == ', ':
		params_str = params_str[:-2]

	return params_str


def get_current_tab_level(parsed):
	parsed = parsed[::-1]

	indents = ''
	for char in parsed:
		if char == '\t':
			indents += char
		elif char == '\n':
			break

	return indents
