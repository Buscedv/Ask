# coding=utf-8
from collections import defaultdict


def set_defaults():
	global built_in_vars
	global variables
	global keywords
	global db_class
	global special_keywords
	global operators
	global ask_library_methods
	global flask_boilerplate
	global flask_end_boilerplate
	global uses_db
	global uses_basic_decorator
	global uses_routes
	global basic_decorator_collector
	global previous_basic_decorator_collector
	global basic_decorator_has_primary_key
	global ask_config
	global imported_ask_modules_to_delete
	global included_module_code
	global project_information
	global source_file_name
	global is_dev
	global is_extra_dev
	global is_repl
	global repl_previous_transpiled
	global transpilation_result
	global is_module_transpile
	global is_include_transpile

	# Transpiler related globals.
	built_in_vars = ['body', 'form', 'args', 'req', 'files', 'auth', 'env', 'db', 'datetime']
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
	imported_ask_modules_to_delete = []
	included_module_code = ''

	project_information = {
		'version': '1.4.1',
	}

	source_file_name = ''
	is_dev = False
	is_extra_dev = False
	is_repl = False
	repl_previous_transpiled = ''
	transpilation_result = defaultdict(lambda: '', {})
	is_module_transpile = False
	is_include_transpile = False


built_in_vars = []
variables = []
keywords = []
db_class = {}
special_keywords = {}
operators = []
ask_library_methods = []
flask_boilerplate = ''
flask_end_boilerplate = ''
uses_db = False
uses_basic_decorator = False
uses_routes = False
basic_decorator_collector = []
previous_basic_decorator_collector = []
basic_decorator_has_primary_key = False
ask_config = {}
imported_ask_modules_to_delete = []
included_module_code = ''
project_information = {}
source_file_name = ''
is_dev = False
is_extra_dev = False
is_repl = False
repl_previous_transpiled = ''
transpilation_result = defaultdict(lambda: '', {})
is_module_transpile = False
is_include_transpile = False
