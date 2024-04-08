import time

from backend.features.base_utils import (NotFoundDataError,
                                         generate_amenity_points,
                                         generate_public_transport_points,
                                         generate_route_from_bbox)
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from geopy.distance import geodesic

from .models import Amenity, AmenityGroup
from collections import Counter

def map_view(request):
    timestamp = int(time.time())
    amenity_groups = AmenityGroup.objects.all()

    amenities_by_group = {}
    for group in amenity_groups:
        amenities_by_group[group] = Amenity.objects.filter(group_amenity=group)

    context = {
        'amenities_by_group': amenities_by_group,
        'timestamp': timestamp
    }

    return render(request, 'map_view.html', context)


#TODO: do poprawy
def count_numbers_of_unique_amenity(amenity_points, languagle="name_pl"):
    amenity_counted_names = []
    missing_status_dicts = []
    updated_places = []
    for place in amenity_points:
        if place.get('status') == 'missing':
            missing_status_dicts.append(place)
        else:
            updated_places.append({k: v for k, v in place.items() if k != 'status' or v != 'missing'})

    print(f"{missing_status_dicts=}")
    missing_counted_amenity = dict(Counter([value["amenity"] for value in missing_status_dicts]))
    for name, value in missing_counted_amenity.items():
        missing_amenity_information = {}
        missing_amenity_name = Amenity.objects.filter(Q(amenity_key=name)).values(languagle)[0][languagle]
        missing_amenity_information["text"] = missing_amenity_name.capitalize()
        missing_amenity_information["badge"] = "0"
        amenity_counted_names.append(missing_amenity_information)

    counted_amenity = dict(Counter([value["amenity"] for value in updated_places]))
    for name, value in counted_amenity.items():
        amenity_information = {}
        amenity_name = Amenity.objects.filter(Q(amenity_key=name)).values(languagle)[0][languagle]
        amenity_information["text"] = amenity_name.capitalize()
        amenity_information["badge"] = value
        amenity_counted_names.append(amenity_information)

    return amenity_counted_names


#TODO: do rozbicia
def calculate_area(request):
    if request.method == 'GET':
        lat = float(request.GET.get('lat'))
        lng = float(request.GET.get('lng'))
        new_lat = float(request.GET.get('newLat'))
        new_lng = float(request.GET.get('newLng'))
        amenitie = request.GET.get('amenitie').split(",")
        public_transport_checkbox = request.GET.get('public_transport')

        if len(amenitie) == 1 and amenitie[0] == "":
            return JsonResponse(
                {'error': "Nie wybrano pola"}
            )

        radius = geodesic((lat, lng), (new_lat, new_lng)).kilometers * 700

        rensponse = {}

        try:
            amenity_points, message_info = generate_amenity_points(
                category=amenitie,
                radius=radius,
                lat=lat,
                lng=lng
            )
            print(f"Test 1 {amenity_points=}")

            rensponse["selected_amenity"] = count_numbers_of_unique_amenity(
                amenity_points=amenity_points
            )

            rensponse["amenity_points"] = amenity_points

            if public_transport_checkbox == "True":
                public_transport_points = generate_public_transport_points(
                    radius=radius,
                    lat=lat,
                    lng=lng
                )
                rensponse["public_transport_points"] = public_transport_points
            else:
                rensponse["public_transport_points"] = ""

            if message_info:
                print(f"Test 2 {amenity_points=}")
                missing_amenity = [amenity["text"] for amenity in count_numbers_of_unique_amenity(amenity_points=message_info)]
                print(f"{missing_amenity=}")
                message_missing_amenity = ", ".join(missing_amenity)
                rensponse["message_info"] = f"Brakujące dane dla: {message_missing_amenity}"

                return JsonResponse(rensponse)

        except NotFoundDataError as error:
            return JsonResponse(
                {"error": error.args[0]}
            )
        return JsonResponse(rensponse)

    return JsonResponse({"message": "Invalid request"}, status=400)


def generate_route(request, origin={}, destination={}):
    rensponse = {}

    if request.method == 'GET':
        print(request.GET)
        lat = float(request.GET.get("endData[lat]"))
        lng = float(request.GET.get("endData[lng]"))
        origin = {
            "x": float(request.GET.get("startData[poi_lat_start]")),
            "y": float(request.GET.get("startData[poi_lng_start]"))
        }
        destination = {
            "x": float(request.GET.get("endData[poi_lat_end]")),
            "y": float(request.GET.get("endData[poi_lng_end]"))
        }

        #TODO: dodać opcję żeby nie można było wybrać takiego samego punkty jako stat i jako end
        route_data, distance = generate_route_from_bbox(
            lat=lat,
            lng=lng,
            origin=origin,
            destination=destination
        )

        rensponse['route_data'] = route_data
        rensponse['distance'] = distance

    return JsonResponse(rensponse, safe=False)