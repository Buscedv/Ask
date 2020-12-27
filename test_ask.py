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
			
	def test_route_params_empty_string(self):
		test_value = ''
		actual = ask.route_params(test_value)
		expected = ''
		self.assertEqual(expected, ask.route_params(test_value))

	def test_route_params_no_parameter(self):
		test_value = 'no parameter given'
		expected = ''
		self.assertEqual(expected, ask.route_params(test_value))

	def test_route_params_one_parameter(self):
		test_value = '<param>'
		expected = 'param'
		self.assertEqual(expected, ask.route_params(test_value))

	def test_route_params_two_parameters(self):
		test_value = '<param1> and <param2>'
		expected = 'param1, param2'
		self.assertEqual(expected, ask.route_params(test_value))

	def test_route_params_param_with_line_break(self):
		test_value = 'string and <param\n>'
		expected = 'param'
		self.assertEqual(expected, ask.route_params(test_value))

	def test_route_params_opened_not_closed(self):
		test_value = '<param'
		expected = ''
		self.assertEqual(expected, ask.route_params(test_value))

	def test_route_params_closed_not_opened(self):
		test_value = 'param>'
		expected = ''
		self.assertEqual(expected, ask.route_params(test_value))

	def test_route_params_empty_param(self):
		test_value = '<>'
		expected = ''
		self.assertEqual(expected, ask.route_params(test_value))

	def test_route_params_param_in_param(self):
		test_value = '<par<param>ram>'
		expected = 'param'
		self.assertEqual(expected, ask.route_params(test_value))

if __name__ == '__main__':
    unittest.main()
