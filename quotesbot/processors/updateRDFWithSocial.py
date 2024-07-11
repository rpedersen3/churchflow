from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS
from urllib.parse import urlparse
import json


class UpdateRDFWithSocial:

    OWL = Namespace("http://www.w3.org/2002/07/owl#")
    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
    VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
    RC = Namespace("http://richcanvas.io/ns#")
    CC = Namespace("http://churchcore.io/ns#")
    FR = Namespace("http://churchcore.io/frontrange#")
    n = URIRef("http://churchcore.io/frontrange#")


    socialNetworks = [
        {
            "name": "Facebook",
            "description": "",
            "websiteUri": "https://facebook.com"
        },
        {
            "name": "Youtube",
            "description": "",
            "websiteUri": "https://youtube.com"
        },
        {
            "name": "Linkedin",
            "description": "",
            "websiteUri": "https://Linkedin.com"
        },
        {
            "name": "Twitter",
            "description": "",
            "websiteUri": "https://Twitter.com"
        },
        {
            "name": "Pinterest",
            "description": "",
            "websiteUri": "https://Pinterest.com"
        },
        {
            "name": "Instragram",
            "description": "",
            "websiteUri": "https://Instragram.com"
        },
        {
            "name": "Tiktok",
            "description": "",
            "websiteUri": "https://Tiktok.com"
        }
    ]

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



        return g2

    def saveRDFFile(self, g2):

        #print(g2.serialize(format="pretty-xml"))
        data = g2.serialize(format="pretty-xml")

        with open('frontrange_out.rdf', "w", encoding="utf-8") as f:
            f.write(data)


    def updateRDFWithSocialNetworks(self):

        g2 = self.setupRDFFile()

        name = "Social Networks"
        socialNetworksId = name.replace(" ", "").lower()
        socialNetworks = self.n + socialNetworksId

        g2.add((socialNetworks, RDF.type, self.OWL.NamedIndividual))
        g2.add((socialNetworks, RDF.type, self.RC.EntityCollection))
        g2.add((socialNetworks, self.RC.name, Literal(name)))


        for socialNetworkRec in self.socialNetworks:

            name = socialNetworkRec["name"]
            socialNetworkId = name.replace(" ", "").lower()
            socialNetwork = self.n + socialNetworkId

            g2.add((socialNetwork, RDF.type, self.OWL.NamedIndividual))
            g2.add((socialNetwork, RDF.type, self.RC.SocialNetwork))
            g2.add((socialNetwork, self.RC.name, Literal(name)))

            g2.add((socialNetworks, self.RC.instance, socialNetwork))
            g2.add((socialNetwork, self.RC.instanceOf, socialNetworks))

        self.saveRDFFile(g2)