# The-Sword 

#  **Problem Statement:**  
Citizens in India face safety concerns due to delayed police responses, while police struggle with inefficiency and manual processes. Our project bridges this gap using AI and real-time communication to enhance safety and productivity.
#  Demo Video

https://drive.google.com/file/d/1T77e_ZAXrupJhO2dTGwlxG-A8mNdjK5B/view?usp=sharing

## Without Captions Full Frame
[https://drive.google.com/file/d/1T77e_ZAXrupJhO2dTGwlxG-A8mNdjK5B/view](https://drive.google.com/file/d/11BdcLobnTh6Lf5OHmNuTjxMHEUcJLEc8/view?usp=drive_link)

## With Captions 
# SurakshaSetu

A comprehensive public safety solution leveraging AI-powered threat detection, real-time alerts, and community-police collaboration to enhance urban security.

## Document And Ppt
https://drive.google.com/drive/folders/1LgmweoFFryIkJN1Nf_TAnd1yYLOr2lw3?usp=sharing

## System Architecure :-

![Image](https://github.com/user-attachments/assets/c890696c-c2ad-4c5c-bf45-42a0b8bffe2a)


## 🚀 Unique Selling Proposition (USP)
1. **AI-Powered Threat Detection** - Real-time violence/weapon identification using YOLO models
2. **Geofencing Security Zones** - Customizable safety perimeters with automatic alerts
3. **Two-Way Alert System** - Instant police-to-citizen notifications and crowd-sourced incident reporting
4. **Transparency Dashboard** - Public incident tracking to ensure police accountability
5. **Integrated Offender Database** - Centralized criminal records with spatial mapping

## ⚙️ Key Features

### 👮 **Police Portal**
- **Live CCTV Analysis**  
  AI models (`viodec_mk1.pt` for violence, `arms_detect.pt` for weapons) process 24/7 feeds
- **Incident Broadcasting**  
  Send verified alerts to citizens via SMS/WhatsApp
- **Incident Reporting**
   Structured incident reporting with evidence attachment
  - **Verify Citizen Reporting**
   Verifying citizen incident reporting with evidence attachment provided
- **Crime Heatmap**
   It show crime zones in map from previous historical dataset
- **SOS Triangulation**  
  Visualize emergency locations on interactive map
- ** Criminal Detection / Missing Person Detection **  
  Facial recognition-compatible criminal database / missing person database


### 👥 **Citizen Interface**
- **Emergency SOS**  
  One-touch alert with live location sharing
- **Incident Reporting**  
  Citizen can report the incident with evidence
- **Incident Alert**  
  Citizen will receive the all the nearby alert from police/citizen from verified police sources
- **Safety Heatmaps**  
  Real-time danger zone visualization
- **Custom Geofencing**  
  Create personal safety radius (500m-2km) with automatic notifications
- **Safe Walk **  
  Shares the live location to guardians with SOS enabled (Especially for Womens)
- **Community Engagement**  
  Gamified way for citizen volunteering  with badges, rewards & leaderboard

## 🛠️ Technical Stack
- **AI Engine**: YOLOv8 (Ultralytics)
- **Backend**: Flask + SocketIO (Real-time comms)
- **Database**: MongoDB (NoSQL)
- **Frontend**: HTML5 + Tailwind CSS + JavaScript
- **APIs**: Twilio (SMS), WhatsApp Business API
- **Computer Vision**: OpenCV + PyMongo

## 📦 Installation

### Prerequisites
- Python 3.8+
- MongoDB Atlas/Compass
- Twilio Account (for SMS)
- Nvidia GPU recommended

```bash
# Clone repository
git clone https://github.com/Arbaaz-Khan-Tech/Suraksha_Setu.git

cd Surkasha-setu

# Install dependencies
pip install -r requirements.txt

# Configure environment
create config.json file
# Edit config.json with your Twilio credentials and phone number

example:- Enter your phone number instead of x
{
    "phone_number": "+91xxxxxxxxxx" /
}
```

## 🖥️ Usage

```bash
# Start Flask server
python app.py

# Access interfaces:
# Police Portal: http://localhost:5000/police
# Citizen App: http://localhost:5000/citizen
```




## 📈 Future Roadmap
1. Twilio SMS/WhatsApp integration for alert escalation
2. Mobile apps (React Native) for field reporting
3. Facial recognition for offender identification
4. Predictive crime mapping using historical data
5. Cross-city police collaboration portal


