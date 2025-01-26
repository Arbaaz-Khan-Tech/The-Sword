from flask import Blueprint, render_template

# Create the Blueprint object
police_bp = Blueprint('police', __name__)

# Define routes for the police blueprint
@police_bp.route("/cctv-feeds")
def police_cctv_feeds():
    return render_template("Police/cctv-feeds.html")

@police_bp.route("/crime-heatmap")
def police_crime_heatmap():
    return render_template("Police/crime-heatmap.html")

@police_bp.route("/police-analytics")
def police_analytics():
    return render_template("Police/police-analytics.html")

@police_bp.route("/incident-report")
def police_incident_report():
    return render_template("Police/incident-report.html")

@police_bp.route("/offender-database")
def police_offender_database():
    return render_template("Police/offender-database.html")

@police_bp.route("/sos-notifications")
def police_sos_notifications():
    return render_template("Police/sos-notifications.html")
