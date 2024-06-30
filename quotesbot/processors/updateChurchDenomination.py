from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS
from urllib.parse import urlparse
import json
import string
import random
import requests

class UpdateChurchDenomination:


    def updateChurchDeonomination(self, church):

        changed = False

        if "denomination" not in church and "name" in church:

            name = church["name"].lower()

            if name.find("baptist") >= 0:
                church["denomination"] = "baptist"

            elif name.find("catholic") >= 0:
                church["denomination"] = "catholic"
            elif name.find("sacred heart") >= 0:
                church["denomination"] = "catholic"
            elif name.find("our lady") >= 0:
                church["denomination"] = "catholic"

            elif name.find("united methodist") >= 0:
                church["denomination"] = "united methodist church"

            elif name.find("presbyterian") >= 0:
                church["denomination"] = "presbyterian"

            elif name.find("united church of christ") >= 0:
                church["denomination"] = "united church of christ"

            elif name.find("apostolic") >= 0:
                church["denomination"] = "apostolic"

            elif name.find("lutheran") >= 0:
                church["denomination"] = "lutheran"

            elif name.find("episcopal") >= 0:
                church["denomination"] = "episcopal"


            elif name.find("church of christ") >= 0:
                church["denomination"] = "church of christ"

            elif name.find("nazarene") >= 0:
                church["denomination"] = "church of the nazarene"

            elif name.find("evangelical") >= 0:
                church["denomination"] = "evangelical"

            elif name.find("adventist") >= 0:
                church["denomination"] = "seventh-day adventist"

            elif name.find("mennonite") >= 0:
                church["denomination"] = "mennonite"

            changed = True

        return changed
