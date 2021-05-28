# coding=utf-8
import unittest
import os

from ask_lang import cfg
from ask_lang.utilities import files


class TestUtilitiesFileUtilsGetRootFromFilePath(unittest.TestCase):
	@classmethod
	def setUp(cls) -> None:
		cfg.set_defaults()

	def test_(self):
		file_path = '/folder/folder/file.txt'
		self.assertEqual('/folder/folder', files.get_root_from_file_path(file_path))


class TestUtilitiesFileUtilsGetFullDbFilePath(unittest.TestCase):
	@classmethod
	def setUp(cls) -> None:
		cfg.set_defaults()

	def test_(self):
		cfg.ask_config = {}
		self.assertEqual(f'sqlite:///{os.getcwd()}/db.db', files.db_path_with_prefix())

	def test_custom_path(self):
		cfg.ask_config = {'db': {'path': 'xyz.db'}}
		self.assertEqual(f'sqlite:///{os.getcwd()}/xyz.db', files.db_path_with_prefix())

	def test_custom_protocol(self):
		cfg.ask_config = {'db': {'custom': True, 'path': 'xyz.db'}}
		self.assertEqual('xyz.db', files.db_path_with_prefix())


class TestUtilitiesFileUtilsGetDbFilePath(unittest.TestCase):
	@classmethod
	def setUp(cls) -> None:
		cfg.set_defaults()

	def test_(self):
		cfg.ask_config = {}
		self.assertEqual(f'{os.getcwd()}/db.db', files.get_db_file_path())

	def test_custom_path(self):
		cfg.ask_config = {'db': {'path': 'xyz.db'}}
		self.assertEqual(f'{os.getcwd()}/xyz.db', files.get_db_file_path())


class TestUtilitiesFileUtilsGetOutputFileDestinationPath(unittest.TestCase):
	@classmethod
	def setUp(cls) -> None:
		cfg.set_defaults()

	def test_(self):
		cfg.ask_config = {}
		cfg.source_file_name = 'script.ask_lang'
		self.assertEqual(f'{os.getcwd()}/app.py', files.output_file_path())

	def test_sub_path(self):
		cfg.ask_config = {}
		cfg.source_file_name = 'folder/script.ask_lang'
		self.assertEqual(f'{os.getcwd()}/folder/app.py', files.output_file_path())


if __name__ == '__main__':
	unittest.main()
