import unittest, json
from datetime import datetime
from app import app, db, FitnessClass

#this is a simple test suite for the Flask app
class SimpleBookingTests(unittest.TestCase):
    #Runs Before Each Test case
    def setUp(self):
        app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI='sqlite:///:memory:')
        self.client = app.test_client()
        with app.app_context():
            db.create_all()
            cls = FitnessClass(
                name="Test Class",
                datetime_ist=datetime(2025, 8, 15, 10, 0),
                instructor="Test Instructor",
                available_slots=1
            )
            db.session.add(cls)
            db.session.commit()
            self.class_id = cls.id
    #Runs after Each Test case
    def tearDown(self):
        with app.app_context():
            db.drop_all()
   
    #make sure there is at least one class available
    def test_get_classes(self):
        self.assertTrue(len(self.client.get('/classes').get_json()) > 0)

    #test booking functionality - successful or not, code 201 success, 400 for errors
    def test_successful_booking(self):
        r = self.client.post('/book', json={"class_id": self.class_id, "client_name": "Alice", "client_email": "alice@example.com"})
        self.assertEqual(r.status_code, 201)

    #booking same class again - overbooking case
    def test_overbooking(self):
        payload = {"class_id": self.class_id, "client_name": "Bob", "client_email": "bob@example.com"}
        self.client.post('/book', json=payload)  # succeed
        self.assertEqual(self.client.post('/book', json=payload).status_code, 400)

    #test the booking retrieval functionality
    def test_get_bookings(self):
        self.client.post('/book', json={"class_id": self.class_id, "client_name": "Charlie", "client_email": "charlie@example.com"})
        self.assertTrue(any(b['class_name'] == "Test Class" for b in self.client.get('/bookings?email=charlie@example.com').get_json()))

if __name__ == "__main__":
    unittest.main()
