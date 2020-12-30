import unittest
import ask


class TestAsk(unittest.TestCase):
	# get_root_from_file_path
	def test_get_root_from_file_path(self):
		file_path = '/folder/folder/file.txt'
		self.assertEqual('/folder/folder', ask.get_root_from_file_path(file_path))

	# route_path_to_func_name
	def test_route_path_to_func_name_path(self):
		test_value = '/path'
		expected = '_path'
		self.assertEqual(expected, ask.route_path_to_func_name(test_value))

	def test_route_path_to_func_name_path_subpath(self):
		test_value = '/path/subpath'
		expected = '_path_subpath'
		self.assertEqual(expected, ask.route_path_to_func_name(test_value))

	def test_route_path_to_func_name_path_subpath_slash(self):
		test_value = '/path/subpath/'
		expected = '_path_subpath_'
		self.assertEqual(expected, ask.route_path_to_func_name(test_value))

	def test_route_path_to_func_name_path_dash_path(self):
		test_value = '/path-path'
		expected = '_path_path'
		self.assertEqual(expected, ask.route_path_to_func_name(test_value))

	def test_route_path_to_func_name_path_char(self):
		test_value = '/path/<path>'
		expected = '_path__path_'
		self.assertEqual(expected, ask.route_path_to_func_name(test_value))

	def test_route_path_to_func_name_path_slash_dash_path(self):
		test_value = '/path/-path'
		expected = '_path__path'
		self.assertEqual(expected, ask.route_path_to_func_name(test_value))

	# maybe_place_space_before
	def test_maybe_place_space_before(self):
		token_val = '%'
		test_value = '' 
		expected = ' % '
		self.assertEqual(expected, ask.maybe_place_space_before(test_value, token_val))

	def test_maybe_place_space_before(self):
		token_val = '%'
		test_value = 'string' 
		expected = 'string % '
		self.assertEqual(expected, ask.maybe_place_space_before(test_value, token_val))

	def test_maybe_place_space_before(self):
		token_val = '%'
		test_value = 'string\n' 
		expected = 'string\n% '
		self.assertEqual(expected, ask.maybe_place_space_before(test_value, token_val))

	def test_maybe_place_space_before(self):
		token_val = '%'
		test_value = 'string\t' 
		expected = 'string\t% '
		self.assertEqual(expected, ask.maybe_place_space_before(test_value, token_val))

	def test_maybe_place_space_before(self):
		token_val = '%'
		test_value = 'string(' 
		expected = 'string(% '
		self.assertEqual(expected, ask.maybe_place_space_before(test_value, token_val))

	def test_maybe_place_space_before(self):
		token_val = '%'
		test_value = 'string ' 
		expected = 'string % '
		self.assertEqual(expected, ask.maybe_place_space_before(test_value, token_val))

	def test_maybe_place_space_before(self):
		token_val = '%'
		test_value = 'string.' 
		expected = 'string.% '
		self.assertEqual(expected, ask.maybe_place_space_before(test_value, token_val))

	# parse_route_params_str
	def test_parse_route_params_str_empty_string(self):
		test_value = ''
		expected = ''
		self.assertEqual(expected, ask.parse_route_params_str(test_value))

	def test_parse_route_params_str_no_parameter(self):
		test_value = 'no parameter given'
		expected = ''
		self.assertEqual(expected, ask.parse_route_params_str(test_value))

	def test_parse_route_params_str_one_parameter(self):
		test_value = '<param>'
		expected = 'param'
		self.assertEqual(expected, ask.parse_route_params_str(test_value))

	def test_parse_route_params_str_two_parameters(self):
		test_value = '<param1> and <param2>'
		expected = 'param1, param2'
		self.assertEqual(expected, ask.parse_route_params_str(test_value))

	def test_parse_route_params_str_param_with_line_break(self):
		test_value = 'string and <param\n>'
		expected = 'param'
		self.assertEqual(expected, ask.parse_route_params_str(test_value))

	def test_parse_route_params_str_opened_not_closed(self):
		test_value = '<param'
		expected = ''
		self.assertEqual(expected, ask.parse_route_params_str(test_value))

	def test_parse_route_params_str_closed_not_opened(self):
		test_value = 'param>'
		expected = ''
		self.assertEqual(expected, ask.parse_route_params_str(test_value))

	def test_parse_route_params_str_empty_param(self):
		test_value = '<>'
		expected = ''
		self.assertEqual(expected, ask.parse_route_params_str(test_value))

	def test_parse_route_params_str_param_in_param(self):
		test_value = '<par<param>ram>'
		expected = 'param'
		self.assertEqual(expected, ask.parse_route_params_str(test_value))

	# get_current_tab_level
	def test_get_current_tab_level_empty_string(self):
		test_value = ''
		expected = ''
		self.assertEqual(expected, ask.get_current_tab_level(test_value))

	def test_get_current_tab_level_one_tab(self):
		test_value = '\t'
		expected = '\t'
		self.assertEqual(expected, ask.get_current_tab_level(test_value))

	def test_get_current_tab_level_two_tabs(self):
		test_value = '\t\t'
		expected = '\t\t'
		self.assertEqual(expected, ask.get_current_tab_level(test_value))

	def test_get_current_tab_level_three_tabs(self):
		test_value = '\t\t\t'
		expected = '\t\t\t'
		self.assertEqual(expected, ask.get_current_tab_level(test_value))

	def test_get_current_tab_level_tab_after_string(self):
		test_value = 'parsed string\t'
		expected = '\t'
		self.assertEqual(expected, ask.get_current_tab_level(test_value))

	def test_get_current_tab_level_tab_in_string(self):
		test_value = 'parsed \t string'
		expected = '\t'
		self.assertEqual(expected, ask.get_current_tab_level(test_value))

	def test_get_current_tab_level_newline(self):
		test_value = '\n'
		expected = ''
		self.assertEqual(expected, ask.get_current_tab_level(test_value))

	def test_get_current_tab_level_newline_then_tab(self):
		test_value = '\n\t'
		expected = '\t'
		self.assertEqual(expected, ask.get_current_tab_level(test_value))
		
	def test_get_current_tab_level_tab_then_newline_then_tab(self):
		test_value = 'parsed \t string \n \t'
		expected = '\t'
		self.assertEqual(expected, ask.get_current_tab_level(test_value))

	# tokens_grouped_by_lines
	def test_tokens_grouped_by_lines(self):
		tokens = [
			['VAR', 'variable'],
			['FORMAT', '\n'],
			['VAR', 'variable'],
			['FORMAT', '\n'],
			['FORMAT', '\t'],
			['VAR', 'variable'],
			['FORMAT', '\n'],
			['FORMAT', '\t'],
			['FORMAT', '\t'],
			['VAR', 'variable'],
		]

		expected = [
			[
				['VAR', 'variable'],
			],
			[
				['FORMAT', '\n'],
				['VAR', 'variable'],
			],
			[
				['FORMAT', '\n'],
				['FORMAT', '\t'],
				['VAR', 'variable'],
			],
			[
				['FORMAT', '\n'],
				['FORMAT', '\t'],
				['FORMAT', '\t'],
				['VAR', 'variable'],
			],
		]

		self.assertEqual(expected, ask.tokens_grouped_by_lines(tokens))

	# insert_indentation_group_markers
	def test_insert_indention_group_markers(self):
		tokens = [
			['FUNC_DEF', 'function'],
			['FORMAT', '\n'],
			['FORMAT', '\t'],
			['FUNC', 'print'],
			['STR', 'text'],
			['OP', ')'],
			['FORMAT', '\n'],
			['FORMAT', '\t'],
			['KEYWORD', 'if'],
			['VAR', 'var'],
			['OP', ':'],
			['FORMAT', '\n'],
			['FORMAT', '\t'],
			['FORMAT', '\t'],
			['FUNC', 'print'],
			['STR', 'text'],
			['OP', ')'],
			['FORMAT', '\n'],
			['FORMAT', '\t'],
			['FUNC', 'print'],
			['STR', 'text'],
			['OP', ')'],
		]

		expected = [
			['GROUP', 'start'],
			['FUNC_DEF', 'function'],
			['GROUP', 'start'],
			['FORMAT', '\n'],
			['FORMAT', '\t'],
			['FUNC', 'print'],
			['STR', 'text'],
			['OP', ')'],
			['FORMAT', '\n'],
			['FORMAT', '\t'],
			['KEYWORD', 'if'],
			['VAR', 'var'],
			['OP', ':'],
			['GROUP', 'start'],
			['FORMAT', '\n'],
			['FORMAT', '\t'],
			['FORMAT', '\t'],
			['FUNC', 'print'],
			['STR', 'text'],
			['OP', ')'],
			['GROUP', 'end'],
			['FORMAT', '\n'],
			['FORMAT', '\t'],
			['FUNC', 'print'],
			['STR', 'text'],
			['OP', ')'],
			['GROUP', 'end'],
			['GROUP', 'end']
		]

		self.assertEqual(expected, ask.insert_indention_group_markers(tokens))

	# add_part
	def test_add_part_string_true_code_with_newline(self):
		is_string = True
		code = 'code \n'
		expected = (
			[{'is_string': True, 'code': code}],
			'',
			False
		)
		self.assertEqual(expected, ask.add_part([],is_string, code))

	def test_add_part_string_true_code_without_newline(self):
		is_string = True
		code = 'code'
		expected = (
			[{'is_string': True, 'code': code}],
			'',
			True
		)
		self.assertEqual(expected, ask.add_part([],is_string, code))

	def test_add_part_string_false_code_with_newline(self):
		is_string = False
		code = 'code \n'
		expected = (
			[{'is_string': False, 'code': code}],
			'',
			False
		)
		self.assertEqual(expected, ask.add_part([],is_string, code))

	def test_add_part_string_false_code_without_newline(self):
		is_string = False
		code = 'code'
		expected = (
			[{'is_string': False, 'code': code}],
			'',
			True
		)
		self.assertEqual(expected, ask.add_part([],is_string, code))

	# transpile_var()
	def test_transpile_var_body(self):
		var = '_body'
		expected = 'request.json'
		self.assertEqual(expected, ask.transpile_var(var))

	def test_transpile_var_form(self):
		var = '_form'
		expected = 'request.form'
		self.assertEqual(expected, ask.transpile_var(var))

	def test_transpile_var_args(self):
		var = '_args'
		expected = 'request.args'
		self.assertEqual(expected, ask.transpile_var(var))

	def test_transpile_var_req(self):
		var = '_req'
		expected = 'AskLibrary.get_all_req()'
		self.assertEqual(expected, ask.transpile_var(var))

	def test_transpile_var_datetime(self):
		var = '_datetime'
		expected = 'datetime.datetime'
		self.assertEqual(expected, ask.transpile_var(var))

	def test_transpile_var_keyError(self):
		expected = var = 'keyError'
		self.assertEqual(expected, ask.transpile_var(var))

	# transpile_keyword()
	# transpile_decorator()
	# transpile_db_action()


if __name__ == '__main__':
	unittest.main()
