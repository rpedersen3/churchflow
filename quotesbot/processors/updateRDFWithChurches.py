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

    churches_file_path = "churches.json"
    with open(churches_file_path, "r") as file:
        churchesData = json.load(file)
    churches = churchesData["churches"]

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



            glooOrgName = "gloo"
            glooOrgId = glooOrgName.replace(" ", "").lower()
            glooOrg = n + glooOrgId

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
            churchCenterBusinessSystem = n + churchCenterBusinessSystemId

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

    def updateWithChurches(self):

        g2 = self.setupRDFFile()


        for church in self.churches:

            if "name" not in church:
                return

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
                churchOrgId = churchOrgName.replace(" ", "").lower()
                chOrg = self.n + churchOrgId
                query = """select ?church where { ?church rc:name ?churchName .
                                            FILTER(?church = <""" + str(chOrg) + """>) }
                                            """

                results = g2.query(query)

                if len(results) == 0:

                    g2.add((chOrg, RDF.type, self.OWL.NamedIndividual))
                    g2.add((chOrg, RDF.type, self.CC.ChurchOrganization))
                    g2.add((chOrg, self.RC.name, Literal(churchOrgName)))

                    if "org" in church:
                        orgName = church["org"]

                        orgChurchOrgName = self.clean(orgName)
                        orgChurchOrgId = orgChurchOrgName.replace(" ", "").lower()
                        orgChOrg = n + orgChurchOrgId

                        g2.add((orgChOrg, RDF.type, self.OWL.NamedIndividual))
                        g2.add((orgChOrg, RDF.type, self.CC.ChurchOrganization))
                        g2.add((orgChOrg, self.RC.name, Literal(orgChurchOrgName)))

                        g2.add((orgChOrg, self.RC.hasSubOrganization, chOrg))

                    churchSiteName = self.clean(church["name"]) + " Site"
                    churchSiteId = churchSiteName.replace(" ", "").lower()
                    chSite = n + churchSiteId

                    g2.add((chSite, RDF.type, self.OWL.NamedIndividual))
                    g2.add((chSite, RDF.type, self.CC.ChurchSite))
                    g2.add((chSite, self.RC.name, Literal(churchSiteName)))
                    g2.add((chOrg, self.RC.hasSite, chSite))

                    if "latitude" in church and "longitude" in church:
                        chSiteLat = church["latitude"]
                        chSiteLong = church["longitude"]
                        g2.add((chSite, self.GEO.lat, Literal(chSiteLat)))
                        g2.add((chSite, self.GEO.long, Literal(chSiteLong)))

                    if "addressInfo" in church:
                        if "city" in church["addressInfo"] and "county" in church["addressInfo"] and "zipcode" in \
                                church["addressInfo"]:

                            print(".. add site address ..")

                            churchSiteAddressName = self.clean(church["name"]) + " Site Address"
                            churchSiteAddressId = churchSiteAddressName.replace(" ", "").lower()
                            chSiteAddress = n + churchSiteAddressId

                            g2.add((chSiteAddress, RDF.type, self.OWL.NamedIndividual))
                            g2.add((chSiteAddress, RDF.type, self.RC.PostalAddress))
                            g2.add((chSiteAddress, self.RC.name, Literal(churchSiteAddressName)))

                            chSiteCity = church["addressInfo"]["city"]
                            chSiteCounty = church["addressInfo"]["county"]
                            chSiteZipcode = church["addressInfo"]["zipcode"]
                            g2.add((chSiteAddress, self.VCARD.locality, Literal(chSiteCity)))
                            g2.add((chSiteAddress, self.VCARD.region, Literal(chSiteCounty)))
                            g2.add((chSiteAddress, self.VCARD.postalCode, Literal(chSiteZipcode)))

                            if "latitude" in church and "longitude" in church:
                                chSiteAddressLat = church["latitude"]
                                chSiteAddressLong = church["longitude"]
                                g2.add((chSiteAddress, self.VCARD.latitude, Literal(chSiteAddressLat)))
                                g2.add((chSiteAddress, self.VCARD.longitude, Literal(chSiteAddressLong)))

                            g2.add((chSite, self.RC.hasSiteAddress, chSiteAddress))

                            # link church to city
                            query = """select ?city ?name where { ?city rdf:type rc:City .  ?city rc:name ?name . 
                                                                FILTER(?name = \"""" + chSiteCity + """\") }
                                                                """
                            results = g2.query(query)

                            print(".......... query for city: ", query)
                            if len(results) > 0:
                                for row in results:
                                    print("row: ", row["city"])
                                    g2.add((chSite, self.RC.city, row["city"]))

                    if "chmss" in church:
                        for chms in church["chmss"]:
                            if chms["type"] == "gloo":
                                # add gloo as a ministry partner
                                g2.add((chOrg, self.RC.isPartnerOf, glooOrg))

                            if chms["type"] == "squarespace":
                                # add business system
                                g2.add((chOrg, self.RC.hasBusinessSystem, squarespaceBusinessSystem))

                            if chms["type"] == "churchcenter":
                                # add business system
                                g2.add((chOrg, self.RC.hasChurchManagementSystem, churchCenterBusinessSystem))

                    if "leadPastor" in church:
                        leadPastor = church["leadPastor"]
                        if "name" in leadPastor:
                            name = self.clean(leadPastor["name"])

                            personName = name
                            personId = personName.replace(" ", "").lower()
                            person = n + personId

                            g2.add((person, RDF.type, self.OWL.NamedIndividual))
                            g2.add((person, RDF.type, self.RC.Person))
                            g2.add((person, self.RC.name, Literal(personName)))

                            g2.add((chOrg, self.RC.hasMember, person))

                            postName = churchOrgName + " Lead Pastor"
                            postId = postName.replace(" ", "").lower()
                            post = n + postId

                            g2.add((post, RDF.type, self.OWL.NamedIndividual))
                            g2.add((post, RDF.type, self.RC.Post))
                            g2.add((post, self.RC.name, Literal(postName)))
                            g2.add((post, self.RC.heldBy, person))

                            g2.add((chOrg, self.RC.hasPost, post))

                    if "websiteUri" in church:
                        websiteUri = church["websiteUri"];
                        websiteId = self.clean(websiteUri.replace(" ", "").lower())
                        website = self.n + websiteId

                        g2.add((website, RDF.type, self.OWL.NamedIndividual))
                        g2.add((website, self.RC.type, self.RC.Website))
                        g2.add((website, self.RC.uri, Literal(websiteUri)))

                        g2.add((chOrg, self.RC.hasWebsite, website))

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
                                    person = self.n + personId

                                    g2.add((person, RDF.type, self.OWL.NamedIndividual))
                                    g2.add((person, RDF.type, self.RC.Person))
                                    g2.add((person, self.RC.name, Literal(personName)))

                                    g2.add((chOrg, self.RC.hasMember, person))
                                else:
                                    print("person already in knowledge base: ", name)


                    print(g2.serialize(format="pretty-xml"))
                    data = g2.serialize(format="pretty-xml")

                    with open('frontrange_out.rdf', "w", encoding="utf-8") as f:
                        f.write(data)

                    '''

            print(f"Graph has {len(g2)} triples.\n")

        self.saveRDFFile(g2)