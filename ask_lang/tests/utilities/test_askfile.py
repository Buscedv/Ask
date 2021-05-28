# coding=utf-8
import unittest

import ask_lang.cfg as cfg
from ask_lang.utilities import askfile


class TestUtilitiesAskfileGetConfigRule(unittest.TestCase):
	@classmethod
	def setUp(cls) -> None:
		cfg.set_defaults()

	def test_single(self):
		cfg.ask_config = {'key': 'value'}
		self.assertEqual('value', askfile.get(['key'], 'missing'))

	def test_single_missing(self):
		cfg.ask_config = {}
		self.assertEqual('missing', askfile.get(['missing_key'], 'missing'))

	def test_multiple(self):
		cfg.ask_config = {'group': {'key': 'value'}}
		self.assertEqual('value', askfile.get(['group', 'key'], 'missing'))

	def test_multiple_missing(self):
		cfg.ask_config = {}
		self.assertEqual('missing', askfile.get(['missing_group', 'missing_key'], 'missing'))


if __name__ == '__main__':
	unittest.main()
