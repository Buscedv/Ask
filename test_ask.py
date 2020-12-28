import unittest
import ask


class TestAsk(unittest.TestCase):
	def test_get_root_from_file_path(self):
		file_path = '/folder/folder/file.txt'
		self.assertEqual('/folder/folder', ask.get_root_from_file_path(file_path))

	def test_route_path_to_func_name(self):
		route_paths = [
			'/path',
			'/path/subpath',
			'/path/subpath/',
			'/path-path'
		]

		func_names = [
			'_path',
			'_path_subpath',
			'_path_subpath_',
			'_path_path'
		]

		for index, route_path in enumerate(route_paths):
			self.assertEqual(func_names[index], ask.route_path_to_func_name(route_path))

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

		excpected = [
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

		self.assertEqual(excpected, ask.tokens_grouped_by_lines(tokens))

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

