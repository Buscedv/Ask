# coding=utf-8
import unittest

from ask_lang import __main__ as main__, cfg


class TestParseSysArgs(unittest.TestCase):
	@classmethod
	def setUp(cls) -> None:
		cfg.set_defaults()

	def test_only_file_name(self):
		self.assertEqual(('my_script', True), main__.parse_sys_args(['ask', 'my_script'], True))

	def test_only_flags(self):
		self.assertEqual(('', False), main__.parse_sys_args(['ask', '-h', '--version'], True))

	def test_file_name_and_flags(self):
		self.assertEqual(('my_script', False), main__.parse_sys_args(['ask', 'my_script', '-h', '--version'], True))

	def test_flags_and_file_name(self):
		self.assertEqual(('my_script', False), main__.parse_sys_args(['ask', '-h', '--version', 'my_script'], True))

	def test_nothing(self):
		self.assertEqual(('', True), main__.parse_sys_args(['ask'], True))

	def test_dev(self):
		self.assertEqual(('my_script', False), main__.parse_sys_args(['ask', 'my_script', '--dev'], True))
		self.assertEqual(True, cfg.is_dev)

	def test_extra_dev(self):
		self.assertEqual(('my_script', False), main__.parse_sys_args(['ask', 'my_script', '-xd'], True))
		self.assertEqual(True, cfg.is_extra_dev)

	def test_module_transpile(self):
		self.assertEqual(('my_script', False), main__.parse_sys_args(['ask', 'my_script', '--module-transpile'], True))
		self.assertEqual(True, cfg.is_module_transpile)
		self.assertEqual({
					'system': {
						'output_path': 'my_script',
						'server': False
					}
				}, cfg.ask_config)

	def test_include_transpile(self):
		self.assertEqual(('my_script', False), main__.parse_sys_args(['ask', 'my_script', '--include-transpile'], True))
		self.assertEqual(True, cfg.is_include_transpile)

	def test_dev_no_file_name(self):
		self.assertEqual(('', True), main__.parse_sys_args(['ask', '--dev'], True))
		self.assertEqual(True, cfg.is_dev)


if __name__ == '__main__':
	unittest.main()
