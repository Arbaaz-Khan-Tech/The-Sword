const map = L.map('map');
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18 }).addTo(map);

let heatLayer, citizenMarker;
const ALERT_RADIUS = 1000;
const severityColors = { low: "green", medium: "yellow", high: "red" };

// **Fetch & Display Crime Heatmap**
function fetchCrimeData() {
    fetch('/api/crime-data')
        .then(res => res.json())
        .then(data => {
            displayHeatmap(data);
            displayCrimeMarkers(data);
        })
        .catch(err => console.error("Error:", err));
}

// **Render Heatmap**
function displayHeatmap(data) {
    if (heatLayer) map.removeLayer(heatLayer);
    heatLayer = L.heatLayer(data.map(c => [c.lat, c.lng, 0.5]), { radius: 20, blur: 15 }).addTo(map);
}

// **Show Crime Markers with Details**
function displayCrimeMarkers(data) {
    data.forEach(crime => {
        L.circleMarker([crime.lat, crime.lng], {
            radius: 8,
            fillColor: severityColors[crime.severity],
            color: "#fff",
            weight: 1,
            opacity: 1,
            fillOpacity: 0.8
        }).addTo(map).bindPopup(`<strong>${crime.type}</strong><br>${crime.description}`);
    });
}

// **Fetch & Show Citizen Location**
navigator.geolocation.getCurrentPosition(position => {
    const lat = position.coords.latitude, lng = position.coords.longitude;

    // **Set map view to user location with zoom**
    map.setView([lat, lng], 15);

    citizenMarker = L.marker([lat, lng], { icon: blueIcon }).addTo(map)
        .bindPopup("📍 You are here").openPopup();

    fetchCrimeData();
}, err => {
    console.error("Location Error:", err);
    alert("Unable to access location. Please enable GPS.");
});

const blueIcon = L.icon({
    iconUrl: 'https://cdn-icons-png.flaticon.com/512/2991/2991102.png',
    iconSize: [30, 30]
});
