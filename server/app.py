#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os
from flask import jsonify

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants')
def restaurants():
    restaurants = []
    for restaurant in Restaurant.query.all():
        # restaurant_dict = restaurant.to_dict()
        restaurant_dict = {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address
        }
        restaurants.append(restaurant_dict)
        
    response = make_response(
        restaurants,
        200
    )
    
    return response
    
@app.route('/restaurants/<int:id>', methods=['GET', 'DELETE'])
def restaurant_by_id(id):
    restaurant =Restaurant.query.filter(Restaurant.id ==id).first()
    
    
    if not restaurant:
        return make_response({"error": "Restaurant not found"}, 404)
    
    if request.method == 'GET':
        restaurant_dict = restaurant.to_dict()
        restaurant_dict['restaurant_pizzas'] = []
        for rp in restaurant.restaurant_pizzas:
            rp_dict = rp.to_dict()
            rp_dict['pizza'] = rp.pizza.to_dict()
            restaurant_dict['restaurant_pizzas'].append(rp_dict)
        
        return make_response(restaurant_dict, 200)
    
    elif request.method == 'DELETE':
        db.session.delete(restaurant)
        db.session.commit()
        return make_response({
            'delete_successful': True,
            "message": "Restaurant deleted"
        }, 204)

        
@app.route('/pizzas')
def pizzas():
    pizzas = [] 
    
    for pizza in Pizza.query.all():
        pizza_dict = {
            "id": pizza.id,
            "ingredients": pizza.ingredients,
            "name": pizza.name
        }
        pizzas.append(pizza_dict)
        
    response = make_response(
        pizzas, 
        200
    )
    
    return response


@app.route('/restaurant_pizzas', methods=['GET', 'POST'])
def restaurant_pizzas():
    if request.method == 'GET':
        restaurant_pizzas = [rp.to_dict() for rp in RestaurantPizza.query.all()]
        return make_response(jsonify(restaurant_pizzas), 200)
    
    elif request.method == 'POST':
        data = request.get_json()
        if not data:
            return make_response(jsonify({"errors": ["Invalid input"]}), 400)

        price = data.get('price')
        pizza_id = data.get('pizza_id')
        restaurant_id = data.get('restaurant_id')

        if price is None or pizza_id is None or restaurant_id is None:
            return make_response(jsonify({"errors": ["Price, pizza_id, and restaurant_id are required"]}), 400)
        
        try:
            new_restaurant_pizza = RestaurantPizza(
                price=price,
                pizza_id=pizza_id,
                restaurant_id=restaurant_id
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            return make_response(jsonify(new_restaurant_pizza.to_dict()), 201)
        
        except ValueError:
            db.session.rollback()
            return make_response(jsonify({"errors": ["validation errors"]}), 400)
        
        except IntegrityError:
            db.session.rollback()
            return make_response(jsonify({"errors": ["Database integrity error"]}), 400)

        except Exception:
            db.session.rollback()
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

if __name__ == "__main__":
    app.run(port=5555, debug=True)