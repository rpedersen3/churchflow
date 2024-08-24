from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS
from urllib.parse import urlparse
import json


class FindMultiCampusChurches:

    OWL = Namespace("http://www.w3.org/2002/07/owl#")
    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
    VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
    RC = Namespace("http://richcanvas.io/ns#")
    CC = Namespace("http://churchcore.io/ns#")
    FR = Namespace("http://churchcore.io/frontrange#")
    n = URIRef("http://churchcore.io/frontrange#")

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


    def findChurchWithSameLocation(self, matchChurches, church):

        for ch in matchChurches:

            if "latitude" in ch and "longitude" in ch:

                chLatitude = float(ch["latitude"])
                chLongitude = float(ch["longitude"])

                if "latitude" in church and "longitude" in church:

                    latitude = float(church["latitude"])
                    longitude = float(church["longitude"])

                    if (abs(chLatitude - latitude) < 0.001 and abs(chLongitude - longitude) < 0.001):
                        return ch

        return None


    def getRootName(self, church):
        return church["name"]


    def findMultiCampusChurches(self):

        # get a list of unique churches
        uniqueChurches = []
        for church in self.churches:
            if self.findChurchWithSameLocation(uniqueChurches, church) is None:
                uniqueChurches.append(church)

        # cluster church orgs
        churchOrgs = []
        for church in uniqueChurches:


            if "name" not in church:
                return


            if "name" in church and "link" in church:

                link = church["link"]
                parsed_url = urlparse(link)
                domain = parsed_url.netloc.replace("www.", "")

                # not a social website
                if domain.find("facebook") == -1:

                    foundChurchOrg = self.findChurchOrgWithDomain(churchOrgs, domain)
                    if foundChurchOrg is None:
                        rootName = self.getRootName(church)
                        rootLink = "https://www." + domain
                        foundChurchOrg = {
                            "name": rootName,
                            "link": rootLink,
                            "subChurches": []
                        }

                        churchOrgs.append(foundChurchOrg)

                    foundChurchOrg["subChurches"].append(church)


        for churchOrg in churchOrgs:

            if (len(churchOrg["subChurches"]) > 1):

                print("multi church org: ", churchOrg["name"], ', ', churchOrg["link"])
                for subChurch in churchOrg["subChurches"]:
                    print(".... ", subChurch["name"], ", ", subChurch["link"])
