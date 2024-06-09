from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS
import json

class GraphConvert:
    name = "graphconvert"

    def clean(self, txt):

        import re
        pattern = re.compile(r'[^\x00-\x7F]+')
        d1 = pattern.sub('', txt)
        d2 = re.sub(r'&#\d+;', '', d1)
        d3 = d2.replace('"', '').replace(',', '').replace('#', '')
        d4 = d3.replace('\n', '').replace('\r', '').replace('\t', '')


        return d3

    def saveRDFFile(self, g2):

        #print(g2.serialize(format="pretty-xml"))
        data = g2.serialize(format="pretty-xml")

        with open('frontrange_out.rdf', "w", encoding="utf-8") as f:
            f.write(data)

    def setupRDFFile(self):

        richcanvasFilename = r"C:\RichCanvasOntology\richcanvas\richcanvas1.1.0.ttl"
        richcanvasFile = open(richcanvasFilename)

        churchcoreFilename = r"C:\RichCanvasOntology\richcanvas\churchcore.1.1.0.rdf"
        churchcoreFile = open(churchcoreFilename)

        frontRangeFile = open('frontrange_out.rdf', errors="ignore")

        g = Graph()
        # g.parse(richcanvasFile, format="ttl")
        # g.parse(frontRangeFile, format="xml")

        g2 = Graph()
        g2.parse(frontRangeFile, format="xml")

        OWL = Namespace("http://www.w3.org/2002/07/owl#")
        g2.bind("owl", OWL)

        FOAF = Namespace("http://xmlns.com/foaf/0.1/")
        g2.bind("foaf", FOAF)

        GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
        g2.bind("geo", GEO)

        VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
        g2.bind("vcard", VCARD)

        RC = Namespace("http://richcanvas.io/ns#")
        g2.bind("rc", RC)

        CC = Namespace("http://churchcore.io/ns#")
        g2.bind("cc", CC)

        FR = Namespace("http://churchcore.io/frontrange#")
        g2.bind("fr", FR)

        n = URIRef("http://churchcore.io/frontrange#")

        glooOrgName = "gloo"
        glooOrgId = glooOrgName.replace(" ", "").lower()
        glooOrg = n + glooOrgId

        g2.add((glooOrg, RDF.type, OWL.NamedIndividual))
        g2.add((glooOrg, RDF.type, CC.MinistryOrganization))
        g2.add((glooOrg, RC.name, Literal(glooOrgName)))

        squarespaceBusinessSystemName = "squarespace"
        squarespaceBusinessSystemId = squarespaceBusinessSystemName.replace(" ", "").lower()
        squarespaceBusinessSystem = n + squarespaceBusinessSystemId

        g2.add((squarespaceBusinessSystem, RDF.type, OWL.NamedIndividual))
        g2.add((squarespaceBusinessSystem, RDF.type, RC.BusinessSystem))
        g2.add((squarespaceBusinessSystem, RC.name, Literal(squarespaceBusinessSystemName)))

        churchCenterBusinessSystemName = "churchcenter"
        churchCenterBusinessSystemId = churchCenterBusinessSystemName.replace(" ", "").lower()
        churchCenterBusinessSystem = n + churchCenterBusinessSystemId

        g2.add((churchCenterBusinessSystem, RDF.type, OWL.NamedIndividual))
        g2.add((churchCenterBusinessSystem, RDF.type, RC.ChurchManagementSystem))
        g2.add((churchCenterBusinessSystem, RC.name, Literal(churchCenterBusinessSystemName)))

        return g2

    def addCities(self, g2):

        n = URIRef("http://churchcore.io/frontrange#")
        OWL = Namespace("http://www.w3.org/2002/07/owl#")
        FOAF = Namespace("http://xmlns.com/foaf/0.1/")
        GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
        VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
        RC = Namespace("http://richcanvas.io/ns#")
        CC = Namespace("http://churchcore.io/ns#")
        FR = Namespace("http://churchcore.io/frontrange#")


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

            g2.add((city, RDF.type, OWL.NamedIndividual))
            g2.add((city, RDF.type, RC.City))
            g2.add((city, RC.name, Literal(cityName)))
            g2.add((city, VCARD.locality, Literal(cityName)))
            g2.add((city, GEO.lat, Literal(lat)))
            g2.add((city, GEO.long, Literal(long)))
            g2.add((city, RC.population, Literal(population)))
            g2.add((city, RC.numberOfChurches, Literal(numberOfChurches)))

            raceThreshold = 4.0
            if "whitePercent" in cy and cy["whitePercent"] > raceThreshold:

                cityRaceName = cityName + " White"
                cityRaceId = cityRaceName.replace(" ", "").lower()
                cityRace = n + cityRaceId

                cityRacePercent = cy["whitePercent"]
                cityRacePopulation = round(cityRacePercent * population / 100.0)

                g2.add((cityRace, RDF.type, OWL.NamedIndividual))
                g2.add((cityRace, RDF.type, RC.CityRace))
                g2.add((cityRace, RC.name, Literal(cityRaceName)))
                g2.add((cityRace, RC.population, Literal(cityRacePopulation)))
                g2.add((cityRace, RC.percent, Literal(cityRacePercent)))
                g2.add((cityRace, RC.raceName, Literal("white")))

                g2.add((city, RC.cityRace, cityRace))

            if "blackPercent" in cy and cy["blackPercent"] > raceThreshold:

                cityRaceName = cityName + " Black"
                cityRaceId = cityRaceName.replace(" ", "").lower()
                cityRace = n + cityRaceId

                cityRacePercent = cy["blackPercent"]
                cityRacePopulation = round(cityRacePercent * population / 100.0)

                g2.add((cityRace, RDF.type, OWL.NamedIndividual))
                g2.add((cityRace, RDF.type, RC.CityRace))
                g2.add((cityRace, RC.name, Literal(cityRaceName)))
                g2.add((cityRace, RC.population, Literal(cityRacePopulation)))
                g2.add((cityRace, RC.percent, Literal(cityRacePercent)))
                g2.add((cityRace, RC.raceName, Literal("black")))

                g2.add((city, RC.cityRace, cityRace))

            if "hispanicPercent" in cy and cy["hispanicPercent"] > raceThreshold:

                cityRaceName = cityName + " Hispanic"
                cityRaceId = cityRaceName.replace(" ", "").lower()
                cityRace = n + cityRaceId

                cityRacePercent = cy["hispanicPercent"]
                cityRacePopulation = round(cityRacePercent * population / 100.0)

                g2.add((cityRace, RDF.type, OWL.NamedIndividual))
                g2.add((cityRace, RDF.type, RC.CityRace))
                g2.add((cityRace, RC.name, Literal(cityRaceName)))
                g2.add((cityRace, RC.population, Literal(cityRacePopulation)))
                g2.add((cityRace, RC.percent, Literal(cityRacePercent)))
                g2.add((cityRace, RC.raceName, Literal("hispanic")))

                g2.add((city, RC.cityRace, cityRace))

            if "asianPercent" in cy and cy["asianPercent"] > raceThreshold:

                cityRaceName = cityName + " Asian"
                cityRaceId = cityRaceName.replace(" ", "").lower()
                cityRace = n + cityRaceId

                cityRacePercent = cy["asianPercent"]
                cityRacePopulation = round(cityRacePercent * population / 100.0)

                g2.add((cityRace, RDF.type, OWL.NamedIndividual))
                g2.add((cityRace, RDF.type, RC.CityRace))
                g2.add((cityRace, RC.name, Literal(cityRaceName)))
                g2.add((cityRace, RC.population, Literal(cityRacePopulation)))
                g2.add((cityRace, RC.percent, Literal(cityRacePercent)))
                g2.add((cityRace, RC.raceName, Literal("asian")))

                g2.add((city, RC.cityRace, cityRace))

            print("city: ", cityName)
            print(f"Graph has {len(g2)} triples.\n")

    def addChurch(self, church, g2):

        if "name" not in church:
            return

        n = URIRef("http://churchcore.io/frontrange#")
        OWL = Namespace("http://www.w3.org/2002/07/owl#")
        FOAF = Namespace("http://xmlns.com/foaf/0.1/")
        GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
        VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
        RC = Namespace("http://richcanvas.io/ns#")
        CC = Namespace("http://churchcore.io/ns#")
        FR = Namespace("http://churchcore.io/frontrange#")

        glooOrgName = "gloo"
        glooOrgId = glooOrgName.replace(" ", "").lower()
        glooOrg = n + glooOrgId

        squarespaceBusinessSystemName = "squarespace"
        squarespaceBusinessSystemId = squarespaceBusinessSystemName.replace(" ", "").lower()
        squarespaceBusinessSystem = n + squarespaceBusinessSystemId

        churchCenterBusinessSystemName = "churchcenter"
        churchCenterBusinessSystemId = churchCenterBusinessSystemName.replace(" ", "").lower()
        churchCenterBusinessSystem = n + churchCenterBusinessSystemId

        if "name" in church and "latitude" in church and "longitude" in church:

            churchOrgName = self.clean(church["name"])
            query = """select ?churchName where { ?churchName rc:name ?name .
                                        FILTER(LCASE(?name) = \"""" + churchOrgName.lower() + """\") }
                                        """
            results = g2.query(query)
            if len(results) == 0:

                print("***************** parse church: ", churchOrgName)

                churchOrgId = churchOrgName.replace(" ", "").lower()
                chOrg = n + churchOrgId

                churchSiteName = self.clean(church["name"]) + " Site"
                churchSiteId = churchSiteName.replace(" ", "").lower()
                chSite = n + churchSiteId

                g2.add((chSite, RDF.type, OWL.NamedIndividual))
                g2.add((chSite, RDF.type, CC.ChurchSite))
                g2.add((chSite, RC.name, Literal(churchSiteName)))

                if "latitude" in church and "longitude" in church:
                    chSiteLat = church["latitude"]
                    chSiteLong = church["longitude"]
                    g2.add((chSite, GEO.lat, Literal(chSiteLat)))
                    g2.add((chSite, GEO.long, Literal(chSiteLong)))


                if "addressInfo" in church:
                    if "city" in church["addressInfo"] and "county" in church["addressInfo"] and "zipcode" in church["addressInfo"]:

                        print(".. add site address ..")

                        churchSiteAddressName = self.clean(church["name"]) + " Site Address"
                        churchSiteAddressId = churchSiteAddressName.replace(" ", "").lower()
                        chSiteAddress = n + churchSiteAddressId

                        g2.add((chSiteAddress, RDF.type, OWL.NamedIndividual))
                        g2.add((chSiteAddress, RDF.type, RC.PostalAddress))
                        g2.add((chSiteAddress, RC.name, Literal(churchSiteAddressName)))

                        chSiteCity = church["addressInfo"]["city"]
                        chSiteCounty = church["addressInfo"]["county"]
                        chSiteZipcode = church["addressInfo"]["zipcode"]
                        g2.add((chSiteAddress, VCARD.locality, Literal(chSiteCity)))
                        g2.add((chSiteAddress, VCARD.region, Literal(chSiteCounty)))
                        g2.add((chSiteAddress, VCARD.postalCode, Literal(chSiteZipcode)))

                        if "latitude" in church and "longitude" in church:
                            chSiteAddressLat = church["latitude"]
                            chSiteAddressLong = church["longitude"]
                            g2.add((chSiteAddress, VCARD.latitude, Literal(chSiteAddressLat)))
                            g2.add((chSiteAddress, VCARD.longitude, Literal(chSiteAddressLong)))

                        g2.add((chSite, RC.hasSiteAddress, chSiteAddress))

                        # link church to city
                        query = """select ?city ?name where { ?city rdf:type rc:City .  ?city rc:name ?name . 
                                                            FILTER(?name = \"""" + chSiteCity + """\") }
                                                            """
                        results = g2.query(query)

                        print(".......... query for city: ", query)
                        if len(results) > 0:
                            for row in results:
                                print("row: ", row["city"])
                                g2.add((chSite, RC.city, row["city"]))


                g2.add((chOrg, RDF.type, OWL.NamedIndividual))
                g2.add((chOrg, RDF.type, CC.ChurchOrganization))
                g2.add((chOrg, RC.name, Literal(churchOrgName)))
                g2.add((chOrg, RC.hasSite, chSite))

                if "chmss" in church:
                    for chms in church["chmss"]:
                        if chms["type"] == "gloo":
                            # add gloo as a ministry partner
                            g2.add((chOrg, RC.isPartnerOf, glooOrg))

                        if chms["type"] == "squarespace":
                            # add business system
                            g2.add((chOrg, RC.hasBusinessSystem, squarespaceBusinessSystem))

                        if chms["type"] == "churchcenter":
                            # add business system
                            g2.add((chOrg, RC.hasChurchManagementSystem, churchCenterBusinessSystem))

                if "leadPastor" in church:
                    leadPastor = church["leadPastor"]
                    if "name" in leadPastor:
                        name = self.clean(leadPastor["name"])

                        personName = name
                        personId = personName.replace(" ", "").lower()
                        person = n + personId

                        g2.add((person, RDF.type, OWL.NamedIndividual))
                        g2.add((person, RDF.type, RC.Person))
                        g2.add((person, RC.name, Literal(personName)))

                        g2.add((chOrg, RC.hasMember, person))


                        postName = churchOrgName + " Lead Pastor"
                        postId = postName.replace(" ", "").lower()
                        post = n + postId

                        g2.add((post, RDF.type, OWL.NamedIndividual))
                        g2.add((post, RDF.type, RC.Post))
                        g2.add((post, RC.name, Literal(postName)))
                        g2.add((post, RC.heldBy, person))

                        g2.add((chOrg, RC.hasPost, post))

                '''
                if "contacts" in church:
                    contacts = church["contacts"]
                    for contact in contacts:
                        if "name" in contact:
        
                            name = self.clean(contact["name"])
        
                            query = """select ?person where { ?person rc:name ?name . 
                                    FILTER(?name = \"""" + name + """\") }
                                    """
                            results = g2.query(query)
        
                            if len(results) == 0:
                                personName = name
                                personId = personName.replace(" ", "").lower()
                                person = n + personId
        
                                g2.add((person, RDF.type, OWL.NamedIndividual))
                                g2.add((person, RDF.type, RC.Person))
                                g2.add((person, RC.name, Literal(personName)))
        
                                g2.add((chOrg, RC.hasMember, person))
                            else:
                                print("person already in knowledge base: ", name)
        
        
                print(g2.serialize(format="pretty-xml"))
                data = g2.serialize(format="pretty-xml")
        
                with open('frontrange_out.rdf', "w", encoding="utf-8") as f:
                    f.write(data)
        
                '''

        print(f"Graph has {len(g2)} triples.\n")

    def initKnowledgeBase(self):

        file = open("richcanvas1.1.0.ttl")

        g = Graph()
        g.parse(file, format="ttl")

        print(f"Graph has {len(g)} triples.\n")