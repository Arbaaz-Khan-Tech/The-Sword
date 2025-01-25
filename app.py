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

app = Flask(__name__)
socketio = SocketIO(app)


 


# Load both YOLO models
violence_model = YOLO("viodec_mk1.pt")  # Replace with your violence detection model path
arms_model = YOLO("arms_detect.pt")  # Replace with your arms detection model path

# Define violence-related and arms-related classes
violence_classes = ["Violence "]  # Adjust based on your model's labels
arms_classes = ["Gun", "knife", "Pistol","handgun","rifle"]  # Adjust based on your model's labels

# Initialize video capture
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Error: Unable to access the webcam.")


def detection_loop():
    """Perform object detection using both models and stream video frames."""
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Unable to read frame from webcam.")
                break

            # Run YOLOv8 inference for both models
            violence_results = violence_model(frame)
            arms_results = arms_model(frame)

            # Process violence detection results
            for result in violence_results[0].boxes:
                cls_id = int(result.cls[0])
                label = violence_model.names[cls_id]
                if label in violence_classes:
                    # Emit violence alert
                    socketio.emit('alert', {'message': f"Violence detected: {label}"}, broadcast=True)

            # Process arms detection results
            for result in arms_results[0].boxes:
                cls_id = int(result.cls[0])
                label = arms_model.names[cls_id]
                if label in arms_classes:
                    # Emit arms alert
                    socketio.emit('alert', {'message': f"Weapon detected: {label}"}, broadcast=True)

            # Encode the frame as a JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            frame_data = buffer.tobytes()

            # Yield the frame to the video stream
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cap.release()


@app.route('/video_feed')
def video_feed():
    """Stream the video feed to the front end."""
    return Response(
        detection_loop(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )



#created a connection to MongoDB
mongo_con="mongodb://localhost:27017"
client=MongoClient(mongo_con)
db=client["SurakshaSetu"]
collection=db["Incidents"]


# Citizen Side Routes
@app.route("/")
def citizen_index():
    return render_template("Citizen/index.html")

@app.route("/citizen/geofencing")
def citizen_geofencing():
    return render_template("Citizen/geofencing.html")

@app.route("/citizen/incident-alerts", methods=["GET"])
def citizen_incident_alerts():
    incidents = list(collection.find())
    print("Retrieved incidents:", incidents)
    for incident in incidents:
        incident["_id"] = str(incident["_id"])
    return render_template("Citizen/incident-alerts.html", incidents=incidents)

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
    

@app.route("/police/incident-alerts", methods=["GET"])
def police_incident_alerts():
    # Fetch all incidents from the database
    incidents = list(collection.find())
    # Convert MongoDB ObjectId to string for JSON serialization
    for incident in incidents:
        incident["_id"] = str(incident["_id"])
    return render_template("Police/incident-alerts.html", incidents=incidents)

# Route to update incident status
@app.route("/police/update-incident-status/<incident_id>", methods=["POST"])
def update_incident_status(incident_id):
    try:
        new_status = request.json.get("status")
        # Update the status_type in the database
        result = collection.update_one(
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
            }

            # Insert into MongoDB
            result = collection.insert_one(incident_data)
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


if __name__ == "__main__":
    app.run(debug=True)
