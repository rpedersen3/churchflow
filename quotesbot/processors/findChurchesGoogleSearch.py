from googleapiclient.discovery import build
from datetime import datetime
import json
import time
import requests
from urllib.parse import urlparse

from quotesbot.processors.updateChurchWithSocialData import UpdateChurchWithSocialData
class FindChurchesGoogleSearch:

    def checkFacebookType(self, type):
        valid = False

        type = type.lower()

        if type.find("church") >= 0:
            valid = True
        if type.find("religious organization") >= 0:
            valid = True
        if type.find("religious center") >= 0:
            valid = True
        if type.find("nonprofit organization") >= 0:
            valid = True
        if type.find("mission") >= 0:
            valid = True

        return valid


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
                streetNumber =  component["long_name"]
            if component["types"][0] == "route":
                streetRoute =  component["long_name"]
            if component["types"][0] == "locality":
                city = component["long_name"]
            if component["types"][0] == "administrative_area_level_2":
                county = component["long_name"]
            if component["types"][0] == "administrative_area_level_1":
                state = component["short_name"]
            if component["types"][0] == "country":
                country = component["short_name"]
            if component["types"][0] == "postal_code":
                zipcode = component["short_name"]

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

    def updateLocationInfoFromFacebookData(self, googleKey, church):

        changed = False

        print("process facebook lat lon .....................")

        address = None
        facebook = None
        if "source" in church and church["source"] == "facebook" and "social" in church:
            if "facebook" in church["social"]:
                facebook = church["social"]["facebook"]
                if "address" in church["social"]["facebook"]:
                    address = church["social"]["facebook"]["address"]

        if address == None:
            print("no address in facebook")
            return changed


        print("get address info ...............")
        endpoint = 'https://maps.googleapis.com/maps/api/geocode/json'

        if googleKey == '':
            print("api key is not set for getAddressInfoUsingGooglePlaces")
            return changed


        params = {
            'address': address,
            'key': googleKey
        }

        response = requests.get(endpoint, params=params)
        data = response.json()


        if "results" in data:
            if len(data["results"]) > 0:
                result = data["results"][0]
                if "address_components" in result:
                    changed = True
                    components = result["address_components"]
                    self.setAddressInfoWithGoogleAddressComponents(components, church)

                if "geometry" in result:
                    if "location" in result["geometry"]:
                        location = result["geometry"]["location"]
                        if "lat" in location and "lng" in location:
                            changed = True
                            latitude = location["lat"]
                            longitude = location["lng"]

                            facebook["latitude"] = str(latitude)
                            facebook["longitude"] = str(longitude)

        #print("data: ", data)
        print("************** church info: ", church)
        return changed


    def findChurchesFromTheOrg(self, googleKey):

        service = build(
            "customsearch", "v1", developerKey=googleKey
        )

        # get churches
        churches_file_path = "churches.json"
        with open(churches_file_path, "r") as file:
            churchesData = json.load(file)

        churches = churchesData["churches"]
        if churches == None:
            churches = []


        for church in churches:

            if "theorg" not in churches:

                link = church["link"]
                parsed_url = urlparse(link)
                churchDomain = parsed_url.netloc.replace("www.", "")
                churchDomain = churchDomain.replace("/", "")

                query = churchDomain
                print("query: ", query)

                res = (
                    service.cse()
                    .list(
                        q=query,
                        cx="951f3778240354b1a",
                        start=1
                    )
                    .execute()
                )
                print("--------------------------------------")
                # print(res)
                print("--------------------------------------")

                for item in res["items"]:

                    link = item["link"]

                    church["theorg"] = {
                        "url": link
                    }

                    # save to churches file
                    churchesData["churches"] = churches
                    with open(churches_file_path, "w") as json_file:
                        json.dump(churchesData, json_file, indent=4)

                    break


    def findChurchesFromFacebook(self, googleKey):

        # https://programmablesearchengine.google.com/controlpanel/overview?cx=d744719d644574dd7
        service = build(
            "customsearch", "v1", developerKey=googleKey
        )

        # get churches
        churches_file_path = "churches.json"
        with open(churches_file_path, "r") as file:
            churchesData = json.load(file)

        churches = churchesData["churches"]
        if churches == None:
            churches = []



        # 'Christian Church'   pueblo, erie, colorado springs, denver, boulder, windsor
        # 'Religious organization'   pueblo
        # 'Religious Center'   pueblo
        cities = ["pueblo", "erie", "colorado springs", "denver", "boulder", "windsor", "westminster"]
        cities = ["larkspur"]
        terms = ["Religious organization",
                 "Religious Center",
                 "Christian Church",
                 "Nondenominational Church",
                 "Interdenominational Church",
                 "Anglican Church",
                 "Lutheran Church",
                 "Catholic Church",
                 "Methodist Church",
                 "Episcopal Church",
                 "Baptist Church",
                 "Presbyterian Church",
                 "Nazarene Church",
                 "Assemblies of God",
                 "Evangelical Church",
                 "Congregational Church",
                 "Church of God",
                 "Charismatic Church",
                 "Church of Christ",
                 "Eastern Orthodox Church",
                 "Seventh Day Adventist Church",
                 "Apostolic Church",
                 "Pentecostal Church",
                 "Independent Church",
                 "Church",
                 ]


        for city in cities:

                for term in terms:

                    query = "'" + term + "' " + city + ", colorado"
                    print("query: ", query)

                    #starts = [1, 11, 21, 31, 41, 51]
                    starts = [1, 11]
                    for st in starts:


                        res = (
                            service.cse()
                            .list(
                                q=query,
                                cx="2612db1d6c3494ff0",
                                start=st
                            )
                            .execute()
                        )
                        print("--------------------------------------")
                        #print(res)
                        print("--------------------------------------")

                        found = 0
                        for item in res["items"]:

                            link = item["link"]
                            dashCount = len(link.split("/"))
                            if link.find('?') == -1 and \
                                    link.find('&') == -1 and \
                                    link.find('/posts') == -1 and \
                                    link.find('/people') == -1 and \
                                    link.find('/photos') == -1 and \
                                    link.find('/events') == -1 and \
                                    link.endswith('/'):

                                print("link: ", link, ",  dashCount: ", dashCount)

                                found = found + 1


                                # looking for existing church with this link
                                foundChurch = None
                                for church in churches:
                                    if "social" in church and "facebookUrl" in church["social"]:
                                        if church["social"]["facebookUrl"].replace("www.", "").replace("https://", "").replace("http://", "").replace("/", "").lower().strip() == link.replace("www.", "").replace("https://", "").replace("http://", "").replace("/", "").lower().strip():
                                            foundChurch = church
                                            print("************* found church: ", church["name"])
                                            break

                                if foundChurch == None:
                                    social = {
                                        "facebookUrl": link
                                    }

                                    update = UpdateChurchWithSocialData()
                                    update.processFacebook(link, social)
                                    if "facebook" in social and "type" in social["facebook"]:

                                        facebook = social["facebook"]
                                        type = facebook["type"]
                                        if self.checkFacebookType(type):

                                            lnk = link.replace("https://www.facebook.com/", "").replace("http://www.facebook.com/", "")
                                            name = lnk.split("/")[0]

                                            if "name" in facebook:
                                                name = facebook["name"]

                                            church = {
                                                "name": name,
                                                "primarySource": "Facebook",
                                                "social": social
                                            }

                                            changed = self.updateLocationInfoFromFacebookData(googleKey, church)



                                            if "latitude" in facebook and "longitude" in facebook:

                                                church["latitude"] = facebook["latitude"]
                                                church["longitude"] = facebook["longitude"]

                                                print('add church with facebook info: ', name, ", link: ", link)

                                                church["social"] = social

                                                churches.append(church)



                                # save to churches file
                                churchesData["churches"] = churches
                                with open(churches_file_path, "w") as json_file:
                                    json.dump(churchesData, json_file, indent=4)

        '''
        for church in churches:

            # update lat, lon and addressinfo
            if "source" in church and church["source"] == "facebook" and "addressInfo" not in church:

                time.sleep(0.3)

                self.updateLocationInfoFromFacebookData(googleKey, church)

                # save to churches file
                churchesData["churches"] = churches
                with open(churches_file_path, "w") as json_file:
                    json.dump(churchesData, json_file, indent=4)
        '''

    def findChurches(self, googleKey):

        # https://programmablesearchengine.google.com/controlpanel/overview?cx=d744719d644574dd7
        service = build(
            "customsearch", "v1", developerKey=googleKey
        )

        # get churches
        churches_file_path = "churches.json"
        with open(churches_file_path, "r") as file:
            churchesData = json.load(file)

        churches = churchesData["churches"]
        if churches == None:
            churches = []

        # get cities
        file_path = "coloradoFrontRangeCities.json"
        with open(file_path, "r") as file:
            citiesData = json.load(file)

        # cycle through cities looking for church web sites
        cities = citiesData["cities"]
        count = 1

        for city in cities:

            if "crawled" not in city:

                city["crawled"] = str(datetime.now())
                city["crawled-city"] = city["name"]

                time.sleep(5)

                count = count + 1
                if count > 100:
                    break

                starts = [1, 11, 21, 31, 41, 51]

                for st in starts:

                    query = "'" + city["name"] + "' colorado christian church websites"
                    print("query: ", query)
                    res = (
                        service.cse()
                        .list(
                            q=query,
                            cx="d744719d644574dd7",
                            start=st
                        )
                        .execute()
                    )
                    print("--------------------------------------")
                    print(res)
                    print("--------------------------------------")

                    found = 0
                    for item in res["items"]:

                        link = item["link"]
                        dashCount = len(link.split("/"))
                        print("link: ", link, ",  dashCount: ", dashCount)
                        if link.find('?') == -1 and \
                                link.find('&') == -1 and \
                                dashCount <= 4 and \
                                link.find("linkedin") == -1 and \
                                link.find(".gov") == -1 :

                            found = found + 1

                            name = item["displayLink"]
                            name = name.replace('www.', '')
                            name = name.replace('.com', '')
                            name = name.replace('.org', '')
                            name = name.replace('.net', '')
                            name = name.replace('.church', '')

                            # looking for existing church with this link
                            selectedChurch = None
                            for church in churches:
                                if "link" in church and church["link"] == link:
                                    selectedChurch = church
                                    break

                            if selectedChurch == None:
                                print("add church: ", name)
                                church = {
                                    "link": link,
                                    "name": name
                                }
                                churches.append(church)

                                print('link: ', item["link"])

                            # save to churches file
                            churchesData["churches"] = churches
                            with open(churches_file_path, "w") as json_file:
                                json.dump(churchesData, json_file, indent=4)

                            # save cities crawled
                            citiesData["cities"] = cities
                            with open(file_path, "w") as json_file:
                                json.dump(citiesData, json_file, indent=4)



        '''
    
        service = build("customsearch", "v1", developerKey=api_key)
    
        search_engine_id = "d744719d644574dd7"
        api_version = "v1"
        search_engine = service.cse().liste_(cx=search_enginid, version=api_version)
    
        query = "zenserp API tutorials"
        search_engine.q = query
        response = search_engine.execute()
        results = response["items"]
    
        print("results: ", results)
        '''
