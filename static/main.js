let map, userMarker, destinationMarker, routeLine;
let selectedTransport = null;
let isSharing = false;
let timer = null;
let startTime = null;
let guardians = [];

// Initialize map
function initMap() {
    map = L.map('map').setView([0, 0], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Get user's current location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            position => {
                const { latitude, longitude } = position.coords;
                map.setView([latitude, longitude], 13);
                
                // Create user marker with transport icon
                createUserMarker([latitude, longitude]);

                // Allow clicking on map to set destination
                map.on('click', (e) => {
                    setDestination(e.latlng);
                });
            },
            error => {
                showAlert('Error getting location: ' + error.message);
            }
        );
    }
}

function createUserMarker(latlng) {
    if (userMarker) {
        map.removeLayer(userMarker);
    }

    const icon = selectedTransport ? getTransportIcon() : '🚶';
    
    userMarker = L.marker(latlng, {
        draggable: false,
        title: 'Your Location',
        icon: L.divIcon({
            className: 'custom-div-icon',
            html: `<div style="font-size: 24px;">${icon}</div>`,
            iconSize: [30, 30],
            iconAnchor: [15, 15]
        })
    }).addTo(map);
}

function getTransportIcon() {
    const icons = {
        'walking': '🚶',
        'car': '🚗',
        'autorickshaw': '🛺',
        'bus': '🚌'
    };
    return icons[selectedTransport] || '🚶';
}

function setDestination(latlng) {
    if (destinationMarker) {
        map.removeLayer(destinationMarker);
    }
    destinationMarker = L.marker(latlng, {
        draggable: true,
        title: 'Destination',
        icon: L.divIcon({
            className: 'custom-div-icon',
            html: '<div style="font-size: 24px;">📍</div>',
            iconSize: [30, 30],
            iconAnchor: [15, 30]
        })
    }).addTo(map);

    // Update route if sharing is active
    if (isSharing) {
        updateRoute();
    }
}

function updateRoute() {
    if (!userMarker || !destinationMarker) return;

    const userLatLng = userMarker.getLatLng();
    const destLatLng = destinationMarker.getLatLng();

    // Remove existing route line
    if (routeLine) {
        map.removeLayer(routeLine);
    }

    // Draw new route line
    routeLine = L.polyline([
        [userLatLng.lat, userLatLng.lng],
        [destLatLng.lat, destLatLng.lng]
    ], {
        color: 'red',
        weight: 3,
        opacity: 0.7,
        dashArray: '10, 10'
    }).addTo(map);

    // Fit map bounds to show entire route
    map.fitBounds(routeLine.getBounds(), { padding: [50, 50] });
}

function selectTransport(type) {
    selectedTransport = type;

    document.querySelectorAll('.transport-btn').forEach(btn => {
        btn.classList.remove('bg-blue-200', 'border-blue-600');
    });

    const selectedBtn = Array.from(document.querySelectorAll('.transport-btn')).find(btn => {
        return btn.innerText.includes(getTransportIconByType(type));
    });

    if (selectedBtn) {
        selectedBtn.classList.add('bg-blue-200', 'border-blue-600');
    }

    // Update user marker
    if (userMarker) {
        const latlng = userMarker.getLatLng();
        createUserMarker(latlng);
    }
}

function getTransportIconByType(type) {
    const icons = {
        'walking': '🚶',
        'car': '🚗',
        'autorickshaw': '🛺',
        'bus': '🚌'
    };
    return icons[type];
}

function addGuardian() {
    const phoneInput = document.getElementById('guardianPhone');
    const phone = phoneInput.value.trim();
    
    if (!phone) {
        showAlert('Please enter a phone number');
        return;
    }

    if (!guardians.includes(phone)) {
        guardians.push(phone);
        updateGuardiansList();
        phoneInput.value = '';
    }
}

function updateGuardiansList() {
    const list = document.getElementById('guardiansList');
    list.innerHTML = guardians.map(phone => `
        <div class="guardian-item bg-green-100 border border-green-400 text-green-800 p-2 rounded flex justify-between items-center text-sm font-medium">
            <span>${phone}</span>
            <button onclick="removeGuardian('${phone}')" class="text-red-500 hover:text-red-700 font-semibold text-xs">Remove</button>
        </div>
    `).join('');
}

