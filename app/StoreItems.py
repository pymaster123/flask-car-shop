'''Script to populate the database with some initial data.
   In reality you would probably create a separate editor or a tool for importing data from elsewhere,
   but for CM1102 we'll just use this script to populate the database.'''

from myapp import app, db, Car

cars = [
    {"name": "Aston Martin One-77", 
     "price": 2960000.00, 
     "description": "1 of 77 cars built. This is in pearl white, looks amazing.", 
     "imglink": ["AMOne77front1.jpg", "AMOne77front2.jpg", "AMOne77interior1.jpg", "AMOne77rear1.jpg"],
     "mileage": 2000,
     "fuel_type": "Petrol",
     "horsepower": 750,
     "engine_size": 7.3,
     "no_cylinders": 12,
     "acceleration": 3.5,
     "year": 2012,
     "body_type": "Coupe",
     "no_seats": 2,
     "gearbox": "Automatic",
     "co2_emissions": 572,
     "top_speed_kph": 354,
     "top_speed_mph": 220,
     },
    {"name": "Mercedes SLS Black Series", 
     "price": 500000.00, 
     "description": "Mercedes SLS: 1 of 350 ever made", 
     "imglink": ["MercSLSBlackSYellowfront1.jpg", "MercSLSBlackSYellowfront2.jpg", "MercSLSBlackSYellowrear1.jpg", "MercSLSBlackSYellowside1.jpg", "MercSLSBlackSinterior1.jpg"],
     "mileage": 5024,
     "fuel_type": "Petrol",
     "horsepower": 622,
     "engine_size": 6.2,
     "no_cylinders": 8,
     "acceleration": 3.6,
     "year": 2013,
     "body_type": "Coupe",
     "no_seats": 2,
     "gearbox": "Automatic",
     "co2_emissions": 321,
     "top_speed_kph": 315,
     "top_speed_mph": 196,
     },
    {"name": "Aston Martin DB5", 
     "price": 700000.00, 
     "description": "Released in 1963, and used in the James Bond movie, Goldfinger, in 1964. Very special and pretty car with low mile.", 
     "imglink": ["AstonMartinDB5front1.webp", "AstonMartinDB5front2.jpg", "AstonMartinDB5interior1.png", "AstonMartinDB5interior2.jpg", "AstonMartinDB5rear1.jpg", "AstonMartinDB5front3.jpg", "AstonMartinDB5front4.jpg"],
     "mileage": 1540,
     "fuel_type": "Petrol",
     "horsepower": 282,
     "engine_size": 4,
     "no_cylinders": 6,
     "acceleration": 7.1,
     "year": 1963,
     "body_type": "Coupe",
     "no_seats": 2,
     "gearbox": "Manual",
     "co2_emissions": 350,
     "top_speed_kph": 229,
     "top_speed_mph": 142,
     },
     {"name": "Aston Martin Vanquish Zagato 2019", 
     "price": 700000.00, 
     "description": "Very special car from 2019. This car is nearly perfect, with only 1540 miles on the clock. It has a powerful V12 engine and a stunning design by Zagato.", 
     "imglink": ["AMVanquishZagatofront1.jpg", "AMVanquishZagatorear1.jpg", "AMVanquishZagatoside1.jpg"],
     "mileage": 1540,
     "fuel_type": "Petrol",
     "horsepower": 282,
     "engine_size": 4,
     "no_cylinders": 6,
     "acceleration": 7.1,
     "year": 2019,
     "body_type": "Coupe",
     "no_seats": 2,
     "gearbox": "Manual",
     "co2_emissions": 350,
     "top_speed_kph": 229,
     "top_speed_mph": 142,
     }
]

# Bear in mind this script does NOT run the app
# instead we use app.app_context() which Flask provides to allow us to use the app's configuration and extensions
with app.app_context():
    db.create_all() # creates the empty tables
    
    for car in cars:
        existing_car = Car.query.filter_by(name=car["name"]).first()
        if existing_car is None:
            newCar = Car(name=car["name"], price=car["price"], description=car["description"], imglink=car["imglink"], 
                    mileage=car["mileage"], fuel_type=car["fuel_type"], horsepower=car["horsepower"], engine_size=car["engine_size"], 
                    no_cylinders=car["no_cylinders"], acceleration=car["acceleration"], year=car["year"], body_type=car["body_type"], 
                    no_seats=car["no_seats"], gearbox=car["gearbox"], co2_emissions=car["co2_emissions"], top_speed_kph=car["top_speed_kph"], 
                    top_speed_mph=car["top_speed_mph"])
            db.session.add(newCar)
    
    db.session.commit()