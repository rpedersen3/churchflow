from googleapiclient.discovery import build
from datetime import datetime
import json
import time
import requests
from urllib.parse import urlparse

from quotesbot.processors.updateChurchWithSocialData import UpdateChurchWithSocialData

from quotesbot.processors.findChurchOrganizations import FindChurchOrganizations
class FindMinistriesUsingGoogleSearch:

    def addMinistry(self, church, name, link, photo):

        ministries = []
        if "ministries" in church:
            ministries = church["ministries"]

        foundMinistry = False
        for ministry in ministries:
            ministryName = ministry["name"]
            if ministryName.lower().find(name.lower()) >= 0:
                foundMinistry = True
                break

        if foundMinistry == False:
            ministry = {
                "name": name,
                "link": link,
                "photo": photo,
                "phase": "pre-evangelism",
                "context-region": "local",
                "context-focus": "outreach",
                "partner": name
            }

            ministries.append((ministry))

        church["ministries"] = ministries

    def findMinistries(self, googleKey):

        # https://programmablesearchengine.google.com/controlpanel/overview?cx=d744719d644574dd7
        service = build(
            "customsearch", "v1", developerKey=googleKey
        )

        # get churches
        churches_file_path = "multiCampusChurches.json"
        with open(churches_file_path, "r") as file:
            churchesData = json.load(file)

        churches = churchesData["churches"]
        if churches == None:
            churches = []


        for church in churches:

            if "link" in church:

                link = church["link"]
                parsed_url = urlparse(link)
                churchDomain = parsed_url.netloc.replace("www.", "")

                '''
                searchTerm = "celebrate recovery"
                name = "celebrate recovery"
                photo = "https://celebraterecovery.com/wp-content/uploads/2024/03/Celebrate-Recovery-Logo-Left-White_RM.svg"
                caseMatch = False
                '''

                '''
                searchTerm = "griefshare"
                name = "grief share"
                photo = "https://www.griefshare.org/assets/logos/gs_white-fdf8435def3272cf1783fc0ec6e9a53c74328f282bc4ecbde4a37bfde2458ccc.svg"
                caseMatch = False
                '''

                '''
                searchTerm = "divorcecare"
                name = "divorce care"
                photo = "https://www.divorcecare.org/assets/logos/dc_white-8bdb21a230d39bd1928c8c51994bdebd70c82a20298e55a3cd7e923102217f09.svg"
                caseMatch = False
                '''

                '''
                searchTerm = "habitat for humanity"
                name = "habitat for humanity"
                photo = "https://habitatcolorado.org/wp-content/uploads/2022/08/logo.svg"
                caseMatch = False
                '''

                searchTerm = "Alpha"
                name = "habitat for humanity"
                photo = "https://habitatcolorado.org/wp-content/uploads/2022/08/logo.svg"
                caseMatch = True


                query = "site:" + churchDomain + " '" + searchTerm + "'"
                print("--------------------------------------")
                print("query: ", query)

                res = (
                    service.cse()
                    .list(
                        q=query,
                        cx="d744719d644574dd7"
                    )
                    .execute()
                )
                #print("--------------------------------------")
                #print(res)
                #print("--------------------------------------")

                found = 0
                if "items" in res:
                    for item in res["items"]:

                        snippet = item["snippet"]
                        if caseMatch == False:
                            snippet = snippet.lower()

                        if snippet.find(searchTerm) >= 0:

                            link = item["link"]
                            print("church: ", churchDomain)
                            print("found link: ", link)

                            self.addMinistry(church, name, link, photo)



        # save to churches file
        churchesData["churches"] = churches
        with open(churches_file_path, "w") as json_file:
            json.dump(churchesData, json_file, indent=4)