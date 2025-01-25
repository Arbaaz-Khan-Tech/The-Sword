from flask import Flask, Response, jsonify, render_template
import cv2
from ultralytics import YOLO
import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
app = Flask(__name__)



client = MongoClient('mongodb://localhost:27017/')
db = client['alert_database']
collection = db['alerts']



# Load models
violence_model = YOLO("viodec_mk1.pt")
arms_model = YOLO("arms_detect.pt")

violence_classes = ["Violence ","knife","guns","NonViolence"]  
arms_classes = ["Gun", "Knife", "Pistol", "Handgun", "Rifle"]

# Global variable to store detected objects
detected_objects = []

# Function to run inference on a frame
def detect_objects(frame):
    global detected_objects
    violence_results = violence_model(frame)
    arms_results = arms_model(frame)

    detected_objects.clear()  # Clear previous detections

    # Check for violence
    for result in violence_results:
        for box in result.boxes:
            class_id = int(box.cls)
            if violence_classes[class_id] == "Violence":
                detected_objects.append("Violence")

    # Check for arms
    for result in arms_results:
        for box in result.boxes:
            class_id = int(box.cls)
            if arms_classes[class_id] in arms_classes:
                detected_objects.append(arms_classes[class_id])

    return detected_objects

# Function to generate frames from webcam
def generate_frames():
    global detected_objects
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            detected_objects = detect_objects(frame)
            if detected_objects:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"Detected: {detected_objects} at {timestamp}")
                # Save frame with timestamp
                cv2.imwrite(f"detected_{timestamp}.jpg", frame)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detections')
def detections():
    global detected_objects
    return jsonify({"detected_objects": detected_objects})

@app.route('/')
def index():
    return render_template('/Police/Login.html')

@app.route("/citizen/geofencing")
def citizen_geofencing():
    return render_template("Citizen/geofencing.html")

@app.route("/citizen/incident-alerts")
def citizen_incident_alerts():
    return render_template("Citizen/incident-alerts.html")

@app.route("/citizen/real-time-map")
def citizen_real_time_map():
    return render_template("Citizen/real-time-map.html")

@app.route("/citizen/sos")
def citizen_sos():
    return render_template("Citizen/sos.html")

# Police Side Routes
@app.route("/police")
def police_index():
    return render_template("Police/index.html")

@app.route("/police/cctv-feeds")
def police_cctv_feeds():
    return render_template("Police/cctv-feeds.html")

@app.route("/police/crime-heatmap")
def police_crime_heatmap():
    return render_template("Police/crime-heatmap.html")

@app.route("/police/incident-report")
def police_incident_report():
    return render_template("Police/incident-report.html")

@app.route("/police/login")
def police_login():
    return render_template("Police/Login.html")

@app.route("/police/offender-database")
def police_offender_database():
    return render_template("Police/offender-database.html")

@app.route("/police/police-analytics")
def police_analytics():
    return render_template("Police/police-analytics.html")

@app.route("/police/sos-notifications")
def police_sos_notifications():
    return render_template("Police/sos-notifications.html")


@app.route("/Police/Missing_Person_Database")
def Police_Missing_Person_Database():
      return render_template("Police/Mpdb.html")

@app.route("/Police/Broadcast_Alert")    
def Police_Broadcast_Alert():
    return render_template("Police/Broadcast_Alert.html")  

@app.route('/submit_alert', methods=['POST'])
def submit_alert():
    # Get form data
    alert_data = {
        'alertType': request.form.get('alertType'),
        'alertTitle': request.form.get('alertTitle'),
        'alertMessage': request.form.get('alertMessage'),
        'alertLocation': request.form.get('alertLocation'),
        'alertDuration': int(request.form.get('alertDuration')),
        'targetAudience': request.form.getlist('targetAudience')
    }

    # Insert data into MongoDB
    result = collection.insert_one(alert_data)

    # Return a response
    return jsonify({
        'status': 'success',
        'message': 'Alert submitted successfully',
        'inserted_id': str(result.inserted_id)
    })

if __name__ == "__main__":
    app.run(debug=True)
