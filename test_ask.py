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
