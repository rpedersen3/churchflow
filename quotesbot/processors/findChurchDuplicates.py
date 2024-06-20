from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS
from urllib.parse import urlparse
import json
import string
import random
import requests

class FindChurchDuplicates:

    OWL = Namespace("http://www.w3.org/2002/07/owl#")
    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
    VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
    RC = Namespace("http://richcanvas.io/ns#")
    CC = Namespace("http://churchcore.io/ns#")
    FR = Namespace("http://churchcore.io/frontrange#")
    n = URIRef("http://churchcore.io/frontrange#")

    def myfunc(e):
        if 'primary-source' in e:
            return e['primary-source']
        return "abc"

    churches_file_path = "churches.json"
    with open(churches_file_path, "r") as file:
        churchesData = json.load(file)
    churches = sorted(churchesData["churches"], key=myfunc)


    def setupRDFFile(self):

        g2 = Graph()

        frontRangeFile = open('frontrange_out.rdf', errors="ignore")
        g2.parse(frontRangeFile, format="xml")

        g2.bind("owl", self.OWL)
        g2.bind("foaf", self.FOAF)
        g2.bind("geo", self.GEO)
        g2.bind("vcard", self.VCARD)
        g2.bind("rc", self.RC)
        g2.bind("cc", self.CC)
        g2.bind("fr", self.FR)


        glooOrgName = "gloo"
        glooOrgId = glooOrgName.replace(" ", "").lower()
        glooOrg = self.n + glooOrgId

        g2.add((glooOrg, RDF.type, self.OWL.NamedIndividual))
        g2.add((glooOrg, RDF.type, self.CC.MinistryOrganization))
        g2.add((glooOrg, self.RC.name, Literal(glooOrgName)))

        squarespaceBusinessSystemName = "squarespace"
        squarespaceBusinessSystemId = squarespaceBusinessSystemName.replace(" ", "").lower()
        squarespaceBusinessSystem = self.n + squarespaceBusinessSystemId

        g2.add((squarespaceBusinessSystem, RDF.type, self.OWL.NamedIndividual))
        g2.add((squarespaceBusinessSystem, RDF.type, self.RC.BusinessSystem))
        g2.add((squarespaceBusinessSystem, self.RC.name, Literal(squarespaceBusinessSystemName)))

        churchCenterBusinessSystemName = "churchcenter"
        churchCenterBusinessSystemId = churchCenterBusinessSystemName.replace(" ", "").lower()
        churchCenterBusinessSystem = self.n + churchCenterBusinessSystemId

        g2.add((churchCenterBusinessSystem, RDF.type, self.OWL.NamedIndividual))
        g2.add((churchCenterBusinessSystem, RDF.type, self.RC.ChurchManagementSystem))
        g2.add((churchCenterBusinessSystem, self.RC.name, Literal(churchCenterBusinessSystemName)))

        return g2

    def saveRDFFile(self, g2):

        #print(g2.serialize(format="pretty-xml"))
        data = g2.serialize(format="pretty-xml")

        with open('frontrange_out.rdf', "w", encoding="utf-8") as f:
            f.write(data)

    def clean(self, txt):

        import re
        pattern = re.compile(r'[^\x00-\x7F]+')
        d1 = pattern.sub('', txt)
        d2 = re.sub(r'&#\d+;', '', d1)
        d3 = d2.replace('"', '').replace(',', '').replace('#', '')
        d4 = d3.replace('\n', '').replace('\r', '').replace('\t', '')


        return d3

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

                    if (abs(chLatitude - latitude) < 0.003 and abs(chLongitude - longitude) < 0.003):

                        # find another thing to cause match

                        # if location match and openStreetMapPlaceId then just match it
                        if "openStreetMapPlaceId" in church:
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

        print(" ........ updateRDFWithColocatedChurches")

        g2 = self.setupRDFFile()

        # get a list of unique churches
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
                church["primary-source"] = "GooglePlaces"
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

                else:

                    church["is-primary"] = "no"
                    church["mergeChurches"] = []

                    addToChurches = True
                    if "openStreetMapPlaceId" not in church:
                        addToChurches = False

                    if addToChurches:
                        colocatedChurch["churches"].append(church)


        matched = 1
        for colocatedChurch in colocatedChurches:

            if len(colocatedChurch["churches"]) > 1:

                print("------------ ", matched)
                print("colocated churches")

                matched = matched + 1

                primaryChurch = colocatedChurch["churches"][0]
                mergeChurches = []
                offset = 0
                for ch in colocatedChurch["churches"]:

                    if offset >= 1:
                        mergeChurches.append(ch["uniqueId"])

                    offset = offset + 1

                primaryChurch["mergeChurches"] = mergeChurches


        self.saveChurches()


