from flask import Flask, jsonify, request, session
from functools import wraps
import jwt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'JustDemonstrating'


def check_for_token(func):
	@wraps(func)
	def wrapped(*args, **kwargs):
		token = request.args.get('token')

		if not token:
			return jsonify({'message': 'Missing Token'}), 403

		try:
			data = jwt.decode(token, app.config['SECRET_KEY'])
		except:
			return jsonify({'message': 'Invalid token'}), 403

		return func(*args, **kwargs)

	return wrapped


@app.route('/')
def index():
	if not session.get('logged_in'):
		return jsonify({'message': 'Not logged in!'})
	else:
		return jsonify({'message': 'You are logged in!'})


@app.route('/public')
def public():
	return 'Anyone can view this'


@app.route('/auth', methods=['GET'])
@check_for_token
def authorised():
	return 'This is only viewable with a token'


@app.route('/login', methods=['POST'])
def login():
	if request.json['username'] and request.json['password'] == 'password':
		session['logged_in'] = True
		token = jwt.encode({
				'user': request.json['username'],
				'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=30)
			},
			app.config['SECRET_KEY']
		)

		return jsonify({'token': token.decode('utf-8')})
	else:
		return jsonify({'message': 'Unable to verify'}), 403


if __name__ == '__main__':
	app.run()
