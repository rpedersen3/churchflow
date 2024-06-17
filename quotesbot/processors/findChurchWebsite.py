from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS
from urllib.parse import urlparse
import json


class FindChurchWebsite:


    churches_file_path = "churches.json"
    with open(churches_file_path, "r") as file:
        churchesData = json.load(file)
    churches = churchesData["churches"]



    def findChurchOrgWithDomain(self, churchOrgs, domain):

        for church in churchOrgs:

            if "link" in church:

                link = church["link"]
                parsed_url = urlparse(link)
                churchDomain = parsed_url.netloc.replace("www.", "")

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

                            parsed_url = urlparse(church["link"])
                            churchDomain = parsed_url.netloc.replace("www.", "")

                            if chDomain == churchDomain:
                                return ch


        return None


    def getRootName(self, church):
        return church["name"]


    def findChurchWebsite(self):

        print(" ........ updateRDFWithColocatedChurches")

        for church in self.churches:

            if "link" in church and "websiteUri" in church:

                link = church["link"]
                parsed_url = urlparse(link)
                linkDomain = parsed_url.netloc.replace("www.", "")

                website = church["websiteUri"]
                parsed_url = urlparse(website)
                websiteDomain = parsed_url.netloc.replace("www.", "")

                if linkDomain.lower() != websiteDomain.lower():

                    print("..................")
                    print("link: ", church["link"], ", websiteUri: ", church["websiteUri"])
                    print("name: ", church["name"])





