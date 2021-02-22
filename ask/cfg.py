# coding=utf-8
from collections import defaultdict

# Transpiler related globals.
built_in_vars = ['body', 'form', 'args', 'req', 'auth', 'env', 'db', 'datetime']
variables = built_in_vars
keywords = ['if', 'else', 'elif', 'in', 'return', 'not', 'or', 'respond']
# "Special" keywords = keywords that require some sort of data after the keyword it self.
# e.g. Classes have a class name.
db_class = {
	'type': 'DB_MODEL',
	'collect': True,
	'collect_ends': [':'],
	'include_collect_end': True
}
special_keywords = {
	'db_class': db_class,
	'db_model': db_class,
	'def': {
		'type': 'FUNC_DEF',
		'collect': True,
		'collect_ends': ['('],
		'include_collect_end': False
	},
	'decorator': {
		'type': 'DEC_DEF',
		'collect': True,
		'collect_ends': [':'],
		'include_collect_end': False
	}
}
operators = [':', ')', '!', '+', '-', '*', '/', '%', '.', ',', '[', ']', '&', '>', '<', '~', '^', '&', '|']
ask_library_methods = ['quick_set', 'quickSet', 'deep', 'serialize', 'respond', 'require_keys']
flask_boilerplate = ''
flask_end_boilerplate = ''
uses_db = False
uses_basic_decorator = False
uses_routes = False
basic_decorator_collector = []
previous_basic_decorator_collector = []
basic_decorator_has_primary_key = False

# Others.
ask_config = {}

project_information = {
	'version': '1.0.0',
}

source_file_name = ''
is_dev = False
is_extra_dev = False
transpilation_result = defaultdict(lambda: '', {})
