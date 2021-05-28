# coding=utf-8
from collections import defaultdict
from typing import Tuple

from ask_lang import cfg
from ask_lang.utilities import askfile, serve_run
from ask_lang.transpiler.utilities import translator_utils


def generic_transpile_symbol(word: str, words: dict, default: str = None) -> str:
	if askfile.get(['rules', 'underscores'], True):
		words = translator_utils.add_underscores_to_dict_keys(words)

	return defaultdict(lambda: default if default is not None else word, words)[word]


def transpile_function(function: str) -> str:
	return generic_transpile_symbol(function, {
		'respond': 'return jsonify(',
		'inner': 'func(*args, **kwargs',
		'status': 'abort(Response('
	}, f'{function}(')


def transpile_word(word: str, translated: str) -> str:
	translations = {
		'body': 'request.json',
		'form': 'request.form',
		'args': 'request.args',
		'files': 'request.files',
		'req': 'AskLibrary.get_all_req()',
		'datetime': 'datetime.datetime',
		'respond': 'return'
	}

	if word in translations and translated and translated[-1] in ['.']:
		return word

	return generic_transpile_symbol(word, translations)


def transpile_decorator(decorator: str) -> str:
	decorators = {
		'protected': 'check_for_token',
		'limit': 'limiter.limit',
	}

	if decorator == 'basic':
		cfg.previous_basic_decorator_collector = cfg.basic_decorator_collector
		cfg.uses_basic_decorator = True
		cfg.basic_decorator_collector = []

		# "---" is interpreted as an ignored decorator.
		return '---'

	try:
		# A fully matching decorator
		return f'\n@{decorators[decorator]}'
	except KeyError:
		# Check if the decorator partly matches one in the transpilation dict.
		for key, value in decorators.items():
			if decorator[:len(key)] == key:
				return f'\n@{value}{decorator[len(key):]}'
	return ''


def transpile_db_action(action: str) -> Tuple[str, bool]:
	needs_commit = ['add', 'delete']

	transpiled_action = generic_transpile_symbol(action, {
		# Basic
		'col': 'db.Column',

		# Attributes
		'pk': 'primary_key=True',
		'unique': 'unique=True',
		'nullable': 'nullable=True',
		'basic_ignore': 'ignored',  # Ignored in the basic init() boilerplate.
		'desc': 'db.desc',

		# Data types
		'int': 'db.Integer',
		'str': 'db.String',
		'float': 'db.Float',
		'bool': 'db.Boolean',
		'bytes': 'db.LargeBinary',
		'datetime': 'db.DateTime',
		'list_id': 'db.Integer',

		# Actions
		'all': 'query.all',
		'get': 'query.get',
		'save': 'db.session.commit',
		'delete': 'db.session.delete',
		'get_by': 'query.filter_by',
		'filter': 'query.filter',
		'add': 'db.session.add',
		'exists': 'AskLibrary.exists',
		'execute': 'db.engine.execute',

		# Other
		'list': 'generic_list_creator',
	}, '')

	return transpiled_action, action in needs_commit
