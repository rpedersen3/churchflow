from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS
from urllib.parse import urlparse
import json


class UpdateRDFWithMultiChurchOrgs:

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
        g2.add((churchCenterBusinessSystem, RDF.type, self.RC.ChurchmanagementSystem))
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


    def updateRDFWithMultiChurchOrgs(self):

        g2 = self.setupRDFFile()

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
                if domain.find("facebook") == -1 and domain.find("tripadvisor") == -1:

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
