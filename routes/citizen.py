from flask import Blueprint, render_template

citizen_bp = Blueprint("citizen", __name__)

@citizen_bp.route("/")
def index():
    return render_template("Citizen/index.html")

@citizen_bp.route("/geofencing")
def geofencing():
    return render_template("Citizen/geofencing.html")

@citizen_bp.route("/incident-alerts")
def incident_alerts():
    return render_template("Citizen/incident-alerts.html")

@citizen_bp.route("/real-time-map")
def real_time_map():
    return render_template("Citizen/real-time-map.html")

@citizen_bp.route("/sos")
def sos():
    return render_template("Citizen/sos.html")
