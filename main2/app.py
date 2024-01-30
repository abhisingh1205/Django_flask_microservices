from dataclasses import dataclass
from flask import Flask, request, jsonify, make_response, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
from os import environ
import requests
from producer import publish


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@flask_db:5432/postgres'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

@dataclass
class Product(db.Model):
    id: int
    title: str
    image: str

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    title = db.Column(db.String(200))
    image = db.Column(db.String(200))

    def json(self):
        return {'id': self.id, 'title': self.title, 'image': self.image}

@dataclass
class ProductUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    product_id = db.Column(db.Integer)

    UniqueConstraint('user_id', 'product_id', name='user_product_unique')

#db.drop_all()
#db.create_all()

#Test route
@app.route('/test', methods=['GET'])
def test():
    return make_response(jsonify({'message': 'test response'}), 200)

@app.route('/products', methods=['POST'])
def create_product():
    try:
        data = request.get_json()
        new_product = Product(title=data['title'], image=data['image'])
        db.session.add(new_product)
        db.session.commit()

        return make_response(jsonify({'message': 'product created'}), 201)
    except Exception as e:
        return make_response(jsonify({'message': 'unable to create product'}), 500)
    
@app.route('/products', methods=['GET'])
def get_all_products():
    try:
        products = Product.query.all()
        return make_response(jsonify({'products': [product.json() for product in products]}), 200)
    except:
        return make_response(jsonify({'message': 'unable to get products'}), 500)
    
@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    try:
        product = Product.query.filter_by(id=id).first()
        return make_response(jsonify({'product': product.json()}), 200)
    except:
        return make_response(jsonify({'message': 'unable to get products'}), 500)
    
@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    try:
        product = Product.query.filter_by(id=id).first()
        if product:
            data = request.get_json()
            product.title = data['title']
            product.image = data['image']
            db.session.commit()
            return make_response(jsonify({'message': 'Product updated'}), 200)
        else:
            return make_response(jsonify({'message': 'Product not found'}), 404)
    except:
        return make_response(jsonify({'message': 'unable to update product'}), 500)
    
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    try:
        product = Product.query.filter_by(id=id).first()
        if product:
            db.session.delete(product)
            db.session.commit()
            return make_response(jsonify({'message': 'Product deleted'}), 200)
        else:
            return make_response(jsonify({'message': 'Product not found'}), 404)
    except:
        return make_response(jsonify({'message': 'unable to delete product'}), 500)
    
@app.route('/products/<int:id>/like', methods=['POST'])
def like(id):
    print("Inside method")
    req = requests.get('http://docker.for.mac.localhost:8000/api/user/')
    json = req.json()

    try:
        product_user = ProductUser(user_id=json['id'], product_id=id)
        db.session.add(product_user)
        db.session.commit()

        #event
        publish('product_liked', id)
    except:
        abort(400, 'You already liked this product')
    return jsonify({
        'message': 'success'
    })
    




