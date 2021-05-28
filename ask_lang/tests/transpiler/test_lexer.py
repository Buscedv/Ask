# coding=utf-8
import unittest

from ask_lang import cfg
from ask_lang.transpiler import lexer


class TestTranspilerLexerInsertGroupMarkers(unittest.TestCase):
	@classmethod
	def setUp(cls) -> None:
		cfg.set_defaults()

	def test_(self):
		tokens = [
			['FUNC_DEF', 'function'],
			['FORMAT', '\n'],
			['FORMAT', '\t'],
			['FUNC', 'print'],
			['STR', 'text'],
			['OP', ')'],
			['FORMAT', '\n'],
			['FORMAT', '\t'],
			['WORD', 'if'],
			['WORD', 'WORD'],
			['OP', ':'],
			['FORMAT', '\n'],
			['FORMAT', '\t'],
			['FORMAT', '\t'],
			['FUNC', 'print'],
			['STR', 'text'],
			['OP', ')'],
			['FORMAT', '\n'],
			['FORMAT', '\t'],
			['FUNC', 'print'],
			['STR', 'text'],
			['OP', ')'],
		]

		expected = [
			['GROUP', 'start'],
			['FUNC_DEF', 'function'],
			['GROUP', 'start'],
			['FORMAT', '\n'],
			['FORMAT', '\t'],
			['FUNC', 'print'],
			['STR', 'text'],
			['OP', ')'],
			['FORMAT', '\n'],
			['FORMAT', '\t'],
			['WORD', 'if'],
			['WORD', 'WORD'],
			['OP', ':'],
			['GROUP', 'start'],
			['FORMAT', '\n'],
			['FORMAT', '\t'],
			['FORMAT', '\t'],
			['FUNC', 'print'],
			['STR', 'text'],
			['OP', ')'],
			['GROUP', 'end'],
			['FORMAT', '\n'],
			['FORMAT', '\t'],
			['FUNC', 'print'],
			['STR', 'text'],
			['OP', ')'],
			['GROUP', 'end'],
			['GROUP', 'end']
		]

		self.assertEqual(expected, lexer.insert_indent_group_markers(tokens))


class TestTranspilerLexerMergeOps(unittest.TestCase):
	@classmethod
	def setUp(cls) -> None:
		cfg.set_defaults()

	def test_(self):
		self.assertEqual(
			[['OP', '=='], ['TOKEN', 'value'], ['OP', '->'], ['TOKEN', 'value'], ['OP', '='], ['TOKEN', 'value'], ['OP', '=']],
			lexer.merge_ops(
				[['OP', '='], ['OP', '='], ['TOKEN', 'value'], ['OP', '-'], ['OP', '>'], ['TOKEN', 'value'], ['OP', '='], ['TOKEN', 'value'], ['OP', '=']]
			)
		)


class TestTranspilerLexerLex(unittest.TestCase):
	@classmethod
	def setUp(cls) -> None:
		cfg.set_defaults()

	# TODO: Add advanced tests here.


if __name__ == '__main__':
	unittest.main()
