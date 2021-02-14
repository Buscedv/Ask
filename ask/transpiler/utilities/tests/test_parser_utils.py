import unittest

from ask.transpiler.utilities import parser_utils


class TestAskTranspilerUtilitiesParserUtils(unittest.TestCase):
	# route_path_to_func_name()
	def test_route_path_to_func_name(self):
		tests = {
			'/foo/bar': '_foo_bar',
			'/foo-bar': '_foo_bar',
			'/foo/<bar>': '_foo__bar_',
		}

		for test in tests:
			self.assertEqual(tests[test], parser_utils.route_path_to_func_name(test))

	# parse_route_params_str()
	def test_parse_route_params_str(self):
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
			self.assertEqual(tests[test], parser_utils.parse_route_params_str(test))

	# get_current_tab_level()
	def test_get_current_tab_level(self):
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
			self.assertEqual(tests[test], parser_utils.get_current_tab_level(test))


def main():
	unittest.main()


if __name__ == '__main__':
	main()
