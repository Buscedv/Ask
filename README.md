# Ask
A backend programming language. Ask makes it incredibly easy to create REST apis. Ask directly transpiles to Flask so no new deployment procedures. Ask focuses on clear readable code and reduces a lot of boilerplate code when working with ex. databases.

# Example (Ask vs Flask)
Here is the same basic app with one GET route written in Ask and in Python with Flask.
YOu can clearly see the difference in how much code is needed for the Flask app compared to the Ask app.

### Ask
```php
$products = [
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
  respond({products: $products})
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
  return jsonify(products)
  
if __name__ == '__main__':
  app.run()
```
