import requests
from typing import List, Tuple, Dict
import osmnx as ox
from geopy.distance import great_circle


OVERPASS_URL = 'http://overpass-api.de/api/interpreter'


class NotFoundDataError(Exception):
    pass

#TODO: union query with: node(around:{radius},{lat},{lng})[""highway"="bus_stop"];
def osm_query_public_transport_data(radius: float, lat: float, lng: float) -> Dict:
    overpass_query = f"""
    [out:json];
    (
        node(around:{radius},{lat},{lng})["public_transport"="stop_position"];
    );
    out body;
    """

    response = requests.get(
        OVERPASS_URL,
        params={'data':overpass_query}
    ).json()

    return response


def osm_query_amenity_data(category: List[str], key: str, radius: float, lat: float, lng: float) -> Dict:
    overpass_query = f"""
    [out:json];
    (
        node(around:{radius},{lat},{lng})["{key}"="{category}"];
        way(around:{radius},{lat},{lng})["{key}"="{category}"];
        relation(around:{radius},{lat},{lng})["{key}"="{category}"];
    );
    out body;
    """

    response = requests.get(
        OVERPASS_URL,
        params={'data':overpass_query}
    ).json()

    return response


def mapping_name_of_stop(name_stop_position: str) -> str:
    if name_stop_position == "tram_stop":
        return "tramwaj"
    elif name_stop_position == "bus_stop":
        return "autobus"
    elif name_stop_position == "stop":
        return "pociąg/metro"
    elif name_stop_position == "stop_position":
        return "autobus"


#TODO: to fix this + add name of route
def get_public_transport_elements(payload: Dict) -> List:
    location_of_public_transport = []
    for element in payload["elements"]:
        if element["type"] == "node":
            lng, lat = element["lon"], element["lat"]
            name_stop_position = element["tags"].get("name", "Brak nazwy dla tego obiektu")
            if "bus" in element["tags"]:
                if "highway" in element["tags"]:
                    type_of_stop = element["tags"]["highway"]
                elif "public_transport" in element["tags"]:
                    type_of_stop = element["tags"]["public_transport"]
            elif "railway" in element["tags"]:
                type_of_stop = element["tags"]["railway"]
            location_of_public_transport.append({
                "lat": lat,
                "lng": lng,
                "name_stop_position": name_stop_position,
                "type_of_stop": mapping_name_of_stop(type_of_stop)
            })

    if not location_of_public_transport:
        raise NotFoundDataError(
            "Brak danych dla przystanków trasnportu zbiorowego"
        )

    return location_of_public_transport


def combine_address_amenity(tag_element: Dict) -> str:
    if "addr:street" in tag_element and "addr:housenumber" in tag_element:
        addess = f"{tag_element['addr:street']}/{tag_element['addr:housenumber']}"
    elif "addr:street" in tag_element:
        addess = tag_element["addr:street"]
    else:
        addess = "Brak danych"

    if "addr:city" in tag_element:
        addess = addess + f", {tag_element['addr:city']}"

    return addess

#TODO: fix this - ugly
def get_tags_information_from_amenity(tag_element: dict) -> Dict[str, str]:
    amenity_tags = {}
    selected_tags = ["amenity", "name", "website"]
    for tag in selected_tags:
        if tag in tag_element:
            amenity_tags[tag] = tag_element[tag]

        amenity_tags["address"] = combine_address_amenity(tag_element)
        # amenity_tags.get("name", "Brak nazwy dla tego obiektu")

        try:
            amenity_tags["name"]
        except KeyError:
            amenity_tags["name"] = "Brak nazwy dla tego obiektu"

    return amenity_tags


def get_amenity_elements(payload: List) -> Tuple[List[Dict[str, str]], List[str]]:
    location_of_amenity = []
    missing_category = []
    for amenity in payload:
        for amenity_key, amenity_data in amenity.items():
            if amenity_data["elements"]:
                for element in amenity_data["elements"]:
                    if element["type"] != "way":
                        if element["type"] == "node":
                            lng, lat = element["lon"], element["lat"]
                        elif "center" in element:
                            lng, lat = element["center"]["lng"], element["center"]["lat"]
                        location = {"lat": lat, "lng": lng}
                        tags_amenity = get_tags_information_from_amenity(tag_element=element["tags"])
                        location.update(tags_amenity)
                        location_of_amenity.append(location)
            else:
                missing_category.append({"amenity": amenity_key, "status": "missing"})
                location_of_amenity.append({"amenity": amenity_key, "status": "missing"})

    if not location_of_amenity:
        raise NotFoundDataError(
            "Brak danych dla wybranych punktów"
        )

    return location_of_amenity, missing_category


def generate_public_transport_points(radius: float, lat: float, lng: float) -> List:
    public_transport_data = osm_query_public_transport_data(
        radius=radius,
        lat=lat,
        lng=lng
    )
    response = get_public_transport_elements(payload=public_transport_data)

    return response


def generate_amenity_points(category: List[str], radius: float, lat: float, lng: float) -> Tuple:
    points_of_interest = []
    for cat in category:
        data = osm_query_amenity_data(
            category=cat,
            key="amenity",
            radius=radius,
            lat=lat,
            lng=lng
        )
        points_of_interest.append({cat: data})
    response = get_amenity_elements(
        payload=points_of_interest
    )

    return response


def calculate_distance(route_coordinates):
    total_distance = 0.0

    for i in range(len(route_coordinates) - 1):
        point1 = route_coordinates[i]
        point2 = route_coordinates[i + 1]
        distance = great_circle(point1, point2).meters
        total_distance += distance

    return total_distance

#TODO: disc powinien być pobierany jakoś z radius
#TODO: Chyba JS zapamiętuje ostatni punkt po wyczyszczeniu mapy i wstępnie generuje do niego drogę zamiast do wskazanych punktów
def generate_route_from_bbox(lat: float, lng: float, origin, destination):
    G = ox.graph_from_point((lat, lng), dist=1000, network_type="walk", simplify=True)
    origin_node_id = ox.nearest_nodes(G, origin["y"], origin["x"])
    destination_node_id = ox.nearest_nodes(G, destination["y"], destination["x"])
    route = ox.shortest_path(G, origin_node_id, destination_node_id)
    route_nodes = [G.nodes[node_id] for node_id in route]
    route_coordinates = [(node['y'], node['x']) for node in route_nodes]

    distance = calculate_distance(route_coordinates)

    return route_coordinates, round(distance, 1)