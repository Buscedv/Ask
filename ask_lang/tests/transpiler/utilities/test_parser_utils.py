import unittest

from ask_lang.transpiler.utilities import parser_utils


class TestTranspilerUtilitiesParserUtilsIsDbColumnInLastLine(unittest.TestCase):
	def test_true_db_action(self):
		self.assertEqual(
			True,
			parser_utils.is_db_column_or_model_in_past_line([['FORMAT', '\n'], ['DB_ACTION', 'col'], ['TOKEN', 'token']])
		)

	def test_true_db_model(self):
		self.assertEqual(
			True,
			parser_utils.is_db_column_or_model_in_past_line([['FORMAT', '\n'], ['DB_MODEL', 'model'], ['OP', ':']])
		)

	def test_false_caused_by_newline(self):
		self.assertEqual(
			False,
			parser_utils.is_db_column_or_model_in_past_line([
				['FORMAT', '\n'],
				['DB_ACTION', 'col'],
				['FORMAT', '\n'], ['TOKEN', 'token']
			])
		)

	def test_false_missing(self):
		self.assertEqual(
			False,
			parser_utils.is_db_column_or_model_in_past_line([
				['TOKEN', 'token']
			])
		)


class TestTranspilerUtilitiesParserUtilsPreviousNonKeywordWordTok(unittest.TestCase):
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
				parser_utils.previous_non_keyword_word_tok(test['test'])
			)


class TestTranspilerUtilitiesParserUtilsUriToFuncName(unittest.TestCase):
	def test_(self):
		tests = {
			'/foo/bar': '_foo_bar',
			'/foo-bar': '_foo_bar',
			'/foo/<bar>': '_foo__bar_',
		}

		for test in tests:
			self.assertEqual(tests[test], parser_utils.uri_to_func_name(test))


class TestTranspilerUtilitiesParserUtilsIsWordChar(unittest.TestCase):
	def test_(self):
		self.assertEqual(True, parser_utils.is_word_char('a'))
		self.assertEqual(True, parser_utils.is_word_char('_'))
		self.assertEqual(False, parser_utils.is_word_char('1'))
		self.assertEqual(False, parser_utils.is_word_char(1))
		self.assertEqual(False, parser_utils.is_word_char('.'))
		self.assertEqual(False, parser_utils.is_word_char('+'))


class TestTranspilerUtilitiesParserUtilsSpacePrefix(unittest.TestCase):
	def test_no_space_beginning(self):
		self.assertEqual('', parser_utils.space_prefix(''))

	def test_no_space_before_char(self):
		for char in [':', ',', '(', ')', '.', '[', ']', '{', '}']:
			self.assertEqual('', parser_utils.space_prefix('', to_add=char))

	def test_no_space_after_char(self):
		for char in [':', ',', '(', ')', '.', '[', ']', '{', '}']:
			self.assertEqual([''], [parser_utils.space_prefix('', to_add=char)])

	def test_space_after_char(self):
		for char in [',']:
			self.assertEqual(' ', parser_utils.space_prefix(char))

	def test_no_space_between_char_and_word(self):
		for char in ['[']:
			self.assertEqual('', parser_utils.space_prefix(char, 'a'))

	def test_space_between_words(self):
		self.assertEqual(' ', parser_utils.space_prefix('a', 'a'))


class TestTranspilerUtilitiesParserUtilsExtractParamsFromUri(unittest.TestCase):
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
			self.assertEqual(tests[test], parser_utils.extract_params_from_uri(test))


class TestTranspilerUtilitiesParserUtilsGetTabCount(unittest.TestCase):
	def test_(self):
		tests = {
			'\t': '\t',
			'\t\t': '\t\t',
			'\t\t\t': '\t\t\t',
			'parsed string\t': '\t',
			'parsed \t string': '\t',
			'\n': '',
			'\n\t': '\t',
			'parsed \t string \n \t': '\t',
		}

		for test in tests:
			self.assertEqual(tests[test], parser_utils.get_tab_count(test))


class TestTranspilerUtilitiesParserUtilsAddUnderscoresToDictKeys(unittest.TestCase):
	def test_(self):
		self.assertEqual(
			{'key': 'value', '_key': 'value'},
			parser_utils.add_underscores_to_dict_keys({'key': 'value'}))


if __name__ == '__main__':
	unittest.main()
