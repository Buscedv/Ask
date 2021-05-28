# coding=utf-8
import unittest

from ask_lang import cfg
from ask_lang.transpiler import translator


class TestTranspilerTranslatorInsertBasicDecoratorCodeToInsert(unittest.TestCase):
	@classmethod
	def setUp(cls) -> None:
		cfg.set_defaults()

	# TODO: Add advanced tests here.


class TestTranspilerTranslatorTranslate(unittest.TestCase):
	@classmethod
	def setUp(cls) -> None:
		cfg.set_defaults()

	# TODO: Add advanced tests here.


if __name__ == '__main__':
	unittest.main()
