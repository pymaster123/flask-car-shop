from flask import Flask, abort, redirect, render_template, request, session, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
from datetime import datetime
import uuid
from decimal import Decimal
import re

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = "top secret password don't tell anyone this"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite3'
db = SQLAlchemy(app)


# Template filters
# Makes sure currency is well displayed with comma seperated values
@app.template_filter("currency")
def currency(value):
    try:
        return f"{float(value):,.2f}"
    except (TypeError, ValueError):
        return value


class CheckoutForm(FlaskForm):
    card_name = StringField('Name on card: ', validators=[DataRequired(), Length(max=100)])
    card_number = StringField('Card Number: ', filters=[
        lambda value: re.sub(r'[-/\s]', '', value) if value else value
    ], validators=[
        DataRequired(),
        Regexp(r'^\d{16}$', message='Card number must be 16 digits.')
    ])
    cvv = StringField('CVV: ', validators=[
        DataRequired(),
        Regexp(r'^\d{3,4}$', message='CVV must be 3 or 4 digits.')
    ])
    expiry = StringField('Expiry: ', validators=[
        DataRequired(),
        Regexp(r'^(0[1-9]|1[0-2])\/\d{2}$', message='Expiry must be in MM/YY format.')
    ])
    submit = SubmitField('Pay')


class Car(db.Model):
    __tablename__ = 'cars'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True, unique=True)
    price = db.Column(db.Numeric(10,2)) #This needs to be changed 
    description = db.Column(db.Text)

    imglink = db.Column(db.JSON) 

    # Other more specific car details
    mileage = db.Column(db.Integer, nullable=False, default=0)
    fuel_type = db.Column(db.String(16))
    horsepower = db.Column(db.Integer, nullable=False)
    engine_size = db.Column(db.Float, nullable=False)
    no_cylinders = db.Column(db.Integer, nullable=False)
    acceleration = db.Column(db.Float)
    year = db.Column(db.Integer, nullable=False)
    body_type = db.Column(db.String(16))
    no_seats = db.Column(db.Integer, nullable=False)
    gearbox = db.Column(db.String(16))
    co2_emissions = db.Column(db.Integer, nullable=False)
    top_speed_kph = db.Column(db.Integer)
    top_speed_mph = db.Column(db.Integer)


