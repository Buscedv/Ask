# coding=utf-8
from ask_lang import cfg
from ask_lang.utilities import file_utils


# Checks if a given token matches type(s) and/or value(s)
def token_check(token: list, types: str or list = '', values: str or list = '') -> bool:
	try:
		def generic_matcher(needle, haystack):
			return needle == haystack if not type(haystack) is list else needle in haystack

		# Just match types.
		if not values and types:
			return generic_matcher(token[0], types)

		# Just match values.
		if not types and values:
			return generic_matcher(token[1], values)

		# Match both types & values.
		return generic_matcher(token[0], types) and generic_matcher(token[1], values)
	except KeyError:
		# Default.
		return False


def add_underscores_to_elems(original_list: list) -> list:
	return original_list + [f'_{element}' for element in original_list]


def set_boilerplate():
	if cfg.is_extra_dev:
		cfg.flask_boilerplate = '# WARNING! Boilerplate skipped. Extra dev mode is on! (-xd/--extra-dev)'
		return

	# Imports & initial setup
	cfg.flask_boilerplate = ''
	cfg.flask_boilerplate += 'from flask import Flask, jsonify, abort, request, Response\n'
	cfg.flask_boilerplate += 'from flask_limiter import Limiter\n'
	cfg.flask_boilerplate += 'from flask_limiter.util import get_remote_address\n'
	cfg.flask_boilerplate += 'from flask_cors import CORS\n'
	cfg.flask_boilerplate += 'from functools import wraps\n'
	cfg.flask_boilerplate += 'import jwt\n'
	cfg.flask_boilerplate += 'import datetime\n'
	cfg.flask_boilerplate += 'import os\n'
	cfg.flask_boilerplate += 'import hashlib\n'
	cfg.flask_boilerplate += 'import random as rand\n'
	cfg.flask_boilerplate += 'import pickle\n'
	cfg.flask_boilerplate += 'from typing import *\n'
	cfg.flask_boilerplate += 'from flask_sqlalchemy import SQLAlchemy\n'
	cfg.flask_boilerplate += 'from flask_selfdoc import Autodoc\n'

	cfg.flask_boilerplate += 'app = Flask(__name__)\n'
	cfg.flask_boilerplate += 'CORS(app)\n'
	cfg.flask_boilerplate += 'auto = Autodoc(app)\n'

	# Database connection
	cfg.flask_boilerplate += f'app.config[\'SQLALCHEMY_DATABASE_URI\'] = \'{file_utils.get_full_db_file_path(True)}\'\n'
	cfg.flask_boilerplate += 'app.config[\'SQLALCHEMY_TRACK_MODIFICATIONS\'] = False\n'
	cfg.flask_boilerplate += 'db = SQLAlchemy(app)\n'

	# Generic database list {table(s)}.
	# Generic list table
	cfg.flask_boilerplate += '\n\nclass GenericList(db.Model):\n'
	cfg.flask_boilerplate += '\tid = db.Column(db.Integer, primary_key=True)\n'

	cfg.flask_boilerplate += '\n\tdef set_list(self, entry):\n'
	cfg.flask_boilerplate += '\t\tif entry:\n'
	cfg.flask_boilerplate += '\t\t\tfor item in entry:\n'
	cfg.flask_boilerplate += '\t\t\t\tself.push(item)\n'

	cfg.flask_boilerplate += '\n\tdef s(self):\n'
	cfg.flask_boilerplate += '\t\treturn {\n'
	cfg.flask_boilerplate += '\t\t\t\'id\': self.id,\n'
	cfg.flask_boilerplate += '\t\t\t\'list\': self.list()\n'
	cfg.flask_boilerplate += '\t\t}\n'

	cfg.flask_boilerplate += '\n\tdef list(self):\n'
	cfg.flask_boilerplate += '\t\treturn [self.get(item.index) for item in GenericListItem.query.filter_by(parent_id=self.id)]\n'

	cfg.flask_boilerplate += '\n\tdef push(self, item):\n'
	cfg.flask_boilerplate += '\t\tnew_item = GenericListItem(item, self.id)\n'
	cfg.flask_boilerplate += '\t\tdb.session.add(new_item)\n'
	cfg.flask_boilerplate += '\t\tdb.session.commit()\n'
	cfg.flask_boilerplate += '\n\t\treturn self.s()\n'

	cfg.flask_boilerplate += '\n\tdef get(self, index):\n'
	cfg.flask_boilerplate += '\t\titem = GenericListItem.query.filter_by(parent_id=self.id, index=index).first()\n'
	cfg.flask_boilerplate += '\n\t\treturn item.in_type()\n'

	cfg.flask_boilerplate += '\n\tdef remove(self, index):\n'
	cfg.flask_boilerplate += '\t\titem = GenericListItem.query.filter_by(parent_id=self.id, index=index).first()\n'
	cfg.flask_boilerplate += '\t\tdb.session.delete(item)\n'
	cfg.flask_boilerplate += '\t\tdb.session.commit()\n'

	# Generic list item table
	cfg.flask_boilerplate += '\n\nclass GenericListItem(db.Model):\n'
	cfg.flask_boilerplate += '\tid = db.Column(db.Integer, primary_key=True)\n'
	cfg.flask_boilerplate += '\tindex = db.Column(db.Integer)\n'
	cfg.flask_boilerplate += '\titem = db.Column(db.LargeBinary)\n'
	cfg.flask_boilerplate += '\tparent_id = db.Column(db.Integer)\n'

	cfg.flask_boilerplate += '\n\tdef __init__(self, item, parent_id):\n'
	cfg.flask_boilerplate += '\t\tself.item = pickle.dumps(item)\n'
	cfg.flask_boilerplate += '\t\tself.parent_id = parent_id\n'
	cfg.flask_boilerplate += '\t\tself.index = self.get_last_index() + 1\n'

	cfg.flask_boilerplate += '\n\tdef s(self):\n'
	cfg.flask_boilerplate += '\t\treturn {\n'
	cfg.flask_boilerplate += '\t\t\t\'id\': self.id,\n'
	cfg.flask_boilerplate += '\t\t\t\'index\': self.index,\n'
	cfg.flask_boilerplate += '\t\t\t\'item\': self.in_type(),\n'
	cfg.flask_boilerplate += '\t\t\t\'parent_id\': self.parent_id\n'
	cfg.flask_boilerplate += '\t\t}\n'

	cfg.flask_boilerplate += '\n\tdef get_last_index(self):\n'
	cfg.flask_boilerplate += '\t\tlast_item = GenericListItem.query.filter_by(parent_id=self.parent_id).order_by(db.desc(GenericListItem.id)).first()\n'

	cfg.flask_boilerplate += '\n\t\tif AskLibrary.exists(last_item):\n'
	cfg.flask_boilerplate += '\t\t\treturn last_item.index\n'
	cfg.flask_boilerplate += '\n\t\treturn -1\n'

	cfg.flask_boilerplate += '\n\tdef in_type(self):\n'
	cfg.flask_boilerplate += '\t\treturn pickle.loads(self.item)\n'

	# GenericList creation function
	cfg.flask_boilerplate += '\n\ndef generic_list_creator(entry: list or None = None):\n'
	cfg.flask_boilerplate += '\tgeneric_list = GenericList()\n'
	cfg.flask_boilerplate += '\tdb.session.add(generic_list)\n'
	cfg.flask_boilerplate += '\tdb.session.commit()\n'
	cfg.flask_boilerplate += '\n\tif entry:\n'
	cfg.flask_boilerplate += '\t\tgeneric_list.set_list(entry)\n'
	cfg.flask_boilerplate += '\n\treturn generic_list\n'

	# Ask's built-in functions
	cfg.flask_boilerplate += '\n\nclass AskLibrary:\n'

	cfg.flask_boilerplate += '\t@staticmethod\n'
	cfg.flask_boilerplate += '\tdef deep(obj, rule):\n'
	cfg.flask_boilerplate += '\t\trule_key = list(rule.keys())[0]\n'
	cfg.flask_boilerplate += '\t\trule_val = rule[rule_key]\n'
	cfg.flask_boilerplate += '\n\t\tfor element in obj:\n'
	cfg.flask_boilerplate += '\t\t\tif str(element[rule_key]) == str(rule_val):\n'
	cfg.flask_boilerplate += '\t\t\t\treturn element\n'

	cfg.flask_boilerplate += '\n\t@staticmethod\n'
	cfg.flask_boilerplate += '\tdef quick_set(target, source):\n'
	cfg.flask_boilerplate += '\t\tfor key in source.keys():\n'
	cfg.flask_boilerplate += '\t\t\tif key in target.keys():\n'
	cfg.flask_boilerplate += '\t\t\t\ttarget[key] = source[key]\n'
	cfg.flask_boilerplate += '\n\t\treturn target\n'

	cfg.flask_boilerplate += '\n\t# Deprecated method\n'
	cfg.flask_boilerplate += '\tdef quickSet(self, target, source):\n'
	cfg.flask_boilerplate += '\t\treturn self.quick_set(target, source)\n'

	cfg.flask_boilerplate += '\n\t@staticmethod\n'
	cfg.flask_boilerplate += '\tdef require_keys(required_keys, _dict):\n'
	cfg.flask_boilerplate += '\t\tstatuses = []\n'
	cfg.flask_boilerplate += '\t\tfor key in required_keys:\n'
	cfg.flask_boilerplate += '\t\t\tif key not in _dict:\n'
	cfg.flask_boilerplate += '\t\t\t\tstatuses.append(False)\n'
	cfg.flask_boilerplate += '\n\t\t\tstatuses.append(False)\n'
	cfg.flask_boilerplate += '\n\t\treturn False not in statuses\n'

	cfg.flask_boilerplate += '\n\t@staticmethod\n'
	cfg.flask_boilerplate += '\tdef status(message, code):\n'
	cfg.flask_boilerplate += '\t\treturn Response(message, status=code)\n'

	cfg.flask_boilerplate += '\n\t@staticmethod\n'
	cfg.flask_boilerplate += '\tdef respond(response):\n'
	cfg.flask_boilerplate += '\t\treturn jsonify(response)\n'

	cfg.flask_boilerplate += '\n\t@staticmethod\n'
	cfg.flask_boilerplate += '\tdef get_all_req():\n'
	cfg.flask_boilerplate += '\t\treq = {}\n'
	cfg.flask_boilerplate += '\t\tif request.json:\n'
	cfg.flask_boilerplate += '\t\t\tfor thing in request.json.keys():\n'
	cfg.flask_boilerplate += '\t\t\t\treq[thing] = request.json[thing]\n\n'
	cfg.flask_boilerplate += '\t\tif request.form:\n'
	cfg.flask_boilerplate += '\t\t\tfor thing in request.form.keys():\n'
	cfg.flask_boilerplate += '\t\t\t\treq[thing] = request.form[thing]\n\n'
	cfg.flask_boilerplate += '\t\tif request.args:\n'
	cfg.flask_boilerplate += '\t\t\tfor thing in request.args.keys():\n'
	cfg.flask_boilerplate += '\t\t\t\treq[thing] = request.args[thing]\n\n'
	cfg.flask_boilerplate += '\t\treturn req\n'

	cfg.flask_boilerplate += '\n\t@staticmethod\n'
	cfg.flask_boilerplate += '\tdef serialize(db_data):\n'
	cfg.flask_boilerplate += '\t\treturn [data.s() for data in db_data]\n'

	cfg.flask_boilerplate += '\n\t@staticmethod\n'
	cfg.flask_boilerplate += '\tdef exists(query):\n'
	cfg.flask_boilerplate += '\t\tif query is not None:\n'
	cfg.flask_boilerplate += '\t\t\tresult = False\n'
	cfg.flask_boilerplate += '\t\t\ttry:\n'
	cfg.flask_boilerplate += '\t\t\t\tresult = bool(query.scalar())\n'
	cfg.flask_boilerplate += '\t\t\texcept Exception:\n'
	cfg.flask_boilerplate += '\t\t\t\tresult = bool(query)\n'
	cfg.flask_boilerplate += '\t\t\treturn result\n'
	cfg.flask_boilerplate += '\t\treturn False\n'

	# Env, Environment cfg.variables, etc.
	cfg.flask_boilerplate += "\n\nclass Env:\n"

	cfg.flask_boilerplate += '\t@staticmethod\n'
	cfg.flask_boilerplate += "\tdef get(key):\n"
	cfg.flask_boilerplate += "\t\treturn os.environ.get(key)\n"

	# Auth, the JWT authentication system.
	cfg.flask_boilerplate += "\n\nclass Auth:\n"

	cfg.flask_boilerplate += "\tdef __init__(self):\n"
	cfg.flask_boilerplate += "\t\timport uuid\n"
	cfg.flask_boilerplate += "\n\t\tself.secret_key = uuid.uuid4().hex\n"
	cfg.flask_boilerplate += "\t\tself.token = jwt.encode({}, self.secret_key)\n"

	cfg.flask_boilerplate += "\n\tdef set_token(self, req_token):\n"
	cfg.flask_boilerplate += "\t\tself.token = req_token\n"

	cfg.flask_boilerplate += "\n\tdef login(self, user, expiry):\n"
	cfg.flask_boilerplate += "\t\tpayload = {\n"
	cfg.flask_boilerplate += "\t\t	'user': user,\n"
	cfg.flask_boilerplate += "\t\t	'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expiry)\n"
	cfg.flask_boilerplate += "\t\t}\n"
	cfg.flask_boilerplate += "\t\tself.encode(payload)\n"

	cfg.flask_boilerplate += "\n\tdef encode(self, payload):\n"
	cfg.flask_boilerplate += "\t\tself.token = jwt.encode(payload, str(self.secret_key))\n"

	cfg.flask_boilerplate += "\n\tdef decode(self):\n"
	cfg.flask_boilerplate += '\t\treturn jwt.decode(self.token, str(self.secret_key))\n'

	cfg.flask_boilerplate += "\n\tdef user(self):\n"
	cfg.flask_boilerplate += '\t\treturn self.decode()[\'user\']\n'

	# If decode AttributeError here, make sure that PyJWT is on 1.7.1.
	cfg.flask_boilerplate += "\n\tdef get_token(self):\n"
	cfg.flask_boilerplate += '\t\treturn self.token.decode(\'utf-8\')\n'

	cfg.flask_boilerplate += "\n\tdef is_valid(self):\n"
	cfg.flask_boilerplate += "\t\ttry:\n"
	cfg.flask_boilerplate += "\t\t\t_ = self.decode()\n"
	cfg.flask_boilerplate += "\t\t\treturn True\n"
	cfg.flask_boilerplate += "\t\texcept Exception:\n"
	cfg.flask_boilerplate += "\t\t\treturn False\n"

	# Hash, sha256 hashing.
	cfg.flask_boilerplate += '\n\nclass Hash:\n'

	cfg.flask_boilerplate += '\t@staticmethod\n'
	cfg.flask_boilerplate += '\tdef hash(to_hash):\n'
	cfg.flask_boilerplate += '\t\treturn hashlib.sha256(to_hash.encode(\'utf-8\')).hexdigest()\n'

	cfg.flask_boilerplate += '\n\t@staticmethod\n'
	cfg.flask_boilerplate += '\tdef check(the_hash, not_hashed_to_check):\n'
	cfg.flask_boilerplate += '\t\treturn Hash.hash(not_hashed_to_check) == the_hash\n'

	# Random, random number & choice generators.
	cfg.flask_boilerplate += '\n\nclass Random:\n'

	cfg.flask_boilerplate += '\t@staticmethod\n'
	cfg.flask_boilerplate += '\tdef int(start, end, count=1):\n'
	cfg.flask_boilerplate += '\t\tif end - start < count:\n'
	cfg.flask_boilerplate += '\t\t\traise ValueError("Integer count greater than the input range!")\n'
	cfg.flask_boilerplate += '\t\tif count > 1:\n'
	cfg.flask_boilerplate += '\t\t\treturn rand.sample(range(start, end), count)\n'
	cfg.flask_boilerplate += '\n\t\treturn rand.randint(start, end)\n'

	cfg.flask_boilerplate += '\n\t@staticmethod\n'
	cfg.flask_boilerplate += '\tdef __random_float(start, end, decimals):\n'
	cfg.flask_boilerplate += '\t\treturn round(rand.uniform(start, end), decimals)\n'

	cfg.flask_boilerplate += '\n\tdef float(self, start, end, count=1, decimals=16, unique=False):\n'
	cfg.flask_boilerplate += '\t\tif count <= 1:\n'
	cfg.flask_boilerplate += '\t\t\treturn self.__random_float(start, end, decimals)\n'
	cfg.flask_boilerplate += '\n\t\tfloats = []\n'
	cfg.flask_boilerplate += '\t\tfor _ in range(1, count + 1):\n'
	cfg.flask_boilerplate += '\t\t\tn = self.__random_float(start, end, decimals)\n'
	cfg.flask_boilerplate += '\t\t\tif unique:\n'
	cfg.flask_boilerplate += '\t\t\t\twhile n in floats:\n'
	cfg.flask_boilerplate += '\t\t\t\t\tn = self.__random_float(start, end, decimals)\n'
	cfg.flask_boilerplate += '\t\t\tfloats.append(n)\n'
	cfg.flask_boilerplate += '\n\t\treturn floats\n'

	cfg.flask_boilerplate += '\n\t@staticmethod\n'
	cfg.flask_boilerplate += '\tdef element(iterable, count=1, weights=None, unique=False):\n'
	cfg.flask_boilerplate += '\t\tif unique:\n'
	cfg.flask_boilerplate += '\t\t\treturn rand.sample(iterable, k=count)\n'
	cfg.flask_boilerplate += '\n\t\treturn rand.choices(iterable, weights=weights, k=count)\n'

	# Setting up global instances of the library classes.
	# There's also support for leading underscore syntax.
	cfg.flask_boilerplate += "\n\nauth = Auth()\n"
	cfg.flask_boilerplate += "_auth = auth\n"

	cfg.flask_boilerplate += "env = Env()\n"
	cfg.flask_boilerplate += "_env = env\n"

	cfg.flask_boilerplate += "hash = Hash()\n"
	cfg.flask_boilerplate += "_hash = hash\n"

	cfg.flask_boilerplate += "random = Random()\n"
	cfg.flask_boilerplate += "_random = random\n"

	# Decorator function for checking & validating the passed in token for protected routes.
	cfg.flask_boilerplate += "\n\ndef check_for_token(func):\n"
	cfg.flask_boilerplate += "\t@wraps(func)\n"
	cfg.flask_boilerplate += "\tdef wrapped(*args, **kwargs):\n"
	cfg.flask_boilerplate += "\t\ttoken = request.args.get('token')\n"
	cfg.flask_boilerplate += "\t\t_auth.set_token(token)\n"
	cfg.flask_boilerplate += "\t\tif not token:\n"
	cfg.flask_boilerplate += "\t\t\treturn jsonify({'message': 'Missing token!'}), 400\n"
	cfg.flask_boilerplate += "\t\ttry:\n"
	cfg.flask_boilerplate += "\t\t\t_ = jwt.decode(token, _auth.secret_key)\n"
	cfg.flask_boilerplate += "\t\texcept Exception:\n"
	cfg.flask_boilerplate += "\t\t\treturn jsonify({'message': 'Invalid token!'}), 401\n"
	cfg.flask_boilerplate += "\t\treturn func(*args, **kwargs)\n"
	cfg.flask_boilerplate += "\treturn wrapped\n"

	# Flask limiter setup.
	cfg.flask_boilerplate += '\n\nlimiter = Limiter(app, key_func=get_remote_address)'

	# Boilerplate code a the end of the output file (app.py).
	cfg.flask_end_boilerplate = '\n\n@app.route(\'/docs/\', methods=[\'GET\'], defaults={\'filter_type\': None})\n'
	cfg.flask_end_boilerplate += '@app.route(\'/docs/<filter_type>\', methods=[\'GET\'])\n'
	cfg.flask_end_boilerplate += '@auto.doc(\'public\')\n'
	cfg.flask_end_boilerplate += 'def get_docs(filter_type):\n'
	cfg.flask_end_boilerplate += '\tif filter_type:\n'
	cfg.flask_end_boilerplate += '\t\treturn auto.html(filter_type)\n'
	cfg.flask_end_boilerplate += '\treturn auto.html(groups=[\'public\', \'private\'])\n'

	# Boilerplate at the end of the script.
	cfg.flask_end_boilerplate += '\n\nif __name__ == \'__main__\':\n'
	if not cfg.uses_routes:
		cfg.flask_end_boilerplate += '\tmain()\n'
	cfg.flask_end_boilerplate += '\tapp.run()\n'
