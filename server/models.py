from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"
     # add serialization rules
    serialize_rules = ('-restaurant_pizzas.restaurant', '-restaurant_pizzas.pizza')
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # add relationship
    restaurant_pizzas = db.relationship(
        'RestaurantPizza', back_populates = 'restaurant', cascade = "all, delete-orphan"
    )

    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"
    # add serialization rules
    serialize_rules = ('-restaurant_pizzas.pizza', '-restaurant_pizzas.restaurant')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # add relationship
    restaurant_pizzas = db.relationship(
        'RestaurantPizza', back_populates = 'pizza', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = 'restaurant_pizzas'
    
    serialize_rules = ('-pizza.restaurant_pizzas', '-restaurant.restaurant_pizzas')

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    # Foreign Key to store the pizza id
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'))
    # Foreign Key to store the restaurant id
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))

    # Relationship mapping the restaurantpizza to related to pizza
    pizza = db.relationship('Pizza', back_populates='restaurant_pizzas')
    # Relationship mapping the restaurantpizza to related to restaurant
    restaurant = db.relationship('Restaurant', back_populates='restaurant_pizzas')

    @validates('price')
    def validate_price(self, key, value):
        if not isinstance(value, int) or not (1 <= value <= 30):
            raise ValueError("Price must be an integer between 1 and 30")
        return value
    

