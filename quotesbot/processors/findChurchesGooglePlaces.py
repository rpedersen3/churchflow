
from datetime import datetime
import json
import time
import requests

class FindChurchesGooglePlaces:


    # get churches
    churchesData = None
    churches_file_path = "churches.json"
    with open(churches_file_path, "r") as file:
        churchesData = json.load(file)

    churches = churchesData["churches"]
    if churches == None:
        churches = []


    def getChurchByGoogleId(self, googleId):

        for church in self.churches:
            if "googlePlaceId" in church:
                if church["googlePlaceId"] == googleId:
                    return church

        return None

    def setAddressInfoWithGoogleAddressComponents(self, components, currentChurch):

        addressInfo = {}
        if "addressInfo" in currentChurch:
            addressInfo = currentChurch["addressInfo"]

        streetNumber = None
        streetRoute = None
        city = None
        county = None
        state = None
        country = None
        zipcode = None

        for component in components:

            if component["types"][0] == "street_number":
                streetNumber =  component["longText"]
            if component["types"][0] == "route":
                streetRoute =  component["longText"]
            if component["types"][0] == "locality":
                city = component["longText"]
            if component["types"][0] == "administrative_area_level_2":
                county = component["longText"]
            if component["types"][0] == "administrative_area_level_1":
                state = component["shortText"]
            if component["types"][0] == "country":
                country = component["shortText"]
            if component["types"][0] == "postal_code":
                zipcode = component["shortText"]

            if streetNumber is not None and streetRoute is not None:
                addressInfo["street"] = streetNumber + " " + streetRoute
            if city is not None:
                addressInfo["city"] = city
            if county is not None:
                addressInfo["county"] = county
            if state is not None:
                addressInfo["state"] = state
            if country is not None:
                addressInfo["country"] = country
            if zipcode is not None:
                addressInfo["zipcode"] = zipcode

        currentChurch["addressInfo"] = addressInfo

    def updateChurchWithGoogleFindPlaceResults(self, currentChurch, data):

        if "place_id" in data:
            currentChurch["googlePlaceId"] = data["place_id"]
            print("google place id: ", currentChurch["googlePlaceId"])

        if "name" in data:
            currentChurch["name"] = data["name"]
            currentChurch["displayName"] = data["name"]
            print("google display name: ", currentChurch["name"])

        if "formatted_address" in data:
            currentChurch["formattedAddress"] = data["formatted_address"]

            addParts = currentChurch["formattedAddress"].split(",")
            if len(addParts) == 4:
                street = addParts[0].strip()
                city = addParts[1].strip()
                statezip = addParts[2].strip().split(" ")

                zipcode = None
                if len(statezip) > 1:
                    state = statezip[0]
                    zipcode = statezip[1]


                if street != '' and city != '' and zipcode != None:
                    addr = {
                        "street": street,
                        "city": city,
                        "state": "CO",
                        "country": "US",
                        "zipcode": zipcode,
                    }
                    currentChurch["addressInfo"] = addr



            print("google add: ", currentChurch["formattedAddress"])

        if "business_status" in data:
            currentChurch["businessStatus"] = data["business_status"]
            print("google businessStatus: ", currentChurch["businessStatus"])

    def updateChurchWithGoogleResults(self, currentChurch, data):

        if "id" in data:
            currentChurch["googlePlaceId"] = data["id"]
            print("google place id: ", currentChurch["googlePlaceId"])

        if "displayName" in data:
            currentChurch["name"] = data["displayName"]["text"]
            currentChurch["displayName"] = data["displayName"]["text"]
            print("google display name: ", currentChurch["displayName"])

        if "formattedAddress" in data:
            currentChurch["formattedAddress"] = data["formattedAddress"]
            print("google add: ", data["formattedAddress"])

        if "primaryType" in data:
            currentChurch["propertyType"] = data["primaryType"]
            print("google primaryType: ", data["primaryType"])
        elif "types" in data and len(data["types"]) > 0:
            propertyType = data["types"][0]
            currentChurch["propertyType"] = propertyType
            print("google propertyType: ", propertyType)

        if "location" in data:
            currentChurch["latitude"] = str(data["location"]["latitude"])
            currentChurch["longitude"] = str(data["location"]["longitude"])
            print("google latitude: ", str(data["location"]["latitude"]))

        if "rating" in data:
            currentChurch["rating"] = str(data["rating"])
            print("google rating: ", currentChurch["rating"])

        if "addressComponents" in data:
            self.setAddressInfoWithGoogleAddressComponents(data["addressComponents"], currentChurch)

        if "websiteUri" in data:
            currentChurch["link"] = data["websiteUri"]
            print("google websiteUri: ", data["websiteUri"])

        if "nationalPhoneNumber" in data:
            currentChurch["phone"] = data["nationalPhoneNumber"]
            currentChurch["nationalPhoneNumber"] = data["nationalPhoneNumber"]
            print("google nationalPhoneNumber: ", data["nationalPhoneNumber"])

        if "businessStatus" in data:
            currentChurch["businessStatus"] = data["businessStatus"]
            print("google businessStatus: ", data["businessStatus"])


    def saveChurches(self):

        # save to churches file
        self.churchesData["churches"] = self.churches
        with open(self.churches_file_path, "w") as json_file:
            json.dump(self.churchesData, json_file, indent=4)

    def findPlace(self, api_key, name, latitude, longitude):

        fields = ['formatted_address', 'name', 'geometry', 'place_id', 'business_status']


        url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json'
        params = {
            'key': api_key,
            'input': name,
            'inputtype': 'textquery',
            'locationbias': f'point:{latitude},{longitude}',
            'fields': ','.join(fields)
        }
        response = requests.get(url, params=params)
        return response.json()


    def updateChurch(self, church, googleApiKey):

        changed = False

        if "find-google-place" not in church:

            changed = True
            church["find-google-place"] = str(datetime.now())

            if "latitude" in church and "longitude" in church:
                print(" update church ............... ", church["name"])
                time.sleep(0.3)

                data = self.findPlace(googleApiKey, church["name"], church["latitude"], church["longitude"])

                print("************* json returned: ", data)

                if data != None and "candidates" in data and len(data["candidates"]) > 0:

                    candidate = data["candidates"][0]

                    print("update with candidate: ", candidate)
                    self.updateChurchWithGoogleFindPlaceResults(church, candidate)

                    changed = True


        return changed

    def findChurches(self, googleApiKey):

        # get cities
        file_path = "coloradoFrontRangeCities.json"
        with open(file_path, "r") as file:
            citiesData = json.load(file)

        # cycle through cities looking for church web sites
        cities = citiesData["cities"]
        selectedCity = None
        count = 1
        for city in cities:

            cityName = city["name"]

            if "crawled-google-places" not in city:

                city["crawled-google-places"] = str(datetime.now())

                time.sleep(1)

                api_key = googleApiKey
                endpoint = 'https://places.googleapis.com/v1/places:searchText' + "?fields=*&key=" + api_key

                query = city["name"] + " Colorado, Church"
                payload = {
                    "textQuery": query
                }
                if api_key == '':
                    print("api key is not set for getAddressInfoUsingGooglePlaces")
                    return

                time.sleep(1)


                response = requests.post(url=endpoint, json=payload)
                data = response.json()

                print("************* json returned: ", data)

                if "places" in data:
                    places = data["places"]
                    for place in places:

                        id = place["id"]
                        currentChurch = self.getChurchByGoogleId(id)

                        if currentChurch is None:
                            print("add church")
                            currentChurch = {}
                            self.updateChurchWithGoogleResults(currentChurch, place)

                            self.churches.append(currentChurch)
                            self.saveChurches()

