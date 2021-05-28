import unittest

from ask_lang import cfg
from ask_lang.transpiler.utilities import transpiler_utils


class TestTranspilerUtilitiesTranspilerUtilsTokenCheck(unittest.TestCase):
	@classmethod
	def setUp(cls) -> None:
		cfg.set_defaults()

	def test_match_none(self):
		self.assertEqual(False, transpiler_utils.token_check(['TYPE', 'value']))

	# Single type.
	def test_match_type(self):
		self.assertEqual(True, transpiler_utils.token_check(['TYPE', 'value'], 'TYPE'))

	def test_match_type_false(self):
		self.assertEqual(False, transpiler_utils.token_check(['TYPE', 'value'], 'MISSING_TYPE'))

	# Single value.
	def test_match_value(self):
		self.assertEqual(True, transpiler_utils.token_check(['TYPE', 'value'], values='value'))

	def test_match_value_false(self):
		self.assertEqual(False, transpiler_utils.token_check(['TYPE', 'value'], values='missing_value'))

	# Multiple types.
	def test_match_types(self):
		self.assertEqual(True, transpiler_utils.token_check(['TYPE', 'value'], ['MISSING_TYPE', 'TYPE']))

	def test_match_types_false(self):
		self.assertEqual(False, transpiler_utils.token_check(['TYPE', 'value'], ['MISSING_TYPE1', 'MISSING_TYPE']))

	# Multiple values.
	def test_match_values(self):
		self.assertEqual(True, transpiler_utils.token_check(['TYPE', 'value'], values=['value', 'missing_value']))

	def test_match_values_false(self):
		self.assertEqual(False, transpiler_utils.token_check(['TYPE', 'value'], values=['missing_value', 'missing_value1']))


class TestTranspilerUtilitiesTranspilerUtilsAddUnderscoresToElems(unittest.TestCase):
	@classmethod
	def setUp(cls) -> None:
		cfg.set_defaults()

	def test_(self):
		self.assertEqual(['1', '2', '_1', '_2'], transpiler_utils.add_underscores_to_elems(['1', '2']))


if __name__ == '__main__':
	unittest.main()
