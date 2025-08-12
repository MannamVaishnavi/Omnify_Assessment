=> Omnify Assessment Project

This project is a simple Flask-based application that simulates a class booking system. It uses Python, Flask, SQLite, and SQLAlchemy to store and manage data, and returns responses in JSON format via REST APIs.

Features
- View available classes
- Book a class
- View all bookings
- Simple in-memory storage (data is reset when the server restarts)

Requirements
- Python 3.8 or later
- pip
- Virtual environment (optional but recommended to isolate dependencies)

Setup Instructions
1. Create a folder for the project on your local machine (explaining the way I created). Since the project doesn’t involve multiple collaborators, you can complete the entire work locally and make a single push to GitHub at the end.

2. Open a terminal and navigate to the project folder.

3. Create a virtual environment (optional by I recommend) - python -m venv venv

4. Activate the virtual environment:   venv\Scripts\activate

5. Start the Flask application: python app.py

You will see like this -

(venv) C:\Users\vaish\OneDrive\Documents\Omnify_Assessment>python app.py
 * Serving Flask app 'app'
 * Debug mode: on
2025-08-11 20:58:21,299 [INFO] - WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
2025-08-11 20:58:21,299 [INFO] - Press CTRL+C to quit
2025-08-11 20:58:21,299 [INFO] -  * Restarting with stat
2025-08-11 20:58:22,000 [WARNING] -  * Debugger is active!
2025-08-11 20:58:22,016 [INFO] -  * Debugger PIN: 142-889-475

6. Open your browser and go to: http://127.0.0.1:5000


API Endpoints (For Postman)

1. Get all classes
- Method: GET
- URL: http://127.0.0.1:5000/classes

2. Get all clients
- Method: GET
- URL: http://127.0.0.1:5000/clients

3. Get all bookings
- Method: GET
- URL: http://127.0.0.1:5000/bookings

4. Book a class  
- Method: POST  
- URL: http://127.0.0.1:5000/book  
- Headers: Content-Type: application/json  
- Body example:  
  {
    "class_id": 1,
    "client_name": "John Doe",
    "client_email": "john@example.com"
  }



Running Test suite
Save the code in test_app.py
Run the code using the unitttest command - python -m unittest test_app.py
You have to see "OK"or similar message which means the tests are passed.