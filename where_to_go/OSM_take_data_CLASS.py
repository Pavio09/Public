import folium
import requests
import webbrowser

CENTER_MAP = [51.768279, 19.456719]

class OSM:
    """Creates an html map based on the OSM API and opens it in a browser
    """
    def __init__(self, category, key, defult_msg="Brak"):
        self.default = defult_msg
        self.data = self.query_data(category, key)

    @classmethod
    def query_data(cls, category, key):
        cls.category = category
        cls.key = key
        overpass_url = 'http://overpass-api.de/api/interpreter'
        overpass_query = f"""
        [out:json];
        area["name"="Łódź"];
        (
            node(area)["{cls.key}"="{cls.category}"];
            way(area)["{cls.key}"="{cls.category}"];
            rel(area)["{cls.key}"="{cls.category}"];
        );
        out body;"""

        cls.response = requests.get(overpass_url, params= {'data' : overpass_query})
        cls.data = cls.response.json()

        return cls.data

    def containter_value(self):
        """Selects specific data from the OSM API

        Returns:
            list: dane wybrane z słownika API
        """
        list_values = []

        for value in self.data['elements']:
            try:
                inner_list = []
                inner_list.append(value['id'])
                if value['type'] == 'node':
                    inner_list.append(value['lon'])
                    inner_list.append(value['lat'])
                elif 'center' in value:
                    inner_list.append(value['center']['lat'])
                    inner_list.append(value['center']['lon'])
                inner_list.append(value['tags']['name'])
                inner_list.append((value['tags'].get('addr:street', self.default) + " " + value['tags'].get('addr:housenumber', self.default)))
                inner_list.append(value['tags'].get('website', self.default))
                inner_list.append(value['tags']['amenity'])
                list_values.append(inner_list)
            except:
                continue

        return list_values

    def make_map(self, path_for_map: str):
        """Creates a map of points with information based on data from the API

        Args:
            path_for_map (str): path for new map

        Returns:
           Open url in a new page ("tab") of the default browser with created map from OSM
        """
        self.zoom_start = 16
        self.default = 'Brak'
        self.location = CENTER_MAP

        self.map = folium.Map(location=CENTER_MAP, zoom_start=self.zoom_start)

        for element in self.data['elements']:
            if element['type'] == 'node':
                lon = element['lon']
                lat = element['lat']
            elif 'center' in element:
                lon = element['center']['lon']
                lat = element['center']['lat']
            if element['tags'].get('website', self.default) == self.default:
                strona = element['tags'].get('source', self.default)
            else:
                strona = element['tags'].get('website', self.default)
            try:
                folium.Marker(location = [lat, lon],
                            popup =
                            "Nazwa: "+element['tags']['name']+'<br>'+
                            "Adres: "+element['tags'].get('addr:street', self.default)+','+str(element['tags'].get('addr:housenumber', self.default)) +'<br>'+
                            "Strona www : "+ strona+'<br>'+
                            "Telefon: "+ str(element['tags'].get('phone', self.default))+'<br>'
                            ).add_to(self.map)
            except KeyError:
                pass

        self.map.save(path_for_map)

        return webbrowser.open_new_tab(path_for_map)

if __name__ == '__main__':
    path_for_map = ""
    amienity = ['pub', 'ice_cream', 'cafe', 'fast_food']
    osm = OSM(category='atm', key='amenity')
    osm.make_map()
