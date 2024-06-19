
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

        lat = element['lat']
        lon = element['lon']

        county = self.getCounty(lat, lon)

        state = "CO"
        country = "USA"

        addressInfo["street"] = streetNumber + " " + streetRoute
        addressInfo["city"] = city
        addressInfo["county"] = county
        addressInfo["state"] = state
        addressInfo["country"] = country
        addressInfo["zipcode"] = zipcode

        currentChurch["addressInfo"] = addressInfo

    def getCounty(lat, lon):
        nominatim_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10"
        response = requests.get(nominatim_url)
        if response.status_code == 200:
            data = response.json()
            address = data.get("address", {})
            return address.get("county", "Unknown County")
        else:
            return "Unknown County"

    def updateChurchWithResults(self, currentChurch, element):

        osm_id = element['id']
        name = element['tags'].get('name', 'Unnamed')
        lat = element['lat']
        lon = element['lon']
        denomination = element['tags'].get('denomination', 'Unnamed')
        building = element['tags'].get('building', 'Unknown')
        operator = element['tags'].get('operator', 'Unknown')
        email = element['tags'].get('contact:email', 'Unknown')
        phone = element['tags'].get('contact:phone', 'Unknown')
        website = element['tags'].get('contact:website', 'Unknown')

        currentChurch["primary-source"] = "OpenStreetMap"

        currentChurch["openStreetMapPlaceId"] = osm_id
        print("open street map place id: ", osm_id)

        if name is not "Unnamed":
            currentChurch["name"] = name
            currentChurch["displayName"] = name
            print("name: ", name)


        currentChurch["latitude"] = str(lat)
        currentChurch["longitude"] = str(lon)
        print("latitude: ", str(lat))

        self.setAddressInfo(element, currentChurch)

        if website is not "Unknown":
            currentChurch["link"] = website
            currentChurch["websiteUri"] = website
            print("websiteUri: ", website)

        if email is not "Unknown":
            currentChurch["email"] = email

        if phone is not "Unknown":
            currentChurch["phone"] = phone

        if denomination is not "Unknown":
            currentChurch["denomination"] = denomination

        if operator is not "Unknown":
            currentChurch["place-organization"] = operator

        if building is not "Unknown":
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

                osm_id = element['id']
                currentChurch = self.getChurchByOpenStreetMapId(osm_id)
                if currentChurch == None:
                    currentChurch = {}

                self.updateChurchWithResults(currentChurch, element)

            elif element['type'] == 'way' or element['type'] == 'relation':

                osm_id = element['id']
                currentChurch = self.getChurchByOpenStreetMapId(osm_id)
                if currentChurch == None:
                    currentChurch = {}

                self.updateChurchWithResults(currentChurch, element)

        self.saveChurches()

