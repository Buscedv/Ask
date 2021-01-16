<img src="https://ask.edvard.dev/banner.png" alt="Ask">

# Ask

[![CircleCI](https://circleci.com/gh/circleci/circleci-docs.svg?style=svg)](https://circleci.com/gh/Buscedv/Ask)

A backend programming language. Ask makes it incredibly easy to create REST APIs. Ask directly transpiles to Flask so no new deployment procedures are needed. Ask focuses on clear readable code and reduces a lot of boilerplate code when working with e.g. databases and JWT authentication.

## Feature Highlights
- Built-in JWT (JSON web token) authentication.
- Simple database management.
- Syntax heavily inspired by Python.
- Transpiles to plain Flask with no extra modules, libraries, etc. needed.
- Built in CORS support.
- The transpiled code is completely standalone and is not dependent on any other files/modules or the ask.py file.
- Compatible with Python*

` * = You can import external Python modules and call them from you Ask code.`

## Example (Ask vs Flask)
Here is the same basic app with one GET route written in Ask and in Python with Flask.

### Ask
```php
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
```python3
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

## Get started
- Download the `ask.py` file. You can also download `ask-watcher.py` if you want to use live transpilation.
- Write your code in a `.ask` file
- Create a python virtual environment (optional): `python3 -m venv venv`
  - Activate it: `source venv/bin/activate`
- Download `requirements.txt`, and install the requirements (`pip install -r requirements.txt`)
- Transpile your code to Flask (Python) with `python3 ask.py [your file].ask`
- (Optional) If you want to use the watcher: `python3 ask-watcher.py [your file].ask`, the watcher by default uses a 5 second time out between checking your file, you can change this with an optional argument: `python3 ask-watcher.py [your file].ask [number of seconds, ex. 3]`

## Documentation
You can find the full documentation on [ask.edvard.dev](https://ask.edvard.dev)

## Contributing
Read more in the `CONTRIBUTING` file.

## Project structure
- `ask.py`: The Ask to Flask transpiler.
- `ask-watch.py`: A file watcher auto transpiler. Requires ask.py in the same directory.
- `docs/`: Ask's documentation website, built with Vue.js. Fetches the actual documentation from this repo's wiki.
