from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS
from urllib.parse import urlparse
import json
import string
import random

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
            "link": "https://interfaithallianceco.org",
            "tags": ["interfaith alliance"]
        },
        {
            "name": "Alpha",
            "description": "",
            "link": "https://alphausa.org",
            "tags": ["alpha"]
        },
        {
            "name": "Gloo",
            "description": "",
            "link": "https://www.gloo.us",
            "tags": ["gloo"]
        },
        {
            "name": "HeGetsUs",
            "description": "",
            "link": "https://hegetsus.com/",
            "tags": ["hegetsus"]
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

    def generate_random_string(self):

        length = 12

        # Define the characters to choose from: lowercase, uppercase, digits, hyphens, underscores, and periods
        characters = string.ascii_letters + string.digits + '-_.'
        # Generate a random ID by selecting random characters from the character set
        random_id = ''.join(random.choice(characters) for _ in range(length))
        return random_id

    def updateRDFWithPartners(self):

        g2 = self.setupRDFFile()


        for ptnr in self.partners:


            name = ptnr["name"]
            partnerId = name.replace(" ", "").lower()
            partner = self.n + partnerId

            g2.add((partner, RDF.type, self.OWL.NamedIndividual))
            g2.add((partner, RDF.type, self.CC.MinistryOrganization))
            g2.add((partner, self.RC.name, Literal(name)))

            if "link" in ptnr:
                websiteUri = ptnr["link"];
                websiteId = self.generate_random_string()  # self.clean(websiteUri.replace(" ", "").lower())
                website = self.n + websiteId

                g2.add((website, RDF.type, self.OWL.NamedIndividual))
                g2.add((website, self.RC.type, self.RC.Website))
                g2.add((website, self.RC.uri, Literal(websiteUri)))

                g2.add((partner, self.RC.hasWebsite, website))

            tags = ptnr["tags"]
            for tagName in tags:

                tagId = tagName.replace(" ", "").lower() + "tag"
                tag = self.n + tagId

                g2.add((tag, RDF.type, self.OWL.NamedIndividual))
                g2.add((tag, RDF.type, self.RC.Tag))
                g2.add((tag, self.RC.name, Literal(tagName)))

                g2.add((partner, self.RC.hasTag, tag))
                
                

        self.saveRDFFile(g2)