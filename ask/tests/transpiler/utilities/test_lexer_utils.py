import unittest

from ask.transpiler.utilities import lexer_utils


class TestAskTranspilerUtilitiesLexerUtils(unittest.TestCase):
	# group_tokens_by_lines()
	def test_tokens_grouped_by_lines(self):
		tokens = [
			['WORD', 'variable'],
			['FORMAT', '\n'],
			['WORD', 'variable'],
			['FORMAT', '\n'],
			['FORMAT', '\t'],
			['WORD', 'variable'],
			['FORMAT', '\n'],
			['FORMAT', '\t'],
			['FORMAT', '\t'],
			['WORD', 'variable'],
		]

		expected = [
			[
				['WORD', 'variable'],
			],
			[
				['FORMAT', '\n'],
				['WORD', 'variable'],
			],
			[
				['FORMAT', '\n'],
				['FORMAT', '\t'],
				['WORD', 'variable'],
			],
			[
				['FORMAT', '\n'],
				['FORMAT', '\t'],
				['FORMAT', '\t'],
				['WORD', 'variable'],
			],
		]

		self.assertEqual(expected, lexer_utils.group_tokens_by_lines(tokens))


if __name__ == '__main__':
	unittest.main()