function removeGuardian(phone) {
    guardians = guardians.filter(g => g !== phone);
    updateGuardiansList();
}

function startSharing() {
    if (!destinationMarker) {
        showAlert('Please set a destination first');
        return;
    }

    if (!selectedTransport) {
        showAlert('Please select a transport method');
        return;
    }

    if (guardians.length === 0) {
        showAlert('Please add at least one guardian');
        return;
    }

    const estimatedTime = document.getElementById('estimatedTime').value;
    if (!estimatedTime) {
        showAlert('Please enter estimated time');
        return;
    }

    isSharing = true;
    startTime = new Date();
    document.getElementById('startSharing').disabled = true;
    document.getElementById('stopSharing').disabled = false;
    document.getElementById('sosButton').disabled = false;

    // Start timer
    startTimer(parseInt(estimatedTime));

    // Start location tracking
    startLocationTracking();

    // Draw initial route
    updateRoute();

    // Notify guardians
    notifyGuardians('Location sharing started');
}

function stopSharing() {
    isSharing = false;
    clearInterval(timer);
    document.getElementById('startSharing').disabled = false;
    document.getElementById('stopSharing').disabled = true;
    document.getElementById('sosButton').disabled = true;
    
    // Remove route line
    if (routeLine) {
        map.removeLayer(routeLine);
    }
    
    notifyGuardians('Location sharing stopped');
}

function startTimer(estimatedMinutes) {
    const endTime = new Date(startTime.getTime() + estimatedMinutes * 60000);
    
    timer = setInterval(() => {
        const now = new Date();
        const timeDiff = endTime - now;
        
        if (timeDiff <= 0) {
            clearInterval(timer);
            triggerSOS('Estimated time exceeded');
            return;
        }

        const hours = Math.floor(timeDiff / 3600000);
        const minutes = Math.floor((timeDiff % 3600000) / 60000);
        const seconds = Math.floor((timeDiff % 60000) / 1000);
        
        document.getElementById('timer').textContent = 
            `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }, 1000);
}

function startLocationTracking() {
    if (navigator.geolocation) {
        navigator.geolocation.watchPosition(
            position => {
                const { latitude, longitude } = position.coords;
                createUserMarker([latitude, longitude]);
                updateRoute();
            },
            error => {
                showAlert('Error tracking location: ' + error.message);
            }
        );
    }
}

function triggerSOS(reason = 'Manual SOS triggered') {
    const currentLocation = userMarker.getLatLng();
    const locationLink = `https://www.google.com/maps?q=${currentLocation.lat},${currentLocation.lng}`;
    const message = `
        <div class="font-bold text-red-700">🚨 SOS ALERT!</div>
        <div class="text-xs">Reason: ${reason}</div>
        <div class="text-xs mt-1"><a href="${locationLink}" target="_blank" class="text-blue-600 underline font-semibold">📍 View on Google Maps</a></div>
        <div class="text-[11px] text-gray-500 mt-1">Time: ${new Date().toLocaleTimeString()}</div>
    `;

    notifyGuardians(message);
    showAlert('SOS alert sent to guardians');
    stopSharing();
}

function notifyGuardians(message) {
    const alertsDiv = document.getElementById('alerts');
    const alertElement = document.createElement('div');
    alertElement.className = 'alert bg-orange-100 border border-orange-300 text-orange-800 px-3 py-2 rounded text-xs shadow-sm mb-2';
    alertElement.innerHTML = message;
    alertsDiv.insertBefore(alertElement, alertsDiv.firstChild);
}

function showAlert(message) {
    const alertsDiv = document.getElementById('alerts');
    const alertElement = document.createElement('div');
    alertElement.className = 'alert bg-orange-100 border border-orange-300 text-orange-800 px-3 py-2 rounded text-xs shadow-sm mb-2';
    alertElement.innerHTML = message;
    alertsDiv.insertBefore(alertElement, alertsDiv.firstChild);
}

// Initialize the map when the page loads
window.onload = initMap;
