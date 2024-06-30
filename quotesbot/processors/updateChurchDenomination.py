from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS
from urllib.parse import urlparse
import json
import string
import random
import requests

class UpdateChurchDenomination:

    churches_file_path = "churches.json"
    with open(churches_file_path, "r") as file:
        churchesData = json.load(file)
    churches = sorted(churchesData["churches"])

    def saveChurches(self):

        # save to churches file
        self.churchesData["churches"] = self.churches
        with open(self.churches_file_path, "w") as json_file:
            json.dump(self.churchesData, json_file, indent=4)

    def updateChurchDeonominations(self):

        for church in self.churches:

            if "name" in church:

                name = church["name"].lower()

                if name.find("baptist") >= 0:




        self.saveChurches()


