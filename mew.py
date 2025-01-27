from pymongo import MongoClient

mongo_con = "mongodb://localhost:27017"
client = MongoClient(mongo_con)
db = client["SurakshaSetu"]
Alert_Collection = db["Alerts"]

alert_data = {
    'alertType': 'Test Alert',
    'alertTitle': 'Test Title',
    'alertMessage': 'This is a test message',
    'alertLocation': 'Test Location',
    'alertDuration': 30,
    'targetAudience': ['Public', 'Officials']
}

result = Alert_Collection.insert_one(alert_data)
print("Inserted ID:", result.inserted_id)
