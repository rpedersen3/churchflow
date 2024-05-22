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

        churchName = church["name"]
        churchId = churchName.replace(" ", "").lower()
        ch = n + churchId

        churchPlaceName = church["name"] + " Place"
        chPlaceId = n + churchPlaceName.replace(" ", "").lower()


        g2.add((chPlaceId, RDF.type, OWL.NamedIndividual))
        g2.add((chPlaceId, RDF.type, CC.ChurchPlace))
        g2.add((chPlaceId, RC.name, Literal(churchPlaceName)))

        g2.add((ch, RDF.type, OWL.NamedIndividual))
        g2.add((ch, RDF.type, CC.ReligiousOrganization))
        g2.add((ch, RC.name, Literal(churchName)))
        g2.add((ch, RC.name, chPlaceId))

        ontology.add((URIRef(subject), URIRef(property), URIRef(object)))

        print(g2.serialize(format="pretty-xml"))

        print(f"Graph has {len(g)} triples.\n")
    def initKnowledgeBase(self):

        file = open("richcanvas1.1.0.ttl")

        g = Graph()
        g.parse(file, format="ttl")

        print(f"Graph has {len(g)} triples.\n")