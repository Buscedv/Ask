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

	def test_maybe_place_space_before(self):
		token_val = '%'

		parsed = [
			'',
			'string',
			'string\n',
			'string\t',
			'string(',
			'string ',
			'string.',
		]
		
		expected_result = [
			' % ',
			'string % ',
			'string\n% ',
			'string\t% ',
			'string(% ',
			'string % ',
			'string.% ',
		]
		for index, value in enumerate(parsed):
			self.assertEqual(expected_result[index], ask.maybe_place_space_before(value, token_val))
			


if __name__ == '__main__':
    unittest.main()
