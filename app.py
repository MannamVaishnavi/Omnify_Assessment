"""
Fitness Studio Booking API
Requirements: Flask, Flask_SQLAlchemy, pytz
""" 

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
import logging
import re
import os

# here we are setting up the app and DB
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitness.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
db = SQLAlchemy(app)


# all the models are defined here

#class model
class FitnessClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    datetime_ist = db.Column(db.DateTime, nullable=False)  # stored as IST-aware datetime
    instructor = db.Column(db.String(80), nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)

#booking model
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('fitness_class.id'), nullable=False)
    client_name = db.Column(db.String(80), nullable=False)
    client_email = db.Column(db.String(120), nullable=False)


# helper functions and constants
EMAIL_RE = re.compile(r"[^@]+@[^@]+\.[^@]+")

def is_valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email))

IST = pytz.timezone("Asia/Kolkata")

def to_ist(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return IST.localize(dt)
    else:
        return dt.astimezone(IST)

def convert_timezone(dt_ist: datetime, target_tz: str) -> datetime:
    try:
        tz = pytz.timezone(target_tz)
    except Exception:
        logging.warning(f"Unknown timezone '{target_tz}' — returning IST time.")
        tz = IST
    # ensure dt_ist is IST-aware
    if dt_ist.tzinfo is None:
        dt_ist = IST.localize(dt_ist)
    return dt_ist.astimezone(tz)


# routes or API end points are defined here

#home route
@app.route("/")
def home():
    return jsonify({"message": "Welcome to our OMNIFY Fitness Class Booking API"}), 200

#classes route
@app.route("/classes", methods=["GET"])
def get_classes():
    # GET/classes?tz=America/New_York
    # Returns a list of classes with times converted to requested tz (default IST)
    target_tz = request.args.get("tz", "Asia/Kolkata")
    classes = FitnessClass.query.order_by(FitnessClass.datetime_ist).all()
    result = []
    for c in classes:
        local_dt = convert_timezone(c.datetime_ist, target_tz)
        result.append({
            "id": c.id,
            "name": c.name,
            "datetime": local_dt.strftime("%Y-%m-%d %H:%M %Z"), #making the date human readoble and easy to display 
            "instructor": c.instructor,
            "available_slots": c.available_slots
        })
    logging.info("Returned classes list.")
    return jsonify(result), 200

# route to book a class
@app.route("/book", methods=["POST"])
def book_class():
    # POST /book
    # JSON body: { "class_id": int, "client_name": str, "client_email": str }
    data = request.get_json(silent=True)
    #checking data received or not
    if not data:
        logging.error("Booking failed — no JSON body provided.")
        return jsonify({"error": "JSON body required"}), 400

    # checking all the required fields received or not
    if not all(k in data for k in ("class_id", "client_name", "client_email")):
        logging.error("Booking failed — missing fields.")
        return jsonify({"error": "Missing required fields: class_id, client_name, client_email"}), 400

    # type & format checks
    try:
        class_id = int(data["class_id"])
    except Exception:
        return jsonify({"error": "class_id must be an integer"}), 400

    client_name = str(data["client_name"]).strip()
    client_email = str(data["client_email"]).strip()
    if not client_name:
        return jsonify({"error": "client_name cannot be empty"}), 400
    if not is_valid_email(client_email):
        return jsonify({"error": "Invalid email format"}), 400

    fitness_class = FitnessClass.query.get(class_id)
    if not fitness_class:
        logging.error(f"Booking failed — class id {class_id} not found.")
        return jsonify({"error": "Class not found"}), 404

    if fitness_class.available_slots <= 0:
        logging.info(f"Booking failed — no slots left for '{fitness_class.name}'.")
        return jsonify({"error": "No slots available"}), 400

    # if everything is fine then perform booking
    fitness_class.available_slots -= 1
    booking = Booking(class_id=fitness_class.id, client_name=client_name, client_email=client_email)
    db.session.add(booking)
    db.session.commit()

    logging.info(f"Booking successful — {client_name} ({client_email}) booked '{fitness_class.name}'.")
    return jsonify({"message": "Booking successful"}), 201

#bookings route -extract bookings for a given email
@app.route("/bookings", methods=["GET"])
def get_bookings():
    #GET /bookings?email=someone@example.com&tz=America/New_York
    #Returns bookings for the given email (tz optional)
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Email query parameter required"}), 400
    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400
    target_tz = request.args.get("tz", "Asia/Kolkata")

    bookings = Booking.query.filter_by(client_email=email).all()
    result = []
    for b in bookings:
        cls = FitnessClass.query.get(b.class_id)
        if not cls:
            continue
        local_dt = convert_timezone(cls.datetime_ist, target_tz)
        result.append({
            "class_name": cls.name,
            "datetime": local_dt.strftime("%Y-%m-%d %H:%M %Z"),
            "instructor": cls.instructor
        })
    logging.info(f"Returned {len(result)} bookings for {email}.")
    return jsonify(result), 200


# inout data seeding function
def seed_data(force: bool = False):
    # Create tables and add sample classes if none exist
    # Call this once at startup
    db.create_all()
    if force or not FitnessClass.query.first():
        # sample classes (IST times)
        samples = [
            ("Morning Yoga", datetime(2025, 8, 15, 7, 0)),
            ("Evening Yoga", datetime(2025, 8, 15, 18, 0)),
            ("Zumba Dance", datetime(2025, 8, 16, 17, 30)),
            ("Pilates Core", datetime(2025, 8, 17, 6, 30)),
            ("HIIT Blast", datetime(2025, 8, 17, 19, 0)),
        ]
        db.session.query(Booking).delete()
        db.session.query(FitnessClass).delete()
        for name, naive_dt in samples:
            ist_dt = IST.localize(naive_dt)  # make IST-aware
            cls = FitnessClass(
                name=name,
                datetime_ist=ist_dt,
                instructor="Instructor " + name.split()[0],
                available_slots=12
            )
            db.session.add(cls)
        db.session.commit()
        logging.info("Seeded sample fitness classes into database.")


# start the app
if __name__ == "__main__":
    # Ensure working dir is file's directory (helpful when running from IDE)
    # os.chdir(os.path.dirname(os.path.abspath(__file__)) or ".")
    with app.app_context():
        seed_data()   # <-- seed once on startup
    logging.info("Starting Flask app... Visit http://127.0.0.1:5000/classes")
    app.run(debug=True)
