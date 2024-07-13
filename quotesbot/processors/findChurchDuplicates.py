from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS
from urllib.parse import urlparse
import json
import string
import random
import requests

class FindChurchDuplicates:

    def orderFunc(e):
        if 'latitude' not in e:
            return "znolocation"

        if 'primarySource' in e:
            return e['primarySource']

        return "ynoprimarysource"

    churches_file_path = "churches.json"
    with open(churches_file_path, "r") as file:
        churchesData = json.load(file)
    churches = sorted(churchesData["churches"], key=orderFunc)



    def findChurchOrgWithDomain(self, churchOrgs, domain):

        for church in churchOrgs:

            if "link" in church:

                domain = domain.replace("/", "")

                link = church["link"]
                parsed_url = urlparse(link)
                churchDomain = parsed_url.netloc.replace("www.", "")
                churchDomain = churchDomain.replace("/", "")

                if domain.lower() == churchDomain.lower():

                    return church

        return None


    def findChurchMatch(self, matchChurches, church):

        for ch in matchChurches:

            if "latitude" in ch and "longitude" in ch:

                chLatitude = float(ch["latitude"])
                chLongitude = float(ch["longitude"])

                if "latitude" in church and "longitude" in church:

                    latitude = float(church["latitude"])
                    longitude = float(church["longitude"])

                    if (abs(chLatitude - latitude) < 0.001 and abs(chLongitude - longitude) < 0.001):

                        # find another thing to cause match

                        # if location match and openStreetMapPlaceId then just match it
                        if "openStreetMapPlaceId" in church:
                            return ch

                        # if source is facebook then just match it
                        if "source" in church and church["source"] == "facebook":
                            return ch

                        if "googlePlaceId" in ch and "googlePlaceId" in church:
                            if ch["googlePlaceId"] == church["googlePlaceId"]:
                                return ch

                        if "ein" in ch and "ein" in church:
                            if ch["ein"] == church["ein"]:
                                return ch

                        if "name" in ch and "name" in church:
                            if ch["name"].lower() == church["name"].lower():
                                return ch

                        if "link" in ch and "link" in church:

                            parsed_url = urlparse(ch["link"])
                            chDomain = parsed_url.netloc.replace("www.", "")
                            chDomain = chDomain.replace("/", "")

                            parsed_url = urlparse(church["link"])
                            churchDomain = parsed_url.netloc.replace("www.", "")
                            churchDomain = churchDomain.replace("/", "")

                            if chDomain == churchDomain:
                                return ch


        return None

    def findChurchMatchUsingNonLocationInfo(self, matchChurches, church):

        returnCh = None
        for ch in matchChurches:



            if "link" in ch and "link" in church:

                parsed_url = urlparse(ch["link"])
                chDomain = parsed_url.netloc.replace("www.", "")
                chDomain = chDomain.replace("/", "")

                parsed_url = urlparse(church["link"])
                churchDomain = parsed_url.netloc.replace("www.", "")
                churchDomain = churchDomain.replace("/", "")

                if chDomain.lower() == churchDomain.lower():
                    returnCh = ch
                    #return ch

            if "ein" in ch and "ein" in church:
                if ch["ein"] == church["ein"]:
                    returnCh = ch
                    #return ch

            if "name" in ch and "name" in church:
                if ch["name"].lower() == church["name"].lower():
                    returnCh = ch
                    #return ch

        return returnCh


    def getRootName(self, church):
        return church["name"]


    def saveChurches(self):

        # save to churches file
        self.churchesData["churches"] = self.churches
        with open(self.churches_file_path, "w") as json_file:
            json.dump(self.churchesData, json_file, indent=4)

    def generateRandomString(self):

        length = 12

        # Define the characters to choose from: lowercase, uppercase, digits, hyphens, underscores, and periods
        characters = string.ascii_letters + string.digits + '-_.'
        # Generate a random ID by selecting random characters from the character set
        random_id = ''.join(random.choice(characters) for _ in range(length))
        return random_id

    def geocodeAddress(self, address):

        url = 'https://nominatim.openstreetmap.org/search?format=json&email=richardpedersen3@gmail.com&q=' + address
        '''
            params = {
            'q': address,
            'format': 'json'
        }
        response = requests.get(url, params=params)
        '''
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data:
                return data[0]['lat'], data[0]['lon']
            else:
                print('Address not found')
                return None, None
        else:
            print('Error:', response.status_code)
            return None, None

    def findChurchDuplicates(self):

        # get a list of unique churches
        noLocationChurchCount = 0
        colocatedChurches = []
        for church in self.churches:

            if "uniqueId" not in church:
                church["uniqueId"] = self.generateRandomString()

            '''
            if "latitude" not in church and "longitude" not in church and "address" in church:
                print("get lat lon for: ", church["address"])
                lat, lon = self.geocodeAddress(church["address"])
                if lat != None and lon != None:
                    print("set lat: ", lat, ", lon: ", lon)
                    church["latitude"] = str(lat)
                    church["longitude"] = str(lon)

            if "addressInfo" not in church and "address" in church:
                print("get address info for: ", church["address"])
                addParts = church["address"].split(",")
                if len(addParts) == 4:
                    street = addParts[0].strip()
                    city = addParts[1].strip()
                    zipcode = addParts[3].strip()

                    if street != '' and city != '' and zipcode != '':
                        addr = {
                            "street": addParts[0].strip(),
                            "city": addParts[1].strip(),
                            "state": "CO",
                            "country": "US",
                            "zipcode": addParts[3].strip(),
                        }
                        print("set address: ", addr)
                        church["addressInfo"] = addr
            

            if "googlePlaceId" in church:
                church["primarySource"] = "GooglePlaces"
            '''

            church["is-primary"] = "yes"
            church["mergeChurches"] = []

            if "latitude" in church and "longitude" in church:
                colocatedChurch = self.findChurchMatch(colocatedChurches, church)
                if colocatedChurch is None:

                    colocatedChurch = {
                        "latitude": church["latitude"],
                        "longitude": church["longitude"],
                        "churches": []
                    }

                    if "googlePlaceId" in church:
                        colocatedChurch["googlePlaceId"] = church["googlePlaceId"]
                    if "openStreetMapPlaceId" in church:
                        colocatedChurch["openStreetMapPlaceId"] = church["openStreetMapPlaceId"]

                    if "ein" in church:
                        colocatedChurch["ein"] = church["ein"]

                    if "name" in church:
                        colocatedChurch["name"] = church["name"]

                    if "link" in church:
                        link = church["link"]
                        colocatedChurch["link"] = link

                    colocatedChurch["churches"].append(church)
                    colocatedChurches.append(colocatedChurch)

                elif "location" in church:
                    # example of christinthecity.org which is a mission outreach in denver
                    church["is-primary"] = "yes"

                else:

                    church["is-primary"] = "no"
                    church["mergeChurches"] = []

                    addToChurches = False
                    if "source" in church:
                        addToChurches = True
                    if "openStreetMapPlaceId" in church:
                        addToChurches = True

                    if addToChurches:
                        colocatedChurch["churches"].append(church)
            else:
                church["is-primary"] = "no"
                matchedChurch = self.findChurchMatchUsingNonLocationInfo(colocatedChurches, church)
                if matchedChurch == None:

                    noLocationChurchCount = noLocationChurchCount + 1
                    website = ''
                    if "link" in church:
                        website = church["link"]
                    print("church without location (", noLocationChurchCount, "): ", church["name"], "  ", website)

        matched = 0
        for colocatedChurch in colocatedChurches:

            if len(colocatedChurch["churches"]) > 1:

                if "name" in colocatedChurch:
                    print("colocated church", colocatedChurch["name"])

                matched = matched + 1
                primaryChurch = colocatedChurch["churches"][0]
                mergeChurches = []
                offset = 0
                for ch in colocatedChurch["churches"]:

                    if offset >= 1:

                        #if "name" in ch:
                        #    print("add mergeChurch: ", ch["name"])
                        if "source" in ch and ch["source"] == "facebook":
                            print("add mergeChurch: ", ch["name"])

                        mergeChurches.append(ch["uniqueId"])

                    offset = offset + 1

                primaryChurch["mergeChurches"] = mergeChurches


        print("matched churches: ", matched)
        self.saveChurches()


