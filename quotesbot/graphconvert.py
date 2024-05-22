from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS

class GraphConvert:
    name = "graphconvert"

    def addChurch(self, church):

        if "name" not in church:
            return

        richcanvasFilename = r"C:\RichCanvasOntology\richcanvas\richcanvas1.1.0.ttl"
        richcanvasFile = open(richcanvasFilename)

        churchcoreFilename = r"C:\RichCanvasOntology\richcanvas\churchcore.1.1.0.rdf"
        churchcoreFile = open(churchcoreFilename)

        g = Graph()
        #g.parse(richcanvasFile, format="ttl")
        g.parse(churchcoreFile, format="xml")








        g2 = Graph()

        OWL = Namespace("http://www.w3.org/2002/07/owl#")
        g2.bind("owl", OWL)

        FOAF = Namespace("http://xmlns.com/foaf/0.1/")
        g2.bind("foaf", FOAF)

        RC = Namespace("http://richcanvas.io/ns#")
        g2.bind("rc", RC)

        CC = Namespace("http:/churchcore.io/ns#")
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


        churchOrgName = church["name"]
        churchOrgId = churchOrgName.replace(" ", "").lower()
        chOrg = n + churchOrgId

        churchSiteName = church["name"] + " Site"
        churchSiteId = n + churchSiteName.replace(" ", "").lower()
        chSite = n + churchSiteId


        g2.add((chSite, RDF.type, OWL.NamedIndividual))
        g2.add((chSite, RDF.type, CC.ChurchSite))
        g2.add((chSite, RC.name, Literal(churchSiteName)))

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
                name = leadPastor["name"]

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

        if "contacts" in church:
            contacts = church["contacts"]
            for contact in contacts:
                if "name" in contact:
                    
                    name = contact["name"]

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

        print(f"Graph has {len(g2)} triples.\n")
    def initKnowledgeBase(self):

        file = open("richcanvas1.1.0.ttl")

        g = Graph()
        g.parse(file, format="ttl")

        print(f"Graph has {len(g)} triples.\n")