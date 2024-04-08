var map = L.map('map').setView([51.77, 19.46], 14);
var marker = null;
var circle = null;
var poiMarkers = [];
var selectedAmenities = [];
var radius = 500;
var openGroup = null;
var routeLayer = null;
var selectedAmenitiesList = null;
var startData = null;
var endData = null;
var selectedStartData = null;
var selectedEndData = null;
var currentRouteData = null;
var selectedChoice = null;
var decisionResult = null;
var lastMarkerPosition = null;

var timestamp = new Date().getTime();

var publicTransportCheckBox = document.querySelector("input[name=public_transport]");

$('.group-heading').click(function () {
    if (openGroup !== this) {
        if (openGroup) {
            $(openGroup).toggleClass('open');
            $(openGroup).next('.amenity-list').slideToggle();
        }
        $(this).toggleClass('open');
        $(this).next('.amenity-list').slideToggle();
        openGroup = this;
    } else {
        $(this).toggleClass('open');
        $(this).next('.amenity-list').slideToggle();
        openGroup = null;
    }
});

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap'
}).addTo(map);

$('input[name=public_transport]').on('change', function () {
    updateMap();
});

// TODO: do poprawy - jeżeli jest wyżej w order, to nadpisuje to
$('#amenities-form input[name="selected_amenities"]').on('change', function () {
    selectedAmenitiesRaw = $('#amenities-form input[name="selected_amenities"]:checked');

    selectedAmenities = selectedAmenitiesRaw.map(function() {
        return $(this).val().split(',')[0];
    }).get();

    selectedAmenitiesList = selectedAmenitiesRaw.map(function() {
        return {"text": $(this).val().split(',')[1]};
    }).get();

    updateSelectedAmenitiesList(selectedAmenitiesList)

    updateMap();
});

function showPopup(message) {
    var popup = document.getElementById("popup");
    popup.textContent = message;
    popup.style.display = "block";

    setTimeout(function () {
        popup.style.display = "none";
    }, 5000);
}

function createCircle(lat, lng, radius) {
    if (circle) {
        map.removeLayer(circle);
    }

    startData = null;
    endData = null;

    if (routeLayer) {
        map.removeLayer(routeLayer);
    }

    circle = L.circle([lat, lng], {
        radius: radius,
        fillColor: 'blue',
        fillOpacity: 0.2,
        stroke: false
    }).addTo(map);
}

function updateMap() {
    if (selectedAmenities.length > 3) {

        showPopup("Możesz wybrać maksymalnie 3 rodzaje punktów.");

        $('#amenities-form input[name="selected_amenities"]:checked').slice(3).prop('checked', false);

        selectedAmenities = $('#amenities-form input[name="selected_amenities"]:checked').map(function () {
            return $(this).val().split(',')[0];
        }).get();
    }

    console.log(selectedAmenities)
    if (marker) {
        var lat = marker.getLatLng().lat;
        var lng = marker.getLatLng().lng;
        var newLat = lat + (radius / 111000);
        var newLng = lng + (radius / (111000 * Math.cos(lat * Math.PI / 180)));
        var queryParams = 'lat=' + lat + '&lng=' + lng + '&newLat=' + newLat + '&newLng=' + newLng + '&amenitie=' + selectedAmenities.join(',');

        if (publicTransportCheckBox.checked) {
            queryParams += '&public_transport=True'
        } else {
            queryParams += '&public_transport=False'
        }

        fetchData(queryParams);
    }
}

function fetchData(queryParams) {
    fetch('/calculate-area/?' + queryParams)
        .then(response => response.json())
        .then(result => {
            console.log(result)
            if (result.selected_amenity) {
                updateSelectedAmenitiesList(result.selected_amenity);
            }
            handleResult(result);
        })
        .catch(error => {
            console.error('Error:', error);
            showPopup("Wystąpił błąd podczas przetwarzania.");
            removePOIMarkers();
        });
}

function handleResult(result) {
    if (result.error) {
        showPopup(result.error);
        removePOIMarkers();
    } else if (result.message_info) {
        console.log(result);
        removePOIMarkers();
        addAmenityPoints(result.amenity_points);
        addPublicTransportPoints(result.public_transport_points);
        showPopup(result.message_info);
    } else {
        console.log(result);
        removePOIMarkers();
        addAmenityPoints(result.amenity_points);
        addPublicTransportPoints(result.public_transport_points);
    }
}

