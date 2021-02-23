<img src="https://ask.edvard.dev/banner.png" alt="Ask">

# Ask

[![CircleCI](https://circleci.com/gh/circleci/circleci-docs.svg?style=svg)](https://circleci.com/gh/Buscedv/Ask)

## Introduction.
Ask is an open source, dynamic, and transpiled programming language built for building backends and APIs. Ask directly transpiles to Python, more specifically Flask.

### Feature Highlights
- Built-in JWT Authentication.
- Super Simple Database Management.
- Syntax Inspired by Python.
- Built-in CORS Support.
- Reduces Boilerplate.
- Compatible with Python*

`* = You can import external Python modules and call them from you Ask code.`

## Easy to Learn
Ask's syntax is heavily inspired by Python, and can almost be considered to be a superset of Python. This means that picking up Ask is super easy if you’re already familiar with Python.

The main idea behind Ask is to simplify common backend actions (e.g. working with databases). Building a full database CRUD REST API with JWT authentication in Ask is very straight forward and simple and requires virtually zero lines of boilerplate code and no setup whatsoever.

## Extendable.
Ask is a transpiled language (kind of like TypeScript) which means that it compiles the source code to another language that has a similar level of abstraction. In Ask's case, the target language is Python, more specifically a Flask app.

Flask is a very popular and well-established web framework for Python, so there's already a lot of tools, and services for deploying Flask apps.

The transpiled app is completely standalone and doesn't require Ask in any way.

## Installation
- You can download Python from the PyPI.
- `$ pip install ask-lang`.
- Then run your apps with: `$ ask [your file].ask`.

## Example (Ask vs Flask)
Here is the same basic app with one GET route written in Ask and in Python with Flask.

### Ask
```python
products = [
  {
    name: 'Product 1',
    price: 30.0,
    qty: 300
  },
  {
    name: 'Product 2',
    price: 15.5,
    qty: 20
  }
]

@get('/api/v1/products'):
  respond({products: products})
```

### Flask
This is what the same application would look like in Flask.

```python
from flask import Flask, jsonify

app = Flask(__name__)

products = [
  {
    'name': 'Product 1',
    'price': 30.0,
    'qty': 300
  },
  {
    'name': 'Product 2',
    'price': 15.5,
    'qty': 20
  }
]

@app.route('/api/v1/products', methods=['GET'])
def get_products():
  return jsonify({'products': products})

if __name__ == '__main__':
  app.run()
```

As you can see Ask hides away all the clutter and boilerplate.

## Documentation
You can find the full documentation on [docs.ask-lang.org](https://docs.ask-lang.org)

## Contact
- Website: [ask-lang.org](https://ask-lang.org)
- Email: [me(a)edvard.dev](mailto:me@edvard.dev)
- GitHub: [Buscedv](https://github.com/Buscedv)
