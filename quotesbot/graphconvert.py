from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS

class GraphConvert:
    name = "graphconvert"

    def addChurch(self, church):

        if "name" not in church:
            return

        file = open("richcanvas1.1.0.ttl")

        g = Graph()
        g.parse(file, format="ttl")









        g2 = Graph()

        OWL = Namespace("http://www.w3.org/2002/07/owl#")
        g2.bind("owl", OWL)

        FOAF = Namespace("http://xmlns.com/foaf/0.1/")
        g2.bind("foaf", FOAF)

        RC = Namespace("http://richcanvas.io/ns#")
        g2.bind("rc", RC)

        FR = Namespace("http://churchcore.io/frontrange#")
        g2.bind("fr", FR)


        n = URIRef("http://churchcore.io/frontrange#")

        churchName = church["name"]
        churchId = churchName.replace(" ", "").lower()
        ch = n + churchId


        # individual church assertion
        g2.add((ch, RDF.type, OWL.NamedIndividual))
        g2.add((ch, RDF.type, RC.Organization))
        g2.add((ch, RC.name, Literal(churchName)))

        print(g2.serialize(format="pretty-xml"))

        #print(f"Graph has {len(g)} triples.\n")
    def initKnowledgeBase(self):

        file = open("richcanvas1.1.0.ttl")

        g = Graph()
        g.parse(file, format="ttl")

        print(f"Graph has {len(g)} triples.\n")