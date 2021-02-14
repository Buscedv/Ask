import unittest

from ask.utilities import file_utils


class TestAskUtilitiesFileUtils(unittest.TestCase):
	# get_root_from_file_path()
	def test_get_root_from_file_path(self):
		file_path = '/folder/folder/file.txt'
		self.assertEqual('/folder/folder', file_utils.get_root_from_file_path(file_path))


if __name__ == '__main__':
	unittest.main()
