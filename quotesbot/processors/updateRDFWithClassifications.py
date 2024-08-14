from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS
from urllib.parse import urlparse
import json


class UpdateRDFWithGroupClassifications:

    OWL = Namespace("http://www.w3.org/2002/07/owl#")
    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
    VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
    RC = Namespace("http://richcanvas.io/ns#")
    CC = Namespace("http://churchcore.io/ns#")
    FR = Namespace("http://churchcore.io/frontrange#")
    n = URIRef("http://churchcore.io/frontrange#")


    '''
        specific categories

        campus:  erie, boulder, thornton
        online, oncampus
        neighborhood
    '''

    traits = [
        {
            "name": "childcare"
        },
        {
            "name": "meal"
        },
        {
            "name": "refreshments"
        },
        {
            "name": "children welcome"
        }
    ]

    classificationTypes = [
        {
            "name": "gender"
        },
        {
            "name": "race"
        },
        {
            "name": "location"
        },
        {
            "name": "age stage of life"
        },
        {
            "name": "working stage of life"
        },
        {
            "name": "married state"
        },
        {
            "name": "parenting stage of life"
        },
        {
            "name": "educational stage of life"
        },
        {
            "name": "season"
        },
        {
            "name": "school period"
        },
        {
            "name": "regularity"
        },
        {
            "name": "day of week"
        },
        {
            "name": "department"
        },
        {
            "name": "study style"
        },
        {
            "name": "ministry"
        }

    ]

    classification = [
        {
            "name": "on campus",
            "type": "location"
        },
        {
            "name": "off campus",
            "type": "location"
        },
        {
            "name": "home",
            "type": "location"
        },
        {
            "name": "online",
            "type": "location"
        },
        {
            "name": "men",
            "type": "gender",
            "tags": ["man", "mens group"]
        },
        {
            "name": "women",
            "type": "gender",
            "tags": ["womens group"]
        },
        {
            "name": "all gender",
            "type": "gender",
            "tags": ["women/men", "co-ed"]
        },
        {
            "name": "elementry school",
            "type": "educational stage of life",
        },
        {
            "name": "middle school",
            "type": "educational stage of life"
        },
        {
            "name": "high school",
            "type": "educational stage of life"
        },
        {
            "name": "pre-married",
            "type": "married state"
        },
        {
            "name": "married",
            "type": "married state"
        },
        {
            "name": "just married",
            "boarder": "married",
            "type": "married state"
        },
        {
            "name": "remarried",
            "boarder": "married",
            "type": "married state"
        },
        {
            "name": "divorced",
            "boarder": "divorced",
            "type": "married state"
        },
        {
            "name": "adult",
            "type": "age"
        },
        {
            "name": "senior",
            "type": "age"
        },
        {
            "name": "kid",
            "type": "age"
        },
        {
            "name": "young adult",
            "type": "age"
        },
        {
            "name": "teenager",
            "type": "age"
        },
        {
            "name": "young family",
            "type": "parenting stage of life"
        },
        {
            "name": "empty nesters",
            "type": "parenting stage of life"
        },
        {
            "name": "empty nesters",
            "type": "parenting stage of life"
        },
        {
            "name": "all season",
            "tags": ["all year round"],
            "type": "season"
        },
        {
            "name": "fall",
            "type": "season"
        },
        {
            "name": "winter",
            "type": "season"
        },
        {
            "name": "summer",
            "type": "season"
        },
        {
            "name": "fall",
            "type": "season"
        },
        {
            "name": "school year",
            "type": "school period"
        },
        {
            "name": "spring semester",
            "type": "school period"
        },
        {
            "name": "fall semester",
            "type": "school period"
        },
        {
            "name": "varied",
            "type": "regularity"
        },
        {
            "name": "weekly",
            "type": "regularity"
        },
        {
            "name": "monthly",
            "type": "regularity"
        },
        {
            "name": "twice monthly",
            "type": "regularity"
        },
        {
            "name": "monday",
            "type": "day of week"
        },
        {
            "name": "tuesday",
            "type": "day of week"
        },
        {
            "name": "wednesday",
            "type": "day of week"
        },
        {
            "name": "thursday",
            "type": "day of week"
        },
        {
            "name": "friday",
            "type": "day of week"
        },
        {
            "name": "saturday",
            "type": "day of week"
        },
        {
            "name": "sunday",
            "type": "day of week"
        },
        {
            "name": "all church",
            "type": "department"
        },
        {
            "name": "adult discipleship",
            "type": "department"
        },
        {
            "name": "bible",
            "type": "study style"
        },
        {
            "name": "sermon",
            "type": "study style"
        },
        {
            "name": "series",
            "type": "study style"
        },
        {
            "name": "discussion",
            "type": "study style"
        },
        {
            "name": "outreach",
            "tags": ["discipleship"],
            "type": "ministry type"
        },
        {
            "name": "growth",
            "tags": ["grow"],
            "type": "ministry type"
        },
        {
            "name": "serving",
            "type": "ministry type"
        },
        {
            "name": "support",
            "type": "ministry type"
        }
    ]

    orgClassifications = [
        {
            "name": "life groups",
            "tags": ["small groups", "base camps"],
            "type": "growth ministry"
        },
        {
            "name": "sunday school classes",
            "type": "growth ministry"
        },
        {
            "name": "fellowship group",
            "type": "growth ministry"
        },
        {
            "name": "bible studies group",
            "related": ["bible studies"],
            "type": "growth ministry"
        },
        {
            "name": "bible studies group for women",
            "broader": ["bible studies group"],
            "related": ["women"],
            "type": "growth ministry"
        },
        {
            "name": "bible studies group for men",
            "broader": ["bible studies group"],
            "related": ["men"],
            "type": "growth ministry"
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


    def updateRDFWithClassifications(self):

        g2 = self.setupRDFFile()


        for classificationTypeRec in self.classificationTypes:

            name = classificationTypeRec["name"]
            clssTypeId = "clss-" + name.replace(" ", "").lower()
            classificationType = self.n + clssTypeId

            g2.add((classificationType, RDF.type, self.OWL.NamedIndividual))
            g2.add((classificationType, RDF.type, self.RC.ClassificationType))
            g2.add((classificationType, self.RC.name, Literal(name)))

            for classification

            denominations = denCl["denominations"]
            for den in denominations:

                denName = den["name"]
                denId = denName.replace(" ", "").lower()
                denomination = self.n + denId

                tags = den["tags"]

                g2.add((denomination, RDF.type, self.OWL.NamedIndividual))
                g2.add((denomination, RDF.type, self.CC.Denomination))
                g2.add((denomination, self.RC.name, Literal(denName)))

                g2.add((denomination, self.CC.denominationClass, denominationClass))

                for tagName in tags:

                    tagId = tagName.replace(" ", "").lower() + "tag"
                    tag = self.n + tagId

                    g2.add((tag, RDF.type, self.OWL.NamedIndividual))
                    g2.add((tag, RDF.type, self.CC.DenominationTag))
                    g2.add((tag, self.RC.name, Literal(tagName)))

                    g2.add((denomination, self.CC.denominationTag, tag))
                
                

        self.saveRDFFile(g2)