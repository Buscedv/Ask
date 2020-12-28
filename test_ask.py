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
		expected = '_path_path'
		self.assertEqual(expected, ask.route_path_to_func_name(test_value))

	def test_route_path_to_func_name_path_slash_dash_path(self):
		test_value = '/path/-path'
		expected = '_path_path'
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

	#route_params
	def test_route_params_empty_string(self):
		test_value = ''
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
