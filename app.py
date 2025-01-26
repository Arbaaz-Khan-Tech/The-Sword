from flask import Flask, Response, render_template, redirect, request, url_for, session
from flask_socketio import SocketIO, emit
import cv2
from ultralytics import YOLO
from routes.citizen import citizen_bp
from routes.police import police_bp

import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

 # Register blueprints
app.register_blueprint(citizen_bp, url_prefix="/citizen")
app.register_blueprint(police_bp, url_prefix="/police")


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

@app.route("/")
def login_page():
    """Render the login page."""
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    """Handle login logic."""
    role = request.form.get("role")  # Get role (police or citizen) from the form
    username = request.form.get("username")  # Retrieve the username
    password = request.form.get("password")  # Retrieve the password

    # Replace the following with actual authentication logic
    if role == "police" and username == "police123" and password == "securepassword":
        session["role"] = "police"
        session["username"] = username
        return redirect(url_for("police_index"))  # Redirect to police dashboard
    else:
        # Invalid credentials, redirect back to login page
        flash("Invalid Police ID or Password. Please try again.", "error")
        return redirect(url_for("login_page"))

    
@app.route("/base")
def home():
    return render_template("base.html")

@app.route('/open-base')
def open_pbase():
    return render_template('Pbase.html')  # Rendering Pbase.html directly




# Citizen Side Routes



@app.route("/citizen")
def citizen_index():
    """Render Citizen index page."""
    return render_template("Citizen/index.html")

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
    """Render Police index page."""
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
