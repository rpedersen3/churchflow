from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS
import json

class UpdateRDFWithCities:

    OWL = Namespace("http://www.w3.org/2002/07/owl#")
    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
    VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
    RC = Namespace("http://richcanvas.io/ns#")
    CC = Namespace("http://churchcore.io/ns#")
    FR = Namespace("http://churchcore.io/frontrange#")
    n = URIRef("http://churchcore.io/frontrange#")

    def setupRDF(self):

        def setupRDFFile(self):
            richcanvasFilename = r"C:\RichCanvasOntology\richcanvas\richcanvas1.1.0.ttl"
            richcanvasFile = open(richcanvasFilename)

            churchcoreFilename = r"C:\RichCanvasOntology\richcanvas\churchcore.1.1.0.rdf"
            churchcoreFile = open(churchcoreFilename)

            frontRangeFile = open('frontrange_out.rdf', errors="ignore")

            g = Graph()


            g2 = Graph()
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

    def updateWithCities(self):

        g2 = self.setupRDFFile()

        # get cities
        file_path = "coloradoFrontRangeCities.json"
        with open(file_path, "r") as file:
            citiesData = json.load(file)

        # cycle through cities looking for church web sites
        cities = citiesData["cities"]
        selectedCity = None
        count = 1
        for cy in cities:

            cityName = self.clean(cy["name"])
            cityId = cityName.replace(" ", "").lower()
            city = n + cityId

            lat = cy["lat"]
            long = cy["lon"]
            population = cy["population"]
            numberOfChurches = cy["numberOfChurches"]

            g2.add((city, RDF.type, self.OWL.NamedIndividual))
            g2.add((city, RDF.type, self.RC.City))
            g2.add((city, self.RC.name, Literal(cityName)))
            g2.add((city, self.VCARD.locality, Literal(cityName)))
            g2.add((city, self.GEO.lat, Literal(lat)))
            g2.add((city, self.GEO.long, Literal(long)))
            g2.add((city, self.RC.population, Literal(population)))
            g2.add((city, self.RC.numberOfChurches, Literal(numberOfChurches)))

            raceThreshold = 4.0
            if "whitePercent" in cy and cy["whitePercent"] > raceThreshold:
                cityRaceName = cityName + " White"
                cityRaceId = cityRaceName.replace(" ", "").lower()
                cityRace = n + cityRaceId

                cityRacePercent = cy["whitePercent"]
                cityRacePopulation = round(cityRacePercent * population / 100.0)

                g2.add((cityRace, RDF.type, self.OWL.NamedIndividual))
                g2.add((cityRace, RDF.type, self.RC.CityRace))
                g2.add((cityRace, self.RC.name, Literal(cityRaceName)))
                g2.add((cityRace, self.RC.population, Literal(cityRacePopulation)))
                g2.add((cityRace, self.RC.percent, Literal(cityRacePercent)))
                g2.add((cityRace, self.RC.raceName, Literal("white")))

                g2.add((city, self.RC.cityRace, cityRace))

            if "blackPercent" in cy and cy["blackPercent"] > raceThreshold:
                cityRaceName = cityName + " Black"
                cityRaceId = cityRaceName.replace(" ", "").lower()
                cityRace = n + cityRaceId

                cityRacePercent = cy["blackPercent"]
                cityRacePopulation = round(cityRacePercent * population / 100.0)

                g2.add((cityRace, RDF.type, self.OWL.NamedIndividual))
                g2.add((cityRace, RDF.type, self.RC.CityRace))
                g2.add((cityRace, self.RC.name, Literal(cityRaceName)))
                g2.add((cityRace, self.RC.population, Literal(cityRacePopulation)))
                g2.add((cityRace, self.RC.percent, Literal(cityRacePercent)))
                g2.add((cityRace, self.RC.raceName, Literal("black")))

                g2.add((city, self.RC.cityRace, cityRace))

            if "hispanicPercent" in cy and cy["hispanicPercent"] > raceThreshold:
                cityRaceName = cityName + " Hispanic"
                cityRaceId = cityRaceName.replace(" ", "").lower()
                cityRace = self.n + cityRaceId

                cityRacePercent = cy["hispanicPercent"]
                cityRacePopulation = round(cityRacePercent * population / 100.0)

                g2.add((cityRace, RDF.type, self.OWL.NamedIndividual))
                g2.add((cityRace, RDF.type, self.RC.CityRace))
                g2.add((cityRace, self.RC.name, Literal(cityRaceName)))
                g2.add((cityRace, self.RC.population, Literal(cityRacePopulation)))
                g2.add((cityRace, self.RC.percent, Literal(cityRacePercent)))
                g2.add((cityRace, self.RC.raceName, Literal("hispanic")))

                g2.add((city, self.RC.cityRace, cityRace))

            if "asianPercent" in cy and cy["asianPercent"] > raceThreshold:
                cityRaceName = cityName + " Asian"
                cityRaceId = cityRaceName.replace(" ", "").lower()
                cityRace = n + cityRaceId

                cityRacePercent = cy["asianPercent"]
                cityRacePopulation = round(cityRacePercent * population / 100.0)

                g2.add((cityRace, RDF.type, self.OWL.NamedIndividual))
                g2.add((cityRace, RDF.type, self.RC.CityRace))
                g2.add((cityRace, self.RC.name, Literal(cityRaceName)))
                g2.add((cityRace, self.RC.population, Literal(cityRacePopulation)))
                g2.add((cityRace, self.RC.percent, Literal(cityRacePercent)))
                g2.add((cityRace, self.RC.raceName, Literal("asian")))

                g2.add((city, self.RC.cityRace, cityRace))

            print("city: ", cityName)
            print(f"Graph has {len(g2)} triples.\n")

        self.saveRDFFile(g2)