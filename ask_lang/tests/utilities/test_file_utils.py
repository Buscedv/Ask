import unittest

from ask_lang import cfg
from ask_lang.utilities import file_utils


class TestUtilitiesFileUtilsGetRootFromFilePath(unittest.TestCase):
	def test_(self):
		file_path = '/folder/folder/file.txt'
		self.assertEqual('/folder/folder', file_utils.get_root_from_file_path(file_path))


class TestUtilitiesFileUtilsGetFullDbFilePath(unittest.TestCase):
	def test_(self):
		cfg.ask_config = {}
		self.assertEqual('sqlite:///db.db', file_utils.get_full_db_file_path())

	def test_custom_path(self):
		cfg.ask_config = {'db': {'path': 'xyz.db'}}
		self.assertEqual('sqlite:///xyz.db', file_utils.get_full_db_file_path())

	def test_custom_protocol(self):
		cfg.ask_config = {'db': {'custom': True, 'path': 'xyz.db'}}
		self.assertEqual('xyz.db', file_utils.get_full_db_file_path())


class TestUtilitiesFileUtilsGetDbFilePath(unittest.TestCase):
	def test_(self):
		cfg.ask_config = {}
		self.assertEqual('db.db', file_utils.get_db_file_path())

	def test_custom_path(self):
		cfg.ask_config = {'db': {'path': 'xyz.db'}}
		self.assertEqual('xyz.db', file_utils.get_db_file_path())


class TestUtilitiesFileUtilsGetOutputFileDestinationPath(unittest.TestCase):
	def test_(self):
		cfg.source_file_name = 'script.ask_lang'
		self.assertEqual('app.py', file_utils.get_output_file_destination_path())

	def test_sub_path(self):
		cfg.source_file_name = 'folder/script.ask_lang'
		self.assertEqual('folder/app.py', file_utils.get_output_file_destination_path())


if __name__ == '__main__':
	unittest.main()
