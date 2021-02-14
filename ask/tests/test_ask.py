import unittest


class TestAsk(unittest.TestCase):
	# get_root_from_file_path
	def test_get_root_from_file_path(self):
		file_path = '/folder/folder/file.txt'
		self.assertEqual('/folder/folder', ask.get_root_from_file_path(file_path))

	# route_path_to_func_name
	def test_route_path_to_func_name(self):
		tests = {
			'/foo/bar': '_foo_bar',
			'/foo-bar': '_foo_bar',
			'/foo/<bar>': '_foo__bar_',
		}

		for test in tests:
			self.assertEqual(tests[test], ask.route_path_to_func_name(test))

	# parse_route_params_str
	def test_parse_route_params_str(self):
		tests = {
			'': '',
			'no parameter given': '',
			'<param>': 'param',
			'<param1> and <param2>': 'param1, param2',
			'string and <param\n>': 'param',
			'<param': '',
			'<>': '',
			'<par<param>ram>': 'param',
		}

		for test in tests:
			self.assertEqual(tests[test], ask.parse_route_params_str(test))

	# get_current_tab_level
	def test_get_current_tab_level(self):
		tests = {
			'\t': '\t',
			'\t\t': '\t\t',
			'\t\t\t': '\t\t\t',
			'parsed string\t': '\t',
			'parsed \t string': '\t',
			'\n': '',
			'\n\t': '\t',
			'parsed \t string \n \t': '\t',
		}

		for test in tests:
			self.assertEqual(tests[test], ask.get_current_tab_level(test))

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


if __name__ == '__main__':
	unittest.main()
