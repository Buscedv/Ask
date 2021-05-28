import unittest

from ask_lang import cfg
from ask_lang.transpiler.utilities import translator_utils


class TestTranspilerUtilitiesTranslatorUtilsIsDbColumnInLastLine(unittest.TestCase):
	@classmethod
	def setUp(cls) -> None:
		cfg.set_defaults()

	def test_true_db_action(self):
		self.assertEqual(
			True,
			translator_utils.is_db_column_or_model_in_past_line([['FORMAT', '\n'], ['DB_ACTION', 'col'], ['TOKEN', 'token']])
		)

	def test_true_db_model(self):
		self.assertEqual(
			True,
			translator_utils.is_db_column_or_model_in_past_line([['FORMAT', '\n'], ['DB_MODEL', 'model'], ['OP', ':']])
		)

	def test_false_caused_by_newline(self):
		self.assertEqual(
			False,
			translator_utils.is_db_column_or_model_in_past_line([
				['FORMAT', '\n'],
				['DB_ACTION', 'col'],
				['FORMAT', '\n'], ['TOKEN', 'token']
			])
		)

	def test_false_missing(self):
		self.assertEqual(
			False,
			translator_utils.is_db_column_or_model_in_past_line([
				['TOKEN', 'token']
			])
		)


class TestTranspilerUtilitiesTranslatorUtilsPreviousNonKeywordWordTok(unittest.TestCase):
	@classmethod
	def setUp(cls) -> None:
		cfg.set_defaults()

	def test_(self):
		tests = [
			{
				'test': [['FUNC', 'respond'], ['WORD', 'not'], ['WORD', 'var'], ['OP', ')']],
				'expected': 'var'
			},
			{
				'test': [['WORD', 'if'], ['NUM', '4'], ['OP', '='], ['WORD', 'my_variable']],
				'expected': 'my_variable'
			},
		]

		for test in tests:
			self.assertEqual(
				test['expected'],
				translator_utils.previous_non_keyword_word_tok(test['test'])
			)


class TestTranspilerUtilitiesTranslatorUtilsUriToFuncName(unittest.TestCase):
	@classmethod
	def setUp(cls) -> None:
		cfg.set_defaults()

	def test_(self):
		tests = {
			'/foo/bar': '_foo_bar',
			'/foo-bar': '_foo_bar',
			'/foo/<bar>': '_foo__bar_',
			'\'/foo/<bar>\'': '_foo__bar_'
		}

		for test in tests:
			self.assertEqual(tests[test], translator_utils.uri_to_func_name(test))


class TestTranspilerUtilitiesTranslatorUtilsIsWordChar(unittest.TestCase):
	@classmethod
	def setUp(cls) -> None:
		cfg.set_defaults()

	def test_(self):
		self.assertEqual(True, translator_utils.is_word_char('a'))
		self.assertEqual(True, translator_utils.is_word_char('_'))
		self.assertEqual(False, translator_utils.is_word_char('1'))
		self.assertEqual(False, translator_utils.is_word_char(1))
		self.assertEqual(False, translator_utils.is_word_char('.'))
		self.assertEqual(False, translator_utils.is_word_char('+'))


class TestTranspilerUtilitiesTranslatorUtilsSpacePrefix(unittest.TestCase):
	@classmethod
	def setUp(cls) -> None:
		cfg.set_defaults()

	def test_no_space_beginning(self):
		self.assertEqual('', translator_utils.space_prefix(''))

	def test_no_space_before_char(self):
		for char in [':', ',', '(', ')', '.', '[', ']', '{', '}']:
			self.assertEqual('', translator_utils.space_prefix('', to_add=char))

	def test_no_space_after_char(self):
		for char in [':', ',', '(', ')', '.', '[', ']', '{', '}']:
			self.assertEqual([''], [translator_utils.space_prefix('', to_add=char)])

	def test_space_after_char(self):
		for char in [',']:
			self.assertEqual(' ', translator_utils.space_prefix(char))

	def test_no_space_between_char_and_word(self):
		for char in ['[']:
			self.assertEqual('', translator_utils.space_prefix(char, 'a'))

	def test_space_between_words(self):
		self.assertEqual(' ', translator_utils.space_prefix('a', 'a'))


class TestTranspilerUtilitiesTranslatorUtilsExtractParamsFromUri(unittest.TestCase):
	@classmethod
	def setUp(cls) -> None:
		cfg.set_defaults()

	def test_(self):
		tests = {
			'': '',
			'no parameter given': '',
			'<param>': 'param',
			'<param1> and <param2>': 'param1, param2',
			'string and <param\n>': 'param',
			'<param': '',
			'<>': '',
			'<par<param>ram>': 'param',
		}

		for test in tests:
			self.assertEqual(tests[test], translator_utils.extract_params_from_uri(test))


class TestTranspilerUtilitiesTranslatorUtilsGetTabCount(unittest.TestCase):
	@classmethod
	def setUp(cls) -> None:
		cfg.set_defaults()

	def test_(self):
		tests = {
			'\t': '\t',
			'\t\t': '\t\t',
			'\t\t\t': '\t\t\t',
			'translated string\t': '\t',
			'translated \t string': '\t',
			'\n': '',
			'\n\t': '\t',
			'translated \t string \n \t': '\t',
		}

		for test in tests:
			self.assertEqual(tests[test], translator_utils.get_tab_count(test))


class TestTranspilerUtilitiesTranslatorUtilsAddUnderscoresToDictKeys(unittest.TestCase):
	@classmethod
	def setUp(cls) -> None:
		cfg.set_defaults()

	def test_(self):
		self.assertEqual(
			{'key': 'value', '_key': 'value'},
			translator_utils.add_underscores_to_dict_keys({'key': 'value'}))


if __name__ == '__main__':
	unittest.main()
