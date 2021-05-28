import unittest
from unittest.mock import patch

from ask_lang import cfg
from ask_lang.transpiler.utilities import small_transpilers


def get_config_rule_patch_false(*args, **kwargs):
	return False


def get_config_rule_patch_true(*args, **kwargs):
	return True


class TestTranspilerUtilitiesSmallTranspilersGenericTranspileSymbol(unittest.TestCase):
	@classmethod
	def setUp(cls) -> None:
		cfg.set_defaults()

	get_config_rule_path_path = 'ask_lang.transpiler.utilities.small_transpilers.askfile.get'

	def test_match(self):
		with patch(self.get_config_rule_path_path, get_config_rule_patch_true):
			self.assertEqual(
				'match',
				small_transpilers.generic_transpile_symbol(
					'word',
					{'word': 'match'},
					'no match'
				)
			)

	def test_no_match(self):
		with patch(self.get_config_rule_path_path, get_config_rule_patch_true):
			self.assertEqual(
				'no match',
				small_transpilers.generic_transpile_symbol('missing', {'word': 'match'}, 'no match')
			)

	def test_add_underscores(self):
		with patch(self.get_config_rule_path_path, get_config_rule_patch_true):
			self.assertEqual(
				'match',
				small_transpilers.generic_transpile_symbol('_word', {'word': 'match'}, 'no match')
			)

	def test_dont_add_underscores(self):
		with patch(self.get_config_rule_path_path, get_config_rule_patch_false):
			self.assertEqual(
				'no match',
				small_transpilers.generic_transpile_symbol('_word', {'word': 'match'}, 'no match')
			)


class TestTranspilerUtilitiesSmallTranspilersTranspileDecorator(unittest.TestCase):
	@classmethod
	def setUp(cls) -> None:
		cfg.set_defaults()

	def test_(self):
		self.assertEqual('\n@check_for_token', small_transpilers.transpile_decorator('protected'))

	def test_basic(self):
		self.assertEqual('---', small_transpilers.transpile_decorator('basic'))

	def test_missing(self):
		self.assertEqual('', small_transpilers.transpile_decorator('not_real'))

	def test_part_of(self):
		self.assertEqual('\n@check_for_token_not_real', small_transpilers.transpile_decorator('protected_not_real'))


class TestTranspilerUtilitiesSmallTranspilersTranspileDbAction(unittest.TestCase):
	@classmethod
	def setUp(cls) -> None:
		cfg.set_defaults()

	def test_no_match(self):
		self.assertEqual(('', False), small_transpilers.transpile_db_action(''))

	def test_match(self):
		self.assertEqual(('generic_list_creator', False), small_transpilers.transpile_db_action('list'))

	def test_needs_commit(self):
		self.assertEqual(('db.session.add', True), small_transpilers.transpile_db_action('add'))


if __name__ == '__main__':
	unittest.main()
