import unittest

from ask_lang.transpiler.utilities import lexer_utils


class TestTranspilerUtilitiesLexerUtilsGroupToksByLines(unittest.TestCase):
	def test_(self):
		tokens = [
			['TOKEN', 'token'],
			['TOKEN', 'token'],
			['FORMAT', '\n'],
			['TOKEN', 'token'],
			['FORMAT', '\n'],
			['TOKEN', 'token'],
			['TOKEN', 'token'],
		]

		expected = [
			[
				['TOKEN', 'token'],
				['TOKEN', 'token'],
			],
			[
				['FORMAT', '\n'],
				['TOKEN', 'token'],
			],
			[
				['FORMAT', '\n'],
				['TOKEN', 'token'],
				['TOKEN', 'token'],
			]
		]

		self.assertEqual(expected, lexer_utils.group_toks_by_lines(tokens))


class TestTranspilerUtilitiesLexerUtilsWordOrSpecial(unittest.TestCase):
	def test_empty_tmp(self):
		expected = ([['TOKEN', 'token']], '', False, [], False)
		self.assertEqual(expected, lexer_utils.word_or_special([['TOKEN', 'token']], ''))

	def test_word(self):
		expected = ([['TOKEN', 'token'], ['WORD', 'word']], '', False, [], False)
		self.assertEqual(expected, lexer_utils.word_or_special([['TOKEN', 'token']], 'word'))

	def test_special_db_model(self):
		expected = ([['TOKEN', 'token'], ['DB_MODEL', 'db_model']], '', True, [':'], True)
		self.assertEqual(expected, lexer_utils.word_or_special([['TOKEN', 'token']], 'db_model'))

	def test_special_def(self):
		expected = ([['TOKEN', 'token'], ['FUNC_DEF', 'def']], '', True, ['('], False)
		self.assertEqual(expected, lexer_utils.word_or_special([['TOKEN', 'token']], 'def'))


class TestTranspilerUtilitiesLexerUtilsAddChunk(unittest.TestCase):
	def test_not_string(self):
		expected = ([{'is_string': False, 'code': 'code'}], '', True)
		self.assertEqual(expected, lexer_utils.add_chunk([], False, 'code'))

	def test_not_string_with_new_line_end(self):
		expected = ([{'is_string': False, 'code': 'code\n'}], '', False)
		self.assertEqual(expected, lexer_utils.add_chunk([], False, 'code\n'))

	def test_string(self):
		expected = ([{'is_string': True, 'code': 'my string'}], '', True)
		self.assertEqual(expected, lexer_utils.add_chunk([], True, 'my string'))

	def test_string_with_new_line_end(self):
		expected = ([{'is_string': True, 'code': 'my string\n'}], '', False)
		self.assertEqual(expected, lexer_utils.add_chunk([], True, 'my string\n'))


class TestTranspilerUtilitiesLexerUtilsReformatLine(unittest.TestCase):
	def test_add_new_line_at_the_end(self):
		self.assertEqual('word\n', lexer_utils.reformat_line('word'))
		self.assertEqual('word\n', lexer_utils.reformat_line('word\n'))

	def test_quotes(self):
		self.assertEqual('"Hello, World!"\n', lexer_utils.reformat_line('\'Hello, World!\''))

	def test_space_before_parenthesis(self):
		self.assertEqual('print()\n', lexer_utils.reformat_line('print ()\n'))

	def test_indents_fix(self):
		original = 'if True:\n  print(True)\nif False:\n    print(False)'
		expected = 'if True:\n\tprint(True)\nif False:\n\tprint(False)\n'

		self.assertEqual(expected, lexer_utils.reformat_line(original))


if __name__ == '__main__':
	unittest.main()
