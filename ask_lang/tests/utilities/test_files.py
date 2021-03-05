import unittest

from ask_lang import cfg
from ask_lang.utilities import files


class TestUtilitiesFileUtilsGetRootFromFilePath(unittest.TestCase):
	def test_(self):
		file_path = '/folder/folder/file.txt'
		self.assertEqual('/folder/folder', files.get_root_from_file_path(file_path))


class TestUtilitiesFileUtilsGetFullDbFilePath(unittest.TestCase):
	def test_(self):
		cfg.ask_config = {}
		self.assertEqual('sqlite:///db.db', files.db_path_with_prefix())

	def test_custom_path(self):
		cfg.ask_config = {'db': {'path': 'xyz.db'}}
		self.assertEqual('sqlite:///xyz.db', files.db_path_with_prefix())

	def test_custom_protocol(self):
		cfg.ask_config = {'db': {'custom': True, 'path': 'xyz.db'}}
		self.assertEqual('xyz.db', files.db_path_with_prefix())


class TestUtilitiesFileUtilsGetDbFilePath(unittest.TestCase):
	def test_(self):
		cfg.ask_config = {}
		self.assertEqual('db.db', files.get_db_file_path())

	def test_custom_path(self):
		cfg.ask_config = {'db': {'path': 'xyz.db'}}
		self.assertEqual('xyz.db', files.get_db_file_path())


class TestUtilitiesFileUtilsGetOutputFileDestinationPath(unittest.TestCase):
	def test_(self):
		cfg.source_file_name = 'script.ask_lang'
		self.assertEqual('app.py', files.output_file_path())

	def test_sub_path(self):
		cfg.source_file_name = 'folder/script.ask_lang'
		self.assertEqual('folder/app.py', files.output_file_path())


if __name__ == '__main__':
	unittest.main()
