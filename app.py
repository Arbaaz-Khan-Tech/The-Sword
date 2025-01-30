
from flask import Flask, Response, render_template, redirect, url_for
from flask_socketio import SocketIO, emit
import cv2
from ultralytics import YOLO
import threading
from flask import Flask, jsonify, request
from pymongo import MongoClient
import json
import os
from bson import ObjectId

import uuid



import logging
from flask_socketio import SocketIO
import pywhatkit as kit


import datetime

import json


# Load data from JSON file
with open('config.json', 'r') as file:
    config = json.load(file)

# Access the phone number
phone_number = config.get('phone_number')



app = Flask(__name__)
socketio = SocketIO(app)


# Set the logging level to ERROR
app.logger.setLevel(logging.ERROR)


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
    # camera_url = "https://192.168.137.220:4343/video"  # Replace with the URL shown in the app
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


#created a connection to MongoDB
mongo_con="mongodb://localhost:27017"
client=MongoClient(mongo_con)
db=client["SurakshaSetu"]

alerts_collection = db["Alerts_Citizen"]  # For citizen-submitted reports jaha verify ke baad incident me jayega
incidents_collection = db["Incidents"]  # For police-submitted reports
Alert_Collection = db["Alerts"]
markers_collection = db["Markers"]
heatmap_collection = db["Heatmap"]




@app.route('/')
def index():
    return render_template('/Police/Login.html')

@app.route("/citizen/rewards")
def citizen_community_engagement():
    return render_template("Citizen/rewards.html")


@app.route("/citizen/geofencing")
def citizen_geofencing():
    return render_template("Citizen/geofencing.html")

@app.route("/Citizen/alerts") 
def citizen_alerts():
    return render_template("/Citizen/Alerts.html")

@app.route('/citizen/alerts/data', methods=['GET'])
def fetch_citizen_alerts():
    try:
        alerts = list(Alert_Collection.find().sort('_id', -1))
        for alert in alerts:
            alert['_id'] = str(alert['_id'])  # Convert ObjectId to string
        return jsonify({'status': 'success', 'alerts': alerts})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    

@app.route("/citizen/incident-alerts", methods=["GET"])
def citizen_incident_alerts():
    incidents = list(incidents_collection.find().sort("created_at", -1))
    print("Retrieved incidents:", incidents)
    for incident in incidents:
        incident["_id"] = str(incident["_id"])
    return render_template("Citizen/incident-alerts.html", incidents=incidents)

@app.route("/citizen/incident-report", methods=["GET", "POST"])
def citizen_incident_report():
    if request.method == "POST":
        try:
            # Log form and file data
            print("Form data received:", request.form)
            print("Files received:", request.files)

            # Extract data from form
            incident_type = request.form.get("incidentType")
            date_time = request.form.get("dateTime")
            location = request.form.get("location")
            reporting_citizen = request.form.get("reportingCitizen")
            status_type = "pending"  # Default status for the incident
            priority_type = request.form.get("priorityType")
            notice = request.form.get("notice")
            description = request.form.get("description")

            # Handle file uploads
            evidence_files = request.files.getlist("evidence")
            evidence_file_paths = []
            evidence_dir = "static/uploads/evidence"  # Save in the static directory
            os.makedirs(evidence_dir, exist_ok=True)

            for evidence in evidence_files:
                if evidence.filename != "":
                    file_path = os.path.join(evidence_dir, evidence.filename)
                    evidence.save(file_path)
                    # Save public URL for the file
                    evidence_file_paths.append(f"/static/uploads/evidence/{evidence.filename}")
                    print(f"Saved file: {file_path}")

            # Create a document to insert into the Alerts collection
            alert_data = {
                "alert_id": str(uuid.uuid4()),  # Generate a unique alert ID
                "incident_type": incident_type,
                "date_time": date_time,
                "location": location,
                "reporting_citizen": reporting_citizen,
                "status_type": status_type,
                "priority_type": priority_type,
                "notice": notice,
                "description": description,
                "evidence_files": evidence_file_paths,
                "report_status": "pending",  # New field to indicate the status of the report
                
                
            }

            # Insert into the Alerts collection
            result = alerts_collection.insert_one(alert_data)
            print(f"Document inserted with ID: {result.inserted_id}")

            # Return a success response with the alert ID
            return jsonify({
                "message": "Incident report submitted successfully and is pending approval.",
                "alert_id": str(result.inserted_id),
            }), 201
        except Exception as e:
            print(f"Error during submission: {e}")
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    # Render the form for GET requests
    return render_template("Citizen/incident-report.html")

