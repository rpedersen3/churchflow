from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS
from urllib.parse import urlparse
import json


class UpdateRDFWithPartners:

    OWL = Namespace("http://www.w3.org/2002/07/owl#")
    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
    VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
    RC = Namespace("http://richcanvas.io/ns#")
    CC = Namespace("http://churchcore.io/ns#")
    FR = Namespace("http://churchcore.io/frontrange#")
    n = URIRef("http://churchcore.io/frontrange#")


    partners = [
        {
            "name": "Interfaith Alliance",
            "description": "",
            "websiteUri": "https://interfaithallianceco.org/partners/",
            "tags": ["interfaith alliance"]
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


    def updateRDFWithPartners(self):

        g2 = self.setupRDFFile()


        for ptnr in self.partners:

            name = ptnr["name"]
            partnerId = name.replace(" ", "").lower() + "_network"
            partner = self.n + partnerId

            g2.add((partner, RDF.type, self.OWL.NamedIndividual))
            g2.add((partner, RDF.type, self.CC.Partner))
            g2.add((partner, self.RC.name, Literal(name)))

            tags = ptnr["tags"]
            for tagName in tags:

                tagId = tagName.replace(" ", "").lower() + "tag"
                tag = self.n + tagId

                g2.add((tag, RDF.type, self.OWL.NamedIndividual))
                g2.add((tag, RDF.type, self.CC.PartnerTag))
                g2.add((tag, self.RC.name, Literal(tagName)))

                g2.add((partner, self.CC.partnerTag, tag))
                
                

        self.saveRDFFile(g2)