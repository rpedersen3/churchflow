from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS
from urllib.parse import urlparse
import json


class FindChurchDuplicates:

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


    def findChurchDuplicates(self):

        print(" ........ updateRDFWithColocatedChurches")

        g2 = self.setupRDFFile()

        # get a list of unique churches
        colocatedChurches = []
        for church in self.churches:

            if "latitude" in church and "longitude" in church:
                colocatedChurch = self.findChurchMatch(colocatedChurches, church)
                if colocatedChurch is None:
                    colocatedChurch = {
                        "latitude": church["latitude"],
                        "longitude": church["longitude"],
                        "churches": []
                    }

                    # find another thing
                    foundAnotherThing = False
                    if "googlePlaceId" in church:
                        colocatedChurch["googlePlaceId"] = church["googlePlaceId"]

                    if "ein" in church:
                        colocatedChurch["ein"] = church["ein"]

                    if "name" in church:
                        colocatedChurch["name"] = church["name"]

                    if "link" in church:
                        colocatedChurch["link"] = church["link"]



                    colocatedChurch["churches"].append(church)
                    colocatedChurches.append(colocatedChurch)

                else:
                    colocatedChurch["churches"].append(church)


        for colocatedChurch in colocatedChurches:

            if len(colocatedChurch["churches"]) > 1:
                print("colocated churches")
                for ch in colocatedChurch["churches"]:
                    print(".... name: ", ch["name"])

