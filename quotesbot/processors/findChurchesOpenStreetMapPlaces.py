
from datetime import datetime
import json
import time
import requests

class FindChurchesOpenStreetMapPlaces:


    # get churches
    churchesData = None
    churches_file_path = "churches.json"
    with open(churches_file_path, "r") as file:
        churchesData = json.load(file)

    churches = churchesData["churches"]
    if churches == None:
        churches = []


    def getChurchByOpenStreetMapId(self, id):

        for church in self.churches:
            if "openStreetMapPlaceId" in church:
                if church["openStreetMapPlaceId"] == id:
                    return church

        return None

    def setAddressInfo(self, element, currentChurch):

        addressInfo = {}

        streetNumber = element['tags'].get('addr:housenumber', 'Unknown')
        streetRoute = element['tags'].get('addr:street', 'Unknown')
        zipcode = element['tags'].get('addr:postcode', 'Unknown')
        city = element['tags'].get('addr:city', 'Unknown')
        state = element['tags'].get('addr:state', 'Unknown')

        if "lat" in element:
            lat = element['lat']
            lon = element['lon']

        elif "center" in element:
            lat = element['center']['lat']
            lon = element['center']['lon']

        county = "" #vself.getCounty(lat, lon)

        state = "CO"
        country = "USA"

        addressInfo["street"] = streetNumber + " " + streetRoute
        addressInfo["city"] = city
        addressInfo["county"] = county
        addressInfo["state"] = state
        addressInfo["country"] = country
        addressInfo["zipcode"] = zipcode

        currentChurch["addressInfo"] = addressInfo

    def getCounty(self, lat, lon):
        nominatim_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10"
        response = requests.get(nominatim_url)
        if response.status_code == 200:
            data = response.json()
            address = data.get("address", {})
            return address.get("county", "Unknown County")
        else:
            return "Unknown County"

    def updateChurchWithResults(self, currentChurch, element):

        osm_id = str(element['id'])
        name = element['tags'].get('name', 'Unnamed')
        denomination = element['tags'].get('denomination', 'Unnamed')
        building = element['tags'].get('building', 'Unknown')
        operator = element['tags'].get('operator', 'Unknown')
        email = element['tags'].get('contact:email', 'Unknown')
        phone = element['tags'].get('contact:phone', 'Unknown')
        website = element['tags'].get('contact:website', 'Unknown')

        if "lat" in element:
            lat = element['lat']
            lon = element['lon']

        elif "center" in element:
            lat = element['center']['lat']
            lon = element['center']['lon']


        currentChurch["primarySource"] = "OpenStreetMap"

        currentChurch["openStreetMapPlaceId"] = osm_id
        print("open street map place id: ", osm_id)

        if name != "Unnamed":
            currentChurch["name"] = name
            currentChurch["displayName"] = name
            print("name: ", name)


        currentChurch["latitude"] = str(lat)
        currentChurch["longitude"] = str(lon)
        print("latitude: ", str(lat))

        self.setAddressInfo(element, currentChurch)

        if website != "Unknown":
            currentChurch["link"] = website
            currentChurch["websiteUri"] = website
            print("websiteUri: ", website)

        if email != "Unknown":
            currentChurch["email"] = email

        if phone != "Unknown":
            currentChurch["phone"] = phone

        if denomination != "Unnamed":
            currentChurch["denomination"] = denomination

        if operator != "Unknown":
            currentChurch["place-organization"] = operator

        if building != "Unknown":
            currentChurch["place-type"] = building

    def saveChurches(self):

        # save to churches file
        self.churchesData["churches"] = self.churches
        with open(self.churches_file_path, "w") as json_file:
            json.dump(self.churchesData, json_file, indent=4)


    def findChurches(self):

        # get cities
        file_path = "coloradoFrontRangeCities.json"
        with open(file_path, "r") as file:
            citiesData = json.load(file)

        overpass_query = """
        [out:json];
        area["name"="Colorado"]->.searchArea;
        (
          node["amenity"="place_of_worship"]["religion"="christian"](area.searchArea);
          way["amenity"="place_of_worship"]["religion"="christian"](area.searchArea);
          relation["amenity"="place_of_worship"]["religion"="christian"](area.searchArea);
        );
        out center;
        """

        overpass_url = "http://overpass-api.de/api/interpreter"

        # Make the HTTP request
        response = requests.get(overpass_url, params={'data': overpass_query})
        data = response.json()

        # Process and print the results
        for element in data['elements']:
            if element['type'] == 'node':

                # check if in front range region
                if "lat" in element:
                    lat = element['lat']
                    lon = element['lon']

                elif "center" in element:
                    lat = element['center']['lat']
                    lon = element['center']['lon']

                if lat > 38.0 and lat < 41.0 and lon > -106.0 and lon < -104.0:

                    osm_id = str(element['id'])
                    currentChurch = self.getChurchByOpenStreetMapId(osm_id)
                    if currentChurch == None:
                        currentChurch = {}
                        self.churches.append(currentChurch)

                    self.updateChurchWithResults(currentChurch, element)

            elif element['type'] == 'way' or element['type'] == 'relation':

                # check if in front range region
                if "lat" in element:
                    lat = element['lat']
                    lon = element['lon']

                elif "center" in element:
                    lat = element['center']['lat']
                    lon = element['center']['lon']

                if lat > 38.0 and lat < 41.0 and lon > -106.0 and lon < -104.0:

                    osm_id = str(element['id'])
                    currentChurch = self.getChurchByOpenStreetMapId(osm_id)
                    if currentChurch == None:
                        currentChurch = {}
                        self.churches.append(currentChurch)

                    self.updateChurchWithResults(currentChurch, element)

        self.saveChurches()