map.on('click', (event) => {
    var lat = event.latlng.lat;
    var lng = event.latlng.lng;

    if (marker) {
        lastMarkerPosition = marker.getLatLng();
        map.removeLayer(marker);
    }

    startData = null;
    endData = null;

    var newLat = lat + (radius / 111000);
    var newLng = lng + (radius / (111000 * Math.cos(lat * Math.PI / 180)));

    var queryParams = 'lat=' + lat + '&lng=' + lng + '&newLat=' + newLat + '&newLng=' + newLng + '&amenitie=' + selectedAmenities.join(',');

    var iconUrl = `static/js/markers/main.svg`;
    var customIcon = L.icon({
        iconUrl: iconUrl,
        iconSize: [25, 35]
    });

    marker = L.marker([lat, lng])
        .setIcon(customIcon)
        .addTo(map);

    if (publicTransportCheckBox.checked) {
        queryParams += '&public_transport=True'
    } else {
        queryParams += '&public_transport=False'
    }

    if (routeLayer) {
        map.removeLayer(routeLayer);
        clearRouteMessage();
        clearStartEndMessage();
    }

    if (selectedStartData || selectedEndData) {
        showModalResponse(function(response) {
            if (response) {
                clearStartEndMessage();
                createCircle(lat, lng, radius);
                fetchData(queryParams);
            } else {
                if (marker) {
                    map.removeLayer(marker);
                    clearSelectedRoutePoints()
                }
                if (lastMarkerPosition) {
                    marker = L.marker([lastMarkerPosition.lat, lastMarkerPosition.lng]).addTo(map);
                }
            }
        });
    } else {
        clearStartEndMessage();
        createCircle(lat, lng, radius);
        fetchData(queryParams);
    }
});

document.getElementById('yesButton').addEventListener('click', function() {
    handleModalResponse(true);
});

document.getElementById('noButton').addEventListener('click', function() {
    handleModalResponse(false);
});

// TODO: lood at method callback in JS
function showModalResponse(callback) {
    var myModal = new bootstrap.Modal(document.getElementById('dataModal'), {
        keyboard: false
    });

    document.getElementById('yesButton').onclick = function() {
        myModal.hide();
        callback(true);
    };

    document.getElementById('noButton').onclick = function() {
        myModal.hide();
        callback(false);
    };

    myModal.show();
}

function mouseOverPublicTransportHandler(poi) {
    return function () {
        var tooltipContent = `Nazwa przystanku: ${poi.name_stop_position}<br>Rodzaj transportu: ${poi.type_of_stop}`;
        this.bindTooltip(tooltipContent).openTooltip();
    };
}

function mouseOverAmenityHandler(poi) {
    return function () {
        var tooltipContent = `Nazwa: ${poi.name}`;
        this.bindTooltip(tooltipContent).openTooltip();
    };
}

var currentPopupMessage = null;
var generatingRouteMessage = "Generowanie trasy";

function showPopupRouteMessage(message) {
    var popup = document.getElementById("popup-distance");

    if (currentPopupMessage !== message) {
        currentPopupMessage = message;
        popup.textContent = message;
        popup.style.display = "block";
    }

    if (message === generatingRouteMessage) {
        changeInformationRouteMessage("#f5f569")
    } else {
        popup.style.backgroundColor = "";
    }
}

function clearRouteMessage() {
    changeInformationRouteMessage()
}

function clearSelectedRoutePoints() {
    selectedStartData = null;
    selectedEndData = null;
}

function clearStartEndMessage() {
    var startAddress = document.getElementById("start-address");
    startAddress.textContent = "Wybierz punkt startowy";

    var endAddress = document.getElementById("end-address");
    endAddress.textContent = "Wybierz punkt docelowy";
}

function sendNavigationRequest(startData, endData) {
    $.ajax({
        type: 'GET',
        url: '/generate-route/',
        data: { startData, endData },
        success: function (response) {
            if (currentRouteData !== response.route_data) {
                currentRouteData = response.route_data;
                displayRouteOnMap(currentRouteData);
                if (response.distance) {
                    showPopupRouteMessage(`Dystans pieszo: ${response.distance} m`);
                    changeInformationRouteMessage("#d4f0cc")
                }
            }
        },
        error: function (error) {
            console.error('Błąd:', error);
        }
    });
}

function displayRouteOnMap(routeData) {
    if (routeLayer) {
        map.removeLayer(routeLayer);
    }
    var routePoints = routeData.map(coord => L.latLng(coord[0], coord[1]));
    var routeLine = L.polyline(routePoints, {color: 'red'});
    routeLayer = routeLine.addTo(map);
    map.fitBounds(routeLayer.getBounds());
}

function checkAndSendNavigationRequest() {
    if (startData && endData) {
        sendNavigationRequest(startData, endData);
        showPopupRouteMessage(generatingRouteMessage)
    }
}

