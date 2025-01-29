const map = L.map('map');
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18 }).addTo(map);

let policeMarker, selectedCoords = null;

// **Fetch & Show Police Location**
navigator.geolocation.getCurrentPosition(position => {
    const lat = position.coords.latitude, lng = position.coords.longitude;

    // **Set map to police location with zoom**
    map.setView([lat, lng], 15);

    policeMarker = L.marker([lat, lng], { icon: blueIcon }).addTo(map)
        .bindPopup("🚔 You are here").openPopup();
}, err => console.error("Location Error:", err));

map.on('click', (e) => {
    selectedCoords = e.latlng;
    L.marker([e.latlng.lat, e.latlng.lng], { icon: redIcon }).addTo(map)
        .bindPopup("📍 Selected Crime Location").openPopup();
});

document.getElementById('crimeForm').addEventListener('submit', (e) => {
    e.preventDefault();
    if (!selectedCoords) {
        alert("Please select a location on the map.");
        return;
    }

    const crimeData = {
        lat: selectedCoords.lat,
        lng: selectedCoords.lng,
        type: document.getElementById('crimeType').value,
        severity: document.getElementById('severity').value,
        description: document.getElementById('crimeDesc').value
    };

    fetch('/api/report-crime', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(crimeData)
    }).then(res => res.json())
      .then(data => alert(data.message))
      .catch(err => console.error("Error:", err));
});

const redIcon = L.icon({
    iconUrl: 'https://cdn-icons-png.flaticon.com/512/484/484611.png',
    iconSize: [30, 30]
});

const blueIcon = L.icon({
    iconUrl: 'https://cdn-icons-png.flaticon.com/512/2991/2991102.png',
    iconSize: [30, 30]
});