@app.route("/citizen/real-time-map")
def citizen_real_time_map():
    return render_template("Citizen/real-time-map.html")

@app.route("/citizen/safewalk")
def citizen_safewalk():
    return render_template("Citizen/safewalk.html")

@app.route("/citizen/sos")
def citizen_sos():
    return render_template("Citizen/sos.html")

@app.route("/citizen/crime-heatmap")
def citizen_crime_heatmap():
    return render_template("Citizen/crime-heatmap.html")

@app.route("/api/crime-data")
def get_crime_data():
    return jsonify(list(db.heatmap.find({}, {"_id": 0})))

@app.route("/api/report-crime", methods=["POST"])
def report_crime():
    db.heatmap.insert_one(request.json)
    return jsonify({"message": "Crime location saved!"})

@app.route("/Citizen")
def citizen_Index():
    return render_template("Citizen/index.html")

# Police Side Routes
@app.route("/police")
def police_index():
    return render_template("Police/index.html")

@app.route("/police/cctv-feeds")
def police_cctv_feeds():
    return render_template("Police/cctv-feeds.html")

@app.route("/police/crime-locator")
def police_crime_locator():
    return render_template("Police/crime-locator.html")

@app.route("/police/crime-heatmap")
def police_crime_heatmap():
    return render_template("Police/crime-heatmap.html")

@app.route("/police/incident-verify", methods=["GET", "POST"])
def police_incident_verify():
    if request.method == "GET":
        try:
            # Fetch all incidents with status "pending" from the Alerts collection
            pending_alerts = list(alerts_collection.find({"report_status": "pending"}).sort("created_at", -1))
            for alert in pending_alerts:
                alert["_id"] = str(alert["_id"])  
            return render_template("Police/incident-verify.html", incidents=pending_alerts)
        except Exception as e:
            print(f"Error fetching alerts: {e}")
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    if request.method == "POST":
        try:
            # Process Accept or Reject actions
            data = request.get_json()
            alert_id = data.get("alert_id")
            action = data.get("action")

            # Ensure the alert exists
            alert = alerts_collection.find_one({"alert_id": alert_id})
            if not alert:
                return jsonify({"error": "Alert not found"}), 404

            if action == "accept":
                incidents_collection.insert_one(alert)
                alerts_collection.delete_one({"alert_id": alert_id})
                message = "Incident accepted and moved to Incidents collection."
            elif action == "reject":
                alerts_collection.update_one(
                    {"alert_id": alert_id},
                    {"$set": {"report_status": "rejected", "updated_at": datetime.datetime.utcnow()}}
                )
                message = "Incident rejected."
            else:
                return jsonify({"error": "Invalid action"}), 400

            return jsonify({"message": message}), 200
        except Exception as e:
            print(f"Error processing incident: {e}")
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route("/police/incident-alerts", methods=["GET"])
def police_incident_alerts():
    incidents = list(incidents_collection.find().sort("created_at", -1))
    for incident in incidents:
        incident["_id"] = str(incident["_id"])
    return render_template("Police/incident-alerts.html", incidents=incidents)