// TODO: make it less repetitive
function mouseClickAmenityHandler(poi) {
    return function (event) {
        var websiteLink = poi.website;

        if (typeof websiteLink !== 'undefined') {
            websiteLink = `<a href="${websiteLink}" target="_blank">${websiteLink}</a>`;
        } else {
            websiteLink = 'Brak strony';
        }

        var tooltipContent = `
            Nazwa: ${poi.name}
            <br>
            Strona internetowa: ${websiteLink}
            <br>
            Adres: ${poi.address}
            <br>
            <br>
            <div class="gap-2 d-flex justify-content-center" role="group">
                <button onclick="startNavigation() type="button" class="btn btn-primary btn-sm"">
                    Start trasy
                </button>
                <button onclick="endNavigation() type="button" class="btn btn-primary btn-sm"">
                    Cel trasy
                </button>
            </div>
            `;

        var popupContent = document.createElement('div');
        popupContent.innerHTML = tooltipContent;

        var popup = L.popup()
            .setLatLng(event.latlng)
            .setContent(popupContent)
            .openOn(map);

        var startButton = $(popupContent).find('button')[0];
        if (startButton) {
            startButton.addEventListener('click', function () {
                startData = {
                    poi_lat_start: poi.lat,
                    poi_lng_start: poi.lng
                };

                var startAddress = document.getElementById("start-address");
                var messageRoute = "";
                if (poi.address != "Brak danych") {
                    messageRoute = `Start: ${poi.name}, ${poi.address}`;
                } else {
                    messageRoute = `Start: ${poi.name}`
                }
                if (!!startData) {
                    selectedStartData = true;
                }
                startAddress.textContent = messageRoute;

                checkAndSendNavigationRequest();
            });
        }

        var endButton = $(popupContent).find('button')[1];
        if (endButton) {
            endButton.addEventListener('click', function () {
                endData = {
                    poi_lat_end: poi.lat,
                    poi_lng_end: poi.lng,
                    lat : marker.getLatLng().lat,
                    lng : marker.getLatLng().lng
                };

                var endAddress = document.getElementById("end-address");
                var messageRoute = "";
                if (poi.address != "Brak danych") {
                    messageRoute = `Cel: ${poi.name}, ${poi.address}`;
                } else {
                    messageRoute = `Cel: ${poi.name}`
                }
                if (!!endData) {
                    selectedEndData = true;
                }
                endAddress.textContent = messageRoute;

                checkAndSendNavigationRequest();
            });
        }
    };
}

function mouseClickTransportHandler(poi) {
    return function (event) {
        var tooltipContent = `
            Nazwa przystanku: ${poi.name_stop_position}
            <br>
                Rodzaj transportu: ${poi.type_of_stop}
            <br>
            <br>
            <div class="gap-2 d-flex justify-content-center" role="group">
                <button onclick="startNavigation() type="button" class="btn btn-primary btn-sm"">
                    Start trasy
                </button>
                <button onclick="endNavigation() type="button" class="btn btn-primary btn-sm"">
                    Cel trasy
                </button>
            </div>
            `;

        var popupContent = document.createElement('div');
        popupContent.innerHTML = tooltipContent;

        var popup = L.popup()
            .setLatLng(event.latlng)
            .setContent(popupContent)
            .openOn(map);

        var startButton = $(popupContent).find('button')[0];
        if (startButton) {
            startButton.addEventListener('click', function () {
                startData = {
                    poi_lat_start: poi.lat,
                    poi_lng_start: poi.lng
                };

                var startAddress = document.getElementById("start-address");
                var messageRoute = `Start: ${poi.name_stop_position}`;
                startAddress.textContent = messageRoute;
                if (!!startData) {
                    selectedStartData = true;
                }

                checkAndSendNavigationRequest();
            });
        }

        var endButton = $(popupContent).find('button')[1];
        if (endButton) {
            endButton.addEventListener('click', function () {
                endData = {
                    poi_lat_end: poi.lat,
                    poi_lng_end: poi.lng,
                    lat : marker.getLatLng().lat,
                    lng : marker.getLatLng().lng
                };

                var endAddress = document.getElementById("end-address");
                var messageRoute = `Cel: ${poi.name_stop_position}`;
                endAddress.textContent = messageRoute;
                if (!!endData) {
                    selectedEndData = true;
                }

                checkAndSendNavigationRequest();
            });
        }
    };
}

function addAmenityPoints(amenityPoints) {
    for (var i = 0; i < amenityPoints.length; i++) {
        var poi = amenityPoints[i];
        var iconUrl = `static/js/amenity/${poi.amenity}.svg`;
        var customIcon = L.icon({
            iconUrl: iconUrl,
            iconSize: [18, 18]
        });

        if (poi.status !== "missing") {
            var poiMarker = L.marker()
            poiMarker
                .setLatLng([poi.lat, poi.lng])
                .setIcon(customIcon)
                .addTo(map);

            poiMarkers.push(poiMarker);

            poiMarker.on('mouseover', mouseOverAmenityHandler(poi));

            poiMarker.on('click', mouseClickAmenityHandler(poi));

            poiMarker.on('mouseout', function () {
                this.closeTooltip();
            });
        }
    }
}

