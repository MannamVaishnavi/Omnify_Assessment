from flask import Flask, request, jsonify

app = Flask(__name__)

# Simple in-memory data
classes = [
    {"id": 1, "name": "Yoga", "datetime": "2025-08-15 18:00 IST", "instructor": "Alice", "available_slots": 10},
    {"id": 2, "name": "Zumba", "datetime": "2025-08-16 19:00 IST", "instructor": "Bob", "available_slots": 15},
    {"id": 3, "name": "HIIT", "datetime": "2025-08-17 17:00 IST", "instructor": "Carol", "available_slots": 8}
]

bookings = []  # will store bookings as dicts

@app.route('/classes', methods=['GET'])
def get_classes():
    return jsonify(classes)

@app.route('/book', methods=['POST'])
def book():
    data = request.json
    if not data or not all(k in data for k in ('class_id', 'client_name', 'client_email')):
        return jsonify({"error": "Missing fields"}), 400
    
    # Find the class
    fitness_class = next((c for c in classes if c['id'] == data['class_id']), None)
    if not fitness_class:
        return jsonify({"error": "Class not found"}), 404
    
    if fitness_class['available_slots'] <= 0:
        return jsonify({"error": "No slots available"}), 400
    
    # Book and reduce slot
    fitness_class['available_slots'] -= 1
    bookings.append({
        "class_id": fitness_class['id'],
        "client_name": data['client_name'],
        "client_email": data['client_email']
    })
    return jsonify({"message": "Booking successful"}), 201

@app.route('/bookings', methods=['GET'])
def get_bookings():
    email = request.args.get('email')
    if not email:
        return jsonify({"error": "Email query param required"}), 400
    
    user_bookings = []
    for b in bookings:
        if b['client_email'] == email:
            c = next((cls for cls in classes if cls['id'] == b['class_id']), None)
            if c:
                user_bookings.append({
                    "class_name": c['name'],
                    "datetime": c['datetime'],
                    "instructor": c['instructor']
                })
    return jsonify(user_bookings)

if __name__ == '__main__':
    app.run(debug=True)