#This houses all baskets and who created them
class Basket(db.Model):
    __tablename__ = 'baskets'
    id = db.Column(db.Integer, primary_key=True)
    basket_token = db.Column(db.String(64), unique=True, index=True, nullable=False)
    status = db.Column(db.String(20), default="active", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class BasketItem(db.Model):
    __tablename__ = "basket_items"
    __table_args__ = (UniqueConstraint("basket_id", "car_id", name="uq_basket_car"),)

    id = db.Column(db.Integer, primary_key=True)
    basket_id = db.Column(db.Integer, db.ForeignKey("baskets.id"), nullable=False, index=True)
    car_id = db.Column(db.Integer, db.ForeignKey("cars.id"), nullable=False, index=True)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    unit_price = db.Column(db.Numeric(10,2), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    car = db.relationship("Car", backref="basket_items")


# Methods without routes: 
def get_or_create_basket_token():
    token = session.get("basket_token")
    if not token:
        token = uuid.uuid4().hex
        session["basket_token"] = token
    return token

def get_or_create_basket():
    token = get_or_create_basket_token()
    basket = Basket.query.filter_by(basket_token=token).first()
    if not basket:
        basket = Basket(basket_token=token)
        db.session.add(basket)
        db.session.commit()
    return basket

def is_in_basket(carID):
    basket = get_or_create_basket()
    return BasketItem.query.filter_by(basket_id=basket.id, car_id=carID).first() is not None

def sort_by_emissions(cars):
    return sorted(cars, key=lambda car: car.co2_emissions if car.co2_emissions is not None else float('inf'))

def sort_by_price(cars):
    return sorted(cars, key=lambda car: car.price if car.price is not None else float('inf'))

def sort_by_name(cars):
    return sorted(cars, key=lambda car: car.name)


@app.route('/', methods=['GET', 'POST'])
def galleryPage():
    cars = Car.query.all()
    basket = get_or_create_basket()
    basket_car_ids = {item.car_id for item in BasketItem.query.filter_by(basket_id=basket.id).all()}
    if request.args.get("sort"):
        if request.args.get("sort") == "emissions_asc":
            cars = sort_by_emissions(cars)
            return render_template('index.html', cars=cars, basket_car_ids=basket_car_ids)
        if request.args.get("sort")  == "price_asc":
            cars = sort_by_price(cars)
            return render_template('index.html', cars=cars, basket_car_ids=basket_car_ids)
        if request.args.get("sort") == "name":
            cars = sort_by_name(cars)
            return render_template('index.html', cars=cars, basket_car_ids=basket_car_ids)
    else:
        return render_template('index.html', cars=cars, basket_car_ids=basket_car_ids)
    
@app.route('/tyres')
def tyresPage():
    return render_template('TyresPage.html')

@app.route('/partners')
def partnersPage():
    return render_template('PartnersPage.html')

@app.route('/about')
def aboutPage():
    return render_template('AboutUs.html')

@app.route('/car/<int:carID>')
def singleProductPage(carID):
    car = Car.query.get_or_404(carID)

    features={
        "Mileage": car.mileage,
        "Fuel Type": car.fuel_type,
        "Horsepower": car.horsepower,
        "Engine Size": car.engine_size,
        "Number of Cylinders": car.no_cylinders,
        "Acceleration": car.acceleration,
        "Year": car.year,
        "Body Type": car.body_type,
        "Number of Seats": car.no_seats,
        "Gearbox": car.gearbox,
        "CO2 Emissions (g/km)": car.co2_emissions,
        "Top Speed (kph)": car.top_speed_kph,
        "Top Speed (mph)": car.top_speed_mph
    }

    car_in_basket = is_in_basket(car.id)
    return render_template('SingleCar.html', car=car, features=features, is_in_basket=car_in_basket)


@app.route('/basket')
def basketPage():
    basket = get_or_create_basket()
    items = BasketItem.query.filter_by(basket_id=basket.id).all()
    total = Decimal('0.00')

    
    for item in items:
        #should print all items names in a list, also displaying prices
        try:
            total += item.unit_price
        except(TypeError, ValueError):
            pass

    if total > 0:
        checkout_possible = True
    else:
        checkout_possible = False

    return render_template('basket.html', items=items, total=total, basket=basket, checkout_possible=checkout_possible)


@app.route('/basket/add/<int:carID>')
def add_to_basket(carID):
    car = Car.query.get_or_404(carID)

    basket = get_or_create_basket()
    existing_item = BasketItem.query.filter_by(basket_id=basket.id, car_id=car.id).first()
    if existing_item:
        db.session.delete(existing_item)
    else:
        new_item = BasketItem(basket_id=basket.id, car_id=car.id, unit_price=car.price)
        db.session.add(new_item)

    db.session.commit()
    return redirect(request.referrer or url_for('galleryPage'))

@app.route('/basket/checkout/<int:BasketID>', methods=['GET', 'POST'])
def checkout(BasketID):
    token = get_or_create_basket_token()
    basket = Basket.query.filter_by(id=BasketID, basket_token=token).first()
    if basket is None:
        abort(404)

    items = BasketItem.query.filter_by(basket_id=basket.id).all()
    if not items:
        return redirect(url_for('basketPage'))

    total = Decimal('0.00')
    for item in items:
        try:
            total += item.unit_price
        except (TypeError, ValueError):
            pass

    form = CheckoutForm()
    if form.validate_on_submit():
        basket.status = "completed"
        # collect purchased car ids before deleting basket items
        purchased_car_ids = [item.car_id for item in items]

        # remove basket items for this basket
        BasketItem.query.filter_by(basket_id=basket.id).delete()

        # remove purchased cars from inventory
        for cid in purchased_car_ids:
            car = Car.query.get(cid)
            if car:
                db.session.delete(car)

        db.session.commit()

        session.pop("basket_token", None) # get rid of the basket token
        return redirect(url_for('paymentSuccessfulPage'))

    return render_template('checkout.html', basketID=BasketID, form=form, items=items, total=total)


@app.route('/basket/checkout/success')
def paymentSuccessfulPage():
    return render_template('paymentSuccessful.html')


        



if __name__ == '__main__':
    app.run(debug=True)

# if __name__ == '__main__':
#     app.run(host='0.0.0.0')


# Image Citations/References:

# AM One 77
# can use:
# https://upload.wikimedia.org/wikipedia/commons/2/25/2011_Aston_Martin_One-77.jpg , https://commons.wikimedia.org/wiki/File:2011_Aston_Martin_One-77.jpg
# https://live.staticflickr.com/7362/14018247232_9297bffa07_b.jpg , https://www.flickr.com/photos/niki2203/14018247232
# https://upload.wikimedia.org/wikipedia/commons/f/fd/Aston_Martin_One-77_in_London.jpg , https://commons.wikimedia.org/wiki/File:Aston_Martin_One-77_in_London.jpg
# https://live.staticflickr.com/6172/6224145327_524835c47b_b.jpg , https://www.flickr.com/photos/pcw/6224145327

# Can use these ones:
# https://upload.wikimedia.org/wikipedia/commons/3/35/RM_Sotheby%E2%80%99s_2017_-_Mercedes-Benz_SLS_AMG_black_series_-_2014_-_009.jpg
# https://upload.wikimedia.org/wikipedia/commons/0/09/Yellow_Mercedes-Benz_SLS_Black_Series_%2812596911064%29.jpg
# https://commons.wikimedia.org/wiki/File:2014_Mercedes-Benz_SLS_AMG_Black_Series_%288403236103%29.jpg
# https://upload.wikimedia.org/wikipedia/commons/e/ed/Mercedes-Benz_SLS_AMG_Black_%288388537382%29.jpg
# https://upload.wikimedia.org/wikipedia/commons/e/e7/Mercedes-Benz_SLS_AMG_Black_Series_%28C197%2C_2013%29_%2852871988726%29.jpg



# AM DB5
# https://media.astonmartin.com/wp-content/uploads/2024/10/c721def2fc216147685bc54b9aea563c-m.png
# https://upload.wikimedia.org/wikipedia/commons/a/a0/1964_Aston_Martin_DB5_4.0_Front.jpg
# https://upload.wikimedia.org/wikipedia/commons/4/41/1965_Aston_Martin_DB5_SCD_24-resized2.jpg
# https://upload.wikimedia.org/wikipedia/commons/3/39/1964_Aston_Martin_DB5_4.0_Rear.jpg
# https://upload.wikimedia.org/wikipedia/commons/6/63/110_ans_de_l%27automobile_au_Grand_Palais_-_Aston_Martin_DB5_Sports_Saloon_-_1964_-_011.jpg
# https://upload.wikimedia.org/wikipedia/commons/c/ca/Aston_Martin_DB5_1965_interior_Kip_Cyprus.png
# https://upload.wikimedia.org/wikipedia/commons/e/e3/Paris_-_RM_Sotheby%E2%80%99s_2016_-_Aston_Martin_DB5_-_1963_-_007.jpg

# AM Vanquish Zagato
# https://upload.wikimedia.org/wikipedia/commons/2/2c/2019_Aston_Martin_Vanquish_Zagato_Shooting_Brake_no_73_at_Greenwich_2019%2C_front_left.jpg , https://commons.wikimedia.org/wiki/File:2019_Aston_Martin_Vanquish_Zagato_Shooting_Brake_no_73_at_Greenwich_2019,_front_left.jpg
# https://upload.wikimedia.org/wikipedia/commons/4/4b/2019_Aston_Martin_Vanquish_Zagato_Shooting_Brake_no_73_at_Greenwich_2019%2C_rear_right.jpg , https://commons.wikimedia.org/wiki/File:2019_Aston_Martin_Vanquish_Zagato_Shooting_Brake_no_73_at_Greenwich_2019,_rear_right.jpg
# https://upload.wikimedia.org/wikipedia/commons/1/18/2019_Aston_Martin_Vanquish_Zagato_Shooting_Brake_no_73_at_Greenwich_2019%2C_rear_left.jpg, https://commons.wikimedia.org/wiki/File:2019_Aston_Martin_Vanquish_Zagato_Shooting_Brake_no_73_at_Greenwich_2019,_rear_left.jpg