function addPublicTransportPoints(publicTransportPoints) {
    for (var i = 0; i < publicTransportPoints.length; i++) {
        var poi = publicTransportPoints[i];

        var iconUrl = `static/js/markers/${poi.type_of_stop}.svg`;
        var customIcon = L.icon({
            iconUrl: iconUrl,
            iconSize: [22, 22]
        });

        var poiMarker = L.marker()
        poiMarker
            .setLatLng([poi.lat, poi.lng])
            .setIcon(customIcon)
            .addTo(map);

        poiMarkers.push(poiMarker);

        poiMarker.on('mouseover', mouseOverPublicTransportHandler(poi));

        poiMarker.on('click', mouseClickTransportHandler(poi));

        poiMarker.on('mouseout', function () {
            this.closeTooltip();
        });
    }
}

function removePOIMarkers() {
    for (var i = 0; i < poiMarkers.length; i++) {
        map.removeLayer(poiMarkers[i]);
    }
    poiMarkers = [];
}

$('#clear-button-all').click(function () {
    if (marker) {
        map.removeLayer(marker);
        marker = null;
    }
    if (circle) {
        map.removeLayer(circle);
        circle = null;
    }
    if (routeLayer) {
        map.removeLayer(routeLayer);
    }
    removePOIMarkers();
    selectedAmenities = [];
    $('#selected-points-list').empty();
    $('#amenities-form input[name="selected_amenities"]').prop('checked', false);
    clearSelectedAmenitiesList();
    clearRouteMessage();
    clearStartEndMessage();
    clearSelectedRoutePoints();
});

$('#clear-button-points').click(function () {
    removePOIMarkers();
    selectedAmenities = [];
    $('#selected-points-list').empty();
    $('#amenities-form input[name="selected_amenities"]').prop('checked', false);
    clearSelectedAmenitiesList();
    clearSelectedRoutePoints();
});

$('#clear-button-route').click(function () {
    if (routeLayer) {
        map.removeLayer(routeLayer);
    }
    clearRouteMessage();
    clearStartEndMessage();
    clearSelectedRoutePoints();
});

var radiusSlider = $('#radius-slider');
var radiusValue = $('#radius-value');

radiusSlider.val(radius);
radiusValue.text(radius + " m");

radiusSlider.on('input', function () {
    var newRadius = $(this).val();
    radiusValue.text(newRadius + " m");

    radius = parseInt(newRadius);
    if (marker) {
        createCircle(marker.getLatLng().lat, marker.getLatLng().lng, radius);
    }

    updateMap();
});

function updateSelectedAmenitiesList(amenities) {
    var selectedAmenitiesList = document.getElementById('selected-amenities-list');
    var listItems = selectedAmenitiesList.getElementsByTagName('li');

// TODO: kiedy zaznaczam jakieś amenity i go nie ma to wtedy nie pojaiwa się w aktualne wybrane punkty (musi się pojawiać)

    for (var i = 0; i < listItems.length; i++) {
        var amenityText = amenities[i] ? amenities[i].text || 'Brak wybranego punktu' : 'Brak wybranego punktu';
        var badgeValue = amenities[i] ? amenities[i].badge || '0' : '0';
        listItems[i].querySelector('.ms-2').textContent = amenityText;

        var badge = listItems[i].querySelector('.badge');
        badge.textContent = badgeValue;

        if (amenities[i]) {
            badge.style.display = 'inline-block';
        } else {
            badge.style.display = 'none';
        }
    }
}

function clearSelectedAmenitiesList() {
    var selectedAmenitiesList = document.getElementById('selected-amenities-list');
    var listItems = selectedAmenitiesList.getElementsByTagName('li');

    for (var i = 0; i < listItems.length; i++) {
        listItems[i].querySelector('.ms-2').textContent = "Brak wybranego punktu";
        var badge = listItems[i].querySelector('.badge');
        badge.textContent = "";
        badge.style.display = 'none';
    }
}

function changeInformationRouteMessage(color) {
    var popup = document.getElementById("popup-distance");

    if (typeof color === 'string' || color instanceof String) {
        popup.style.backgroundColor = color;
        popup.style.border = "1px solid #222121";
        popup.style.color = "#000000"
    } else {
        popup.style.backgroundColor = "rgba(0, 0, 0, 0)";
        popup.style.border = "0px rgba(0, 0, 0, 0)";
        popup.style.opacity = 0;
    }
}