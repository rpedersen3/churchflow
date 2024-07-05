from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS
from urllib.parse import urlparse
import json


class UpdateRDFWithNetworks:

    OWL = Namespace("http://www.w3.org/2002/07/owl#")
    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
    VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
    RC = Namespace("http://richcanvas.io/ns#")
    CC = Namespace("http://churchcore.io/ns#")
    FR = Namespace("http://churchcore.io/frontrange#")
    n = URIRef("http://churchcore.io/frontrange#")


    networks = [
        {
            "name": "Calvary Chapel",
            "description": "",
            "websiteUri": "https://calvarychapel.com/church-locator/",
            "tags": ["calvary chapel"]
        },
        {
            "name": "Converge Rock Mountain",
            "description": "",
            "websiteUri": "https://www.convergerockymountain.org/churches/",
            "tags": ["converge"]
        },
        {
            "name": "Evangelical Lutheran Church in America",
            "description": "",
            "websiteUri": "https://search.elca.org/Pages/WorldMap.aspx",
            "tags": ["elca", "evangelical lutheran church"]
        },
        {
            "name": "Archdioces of Denver",
            "description": "",
            "websiteUri": "https://archden.org/parish-locator/",
            "tags": ["archdioces of denver"]
        },
        {
            "name": "The Calvary",
            "description": "",
            "websiteUri": "https://thecalvary.org/churches/",
            "tags": ["the calvary"]
        },
        {
            "name": "SBC",
            "description": "",
            "websiteUri": "https://churches.sbc.net/?_search=39.7392358%2C-104.990251%2C100%2CDenver%252C%2520CO%252C%2520USA",
            "tags": ["sbc"]
        },
        {
            "name": "Venture Church Network",
            "description": "",
            "websiteUri": "https://venturechurches.org/search-vcn-churches/?_state=co",
            "tags": ["vcn", "venture church network"]
        },
        {
            "name": "Evangelical Free Church",
            "description": "",
            "websiteUri": "https://churches.efca.org/?s=colorado",
            "tags": ["efc", "evangelical free church"]
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


    def updateRDFWithNetworks(self):

        g2 = self.setupRDFFile()


        for ntwk in self.networks:

            name = ntwk["name"]
            networkId = name.replace(" ", "").lower() + "_network"
            network = self.n + networkId

            g2.add((network, RDF.type, self.OWL.NamedIndividual))
            g2.add((network, RDF.type, self.CC.Network))
            g2.add((network, self.RC.name, Literal(name)))

            tags = ntwk["tags"]
            for tagName in tags:

                tagId = tagName.replace(" ", "").lower() + "tag"
                tag = self.n + tagId

                g2.add((tag, RDF.type, self.OWL.NamedIndividual))
                g2.add((tag, RDF.type, self.CC.NetworkTag))
                g2.add((tag, self.RC.name, Literal(tagName)))

                g2.add((network, self.CC.networkTag, tag))
                
                

        self.saveRDFFile(g2)