@app.route("/police/update-incident-status/<incident_id>", methods=["POST"])
def update_incident_status(incident_id):
    try:
        new_status = request.json.get("status")
        result = incidents_collection.update_one(
            {"_id": ObjectId(incident_id)}, {"$set": {"status_type": new_status}}
        )
        if result.modified_count > 0:
            return jsonify({"message": "Status updated successfully!"}), 200
        else:
            return jsonify({"error": "Incident not found or no changes made"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/police/incident-report", methods=["GET", "POST"])
def police_incident_report():
    if request.method == "POST":
        try:
            # Log form and file data
            print("Form data received:", request.form)
            print("Files received:", request.files)

            # Extract data
            incident_type = request.form.get("incidentType")
            date_time = request.form.get("dateTime")
            location = request.form.get("location")
            reporting_officer = request.form.get("reportingOfficer")
            status_type = request.form.get("statusType")
            priority_type = request.form.get("priorityType")
            notice = request.form.get("notice")
            description = request.form.get("description")

            # Handle file uploads
            evidence_files = request.files.getlist("evidence")
            evidence_file_paths = []
            evidence_dir = "static/uploads/evidence"  # Save in static directory
            os.makedirs(evidence_dir, exist_ok=True)

            for evidence in evidence_files:
                if evidence.filename != "":
                    file_path = os.path.join(evidence_dir, evidence.filename)
                    evidence.save(file_path)
                    # Save public URL for the file
                    evidence_file_paths.append(f"/static/uploads/evidence/{evidence.filename}")
                    print(f"Saved file: {file_path}")

            # Create the document to insert into MongoDB
            incident_data = {
                "incident_type": incident_type,
                "date_time": date_time,
                "location": location,
                "reporting_officer": reporting_officer,
                "status_type": status_type,
                "priority_type": priority_type,
                "notice": notice,
                "description": description,
                "evidence_files": evidence_file_paths,
                "created_at": datetime.datetime.utcnow(),
                "updated_at": datetime.datetime.utcnow(),
            }

            # Insert into MongoDB
            result = incidents_collection.insert_one(incident_data)
         
            print(f"Document inserted with ID: {result.inserted_id}")

            return jsonify({
                "message": "Incident report submitted successfully!",
                "incident_id": str(result.inserted_id),
            }), 201
        except Exception as e:
            print(f"Error during submission: {e}")
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    # Render the form for GET requests
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
    try:
        # Get form data
        alert_data = {
            'alertType': request.form.get('alertType'),
            'alertTitle': request.form.get('alertTitle'),
            'alertMessage': request.form.get('alertMessage'),
            'location': request.form.get('location'),
            'alertDuration': int(request.form.get('alertDuration') or 0),
            'targetAudience': request.form.getlist('targetAudience'),
            'status_type' : "pending" ,
            'priority_type' : "high",
            'date_time' : request.form.get("dateTime"),
            "created_at": datetime.datetime.utcnow(),
            "updated_at": datetime.datetime.utcnow(),
        }

        # Insert into MongoDB
        result = incidents_collection.insert_one(alert_data)
        alert_data['_id'] = str(result.inserted_id)

        # Broadcast the new alert to connected clients (if using Socket.IO)
        # socketio.emit('new_alert', alert_data)

        # Send WhatsApp message
        whatsapp_message = (
            f"🚨 New Alert 🚨\n"
            f"Type: {alert_data['alertType']}\n"
            f"Title: {alert_data['alertTitle']}\n"
            f"Message: {alert_data['alertMessage']}\n"
            f"Location: {alert_data['location']}\n"
            f"Duration: {alert_data['alertDuration']} hours\n"
            f"Target Audience: {', '.join(alert_data['targetAudience'])}"
        )

   
        
        # Schedule the message to be sent in 1 minute
        now =  datetime.datetime.now()
        send_time = now + datetime.timedelta(minutes=2)
        kit.sendwhatmsg(phone_number, whatsapp_message, send_time.hour, send_time.minute)

        return jsonify({
            'status': 'success',
            'message': 'Alert submitted and WhatsApp message scheduled successfully',
            'inserted_id': str(result.inserted_id)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500



@app.route('/api/markers', methods=['POST'])
def save_marker():
    data = request.get_json()
    lat = data.get('lat')
    lng = data.get('lng')
    title = data.get('title')
    priority = data.get('priority')

    if not lat or not lng or not title or not priority:
        return jsonify({'error': 'Latitude, longitude, title, and priority are required'}), 400

    # Insert marker into MongoDB
    marker = {'lat': lat, 'lng': lng, 'title': title, 'priority': priority}
    markers_collection.insert_one(marker)

    return jsonify(marker), 201

# API to fetch all markers
@app.route('/api/markers', methods=['GET'])
def get_markers():
    markers = list(markers_collection.find({}, {'_id': 0}))  # Exclude MongoDB _id field
    return jsonify(markers), 200


if __name__ == "__main__":
    app.run(debug=True)
