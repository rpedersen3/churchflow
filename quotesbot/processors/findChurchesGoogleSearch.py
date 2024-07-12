from googleapiclient.discovery import build
from datetime import datetime
import json
import time

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



        starts = [1, 11, 21, 31, 41, 51]
        for st in starts:

            query = "'Christian Church' pueblo, colorado"
            print("query: ", query)
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

                            type = social["facebook"]["type"]
                            if self.checkFacebookType(type):

                                lnk = link.replace("https://www.facebook.com/", "").replace("http://www.facebook.com/", "")
                                name = lnk.split("/")[0]

                                church = {
                                    "name": name,
                                    "source": "facebook"
                                }

                                print('add church with facebook info: ', name, ", link: ", link)

                                church["social"] = social
                                churches.append(church)

                    # save to churches file
                    churchesData["churches"] = churches
                    with open(churches_file_path, "w") as json_file:
                        json.dump(churchesData, json_file, indent=4)



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
