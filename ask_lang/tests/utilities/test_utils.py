import unittest

import ask_lang.cfg as cfg
from ask_lang.utilities import utils


class TestUtilitiesUtilsParseSysArgs(unittest.TestCase):
	def test_no_valid_flags(self):
		self.assertEqual(('file', True), utils.parse_sys_args(['ask_lang', 'file']))

	#  single after
	def test_single_flag_after(self):
		self.assertEqual(('file', False), utils.parse_sys_args(['ask_lang', 'file', '-d']))

	# Multiple after
	def test_multiple_flags_after(self):
		self.assertEqual(('file', False), utils.parse_sys_args(['ask_lang', 'file', '-d', '--version']))

	# Single before.
	def test_single_flag_before(self):
		self.assertEqual(('file', False), utils.parse_sys_args(['ask_lang', '-d', 'file']))

	# Multiple before.
	def test_multiple_flags_before(self):
		self.assertEqual(('file', False), utils.parse_sys_args(['ask_lang', '--dev', '-v', 'file']))

	# Mix.
	def test_mixed_flags(self):
		self.assertEqual(('file', False), utils.parse_sys_args(['ask_lang', '-d', 'file', '--version', '-v']))


class TestUtilitiesUtilsGetConfigRule(unittest.TestCase):
	def test_single(self):
		cfg.ask_config = {'key': 'value'}
		self.assertEqual('value', utils.get_config_rule(['key'], 'missing'))

	def test_single_missing(self):
		cfg.ask_config = {}
		self.assertEqual('missing', utils.get_config_rule(['missing_key'], 'missing'))

	def test_multiple(self):
		cfg.ask_config = {'group': {'key': 'value'}}
		self.assertEqual('value', utils.get_config_rule(['group', 'key'], 'missing'))

	def test_multiple_missing(self):
		cfg.ask_config = {}
		self.assertEqual('missing', utils.get_config_rule(['missing_group', 'missing_key'], 'missing'))


if __name__ == '__main__':
	unittest.main()
