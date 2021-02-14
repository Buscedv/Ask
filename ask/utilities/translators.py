from collections import defaultdict

from ask import cfg


def generic_transpile_word(word, words, default=None):
	return defaultdict(lambda: default if default is not None else word, words)[word]


def transpile_function(function):
	return generic_transpile_word(function, {
		'respond': 'return jsonify(',
		'inner': 'func(*args, **kwargs',
		'status': 'abort(Response('
	}, f'{function}(')


def transpile_var(var):
	translations = {
		'body': 'request.json',
		'form': 'request.form',
		'args': 'request.args',
		'req': 'AskLibrary.get_all_req()',
		'datetime': 'datetime.datetime'
	}

	# Also support built in vars with leading underscores.
	translations_with_underscores = {f'_{var_key}': translations[var_key] for var_key in translations}
	translations.update(translations_with_underscores)

	return generic_transpile_word(var, translations)


def transpile_keyword(keyword):
	return generic_transpile_word(keyword, {
		'respond': 'return'
	})


def transpile_decorator(decorator):
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
		return f'\n@{decorators[decorator]}'
	except KeyError:
		for key, value in decorators.items():
			if decorator[:len(key)] == key:
				return f'\n@{value}{decorator[len(key):]}'
	return ''


def transpile_db_action(action):
	needs_commit = ['add', 'delete']

	transpiled_action = generic_transpile_word(action, {
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

	return [transpiled_action, action in needs_commit]
