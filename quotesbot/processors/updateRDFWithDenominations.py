from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS
from urllib.parse import urlparse
import json


class UpdateRDFWithDenominations:

    OWL = Namespace("http://www.w3.org/2002/07/owl#")
    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
    VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
    RC = Namespace("http://richcanvas.io/ns#")
    CC = Namespace("http://churchcore.io/ns#")
    FR = Namespace("http://churchcore.io/frontrange#")
    n = URIRef("http://churchcore.io/frontrange#")


    denominationClasses = [
        {
            "name": "Roman Catholicism",
            "denominations": [
                {
                    "name": "Roman Catholic Church",
                    "description": "",
                    "tags": ["roman_catholic", "catholic"]
                }
            ]
        },
        {
            "name": "Eastern Catholic Churches",
            "denominations": [
                {
                    "name": "Byzantine Rite",
                    "description": "e.g., Ukrainian Greek Catholic Church",
                    "tags": ["greek_catholic"]
                },
                {
                    "name": "Alexandrian Rite",
                    "description": "e.g., Coptic Catholic Church",
                    "tags": []
                },
                {
                    "name": "Armenian Rite",
                    "description": "e.g., Armenian Catholic Church",
                    "tags": []
                },
                {
                    "name": "Syriac Rite",
                    "description": "e.g., Maronite Church, Syro-Malabar Church",
                    "tags": ["maronite"]
                }
            ]
        },
        {
            "name": "Eastern Orthodoxy",
            "denominations": [
                {
                    "name": "Eastern Orthodox Church",
                    "description": "includes national churches like the Greek Orthodox Church, Russian Orthodox Church, etc.",
                    "tags": ["orthodox",
                                "orthodox christian",
                                "greek_orthodox",
                                "greek orthodox",
                                "romanian orthodox"]
                },
                {
                    "name": "Oriental Orthodox Churches",
                    "description": "includes the Armenian Apostolic Church, Coptic Orthodox Church, etc.",
                    "tags": ["coptic_orthodox",
                                "ethiopian_orthodox",
                                "apostolic"]
                }
            ]
        },
        {
            "name": "Protestantism",
            "denominations": [
                {
                    "name": "Lutheranism ",
                    "description": "e.g., Evangelical Lutheran Church in America, Lutheran Church–Missouri Synod",
                    "tags": ["lutheran",
                                "lutheran (lcms)",
                                "lutheran (wels)",
                                "wesleyan",
                                "lutheran (lcmc)"]
                },
                {
                    "name": "Anglicanism",
                    "description": "e.g., Church of England, Episcopal Church in the USA",
                    "tags": ["episcopal",
                                "african methodist episcopal"]
                },
                {
                    "name": "Reformed/Calvinism",
                    "description": "e.g., Presbyterian Church, United Church of Christ",
                    "tags": ["presbyterian",
                                "reformed",
                                "reformed (rca)",
                                "presbyterian (pcusa)",
                                "church of christ",
                                "christian reformed church",
                                "church_of_christ",
                                "presbyterian (pca)",
                                "united church of christ",
                                "orthodox_presbyterian_church"]
                },
                {
                    "name": "Methodism",
                    "description": "e.g., United Methodist Church, African Methodist Episcopal Church",
                    "tags": ["methodist",
                                "united_methodist"
                                "united methodist church",
                                "african_methodist_episcopal",
                                "christian methodist episcopal church"]
                },
                {
                    "name": "Baptists",
                    "description": "e.g., Southern Baptist Convention, American Baptist Churches USA",
                    "tags": ["baptist",
                                "southern baptist convention",
                                "american baptist churches usa",
                                "independent baptist",
                                "general association of regular baptist churches",
                                "missionary_baptist",
                                "converge worldwide"]
                },
                {
                    "name": "Pentecostalism",
                    "description": "e.g., Assemblies of God, Church of God in Christ",
                    "tags": ["pentecostal",
                                "assemblies of god",
                                "assemblies_of_god",
                                "church of god",
                                "church of god in christ",
                                "church_of_god_in_christ",
                                "united pentecostal church international",
                                "pentecostal church of god"]
                },
                {
                    "name": "Adventism",
                    "description": "e.g., Seventh-day Adventist Church",
                    "tags": ["seventh-day adventist",
                                "seventh_day_adventist_reformed",
                                "seventh_day_adventist"]
                },
                {
                    "name": "Anabaptism",
                    "description": "e.g., Mennonite Church, Amish",
                    "tags": ["mennonite",
                                "mennonite (mcusa)"]
                },
                {
                    "name": "Restorationism",
                    "description": "e.g., Churches of Christ, Christian Church (Disciples of Christ)",
                    "tags": ["disciples of christ"]
                },
                {
                    "name": "Berean Bible Churches",
                    "description": "",
                    "tags": ["berean fellowship"]
                },
                {
                    "name": "Christian and Missionary Alliance",
                    "description": "",
                    "tags": ["christian and missionary alliance"]
                },
                {
                    "name": "Metropolitan Community Church",
                    "description": "",
                    "tags": ["metropolitan community church"]
                }
            ]
        },
        {
            "name": "Nontrinitarian Movement",
            "denominations": [
                {
                    "name": "Jehovah's Witnesses",
                    "description": "",
                    "tags": ["jehovahs_witness"]
                },
                {
                    "name": "The Church of Jesus Christ of Latter-day Saints (LDS/Mormons)",
                    "description": "",
                    "tags": ["mormon", "latter-day_saints"]
                },
                {
                    "name": "Unitarian Universalism",
                    "description": "historically Christian, now multi-religious",
                    "tags": ["unitarian"]
                }
            ]
        },
        {
            "name": "Independent and Non-Denominational Churches",
            "denominations": [
                {
                    "name": "Non-Denominational Christianity",
                    "description": "churches that do not formally align with any specific denomination",
                    "tags": ["nondenominational", "non-denominational", "interdenominational"]
                }
            ]
        },
        {
            "name": "African Initiated Churches",
            "denominations": [
                {
                    "name": "Zion Christian Church",
                    "description": "",
                    "tags": []
                },
                {
                    "name": "Kimbanguist Church",
                    "description": "",
                    "tags": []
                }
            ]
        },
        {
            "name": "Charismatic Movement",
            "denominations": [
                {
                    "name": "Charismatic Renewal",
                    "description": "within Catholicism, Anglicanism, and mainline Protestantism",
                    "tags": ["anglican"]
                }
            ]
        },
        {
            "name": "Evangelicalism",
            "denominations": [
                {
                    "name": "Various Evangelical Churches and Movements",
                    "description": "often cross-denominational",
                    "tags": ["evangelical",
                                "evangelical free church of america"]
                }
            ]
        },
        {
            "name": "Other Traditions and Denominations",
            "denominations": [
                {
                    "name": "Quakers ",
                    "description": "",
                    "tags": ["quaker"]
                },
                {
                    "name": "Church of the Nazarene ",
                    "description": "",
                    "tags": ["church of the nazarene"]
                }
            ]
        },
        {
            "name": "New Religious Movements",
            "denominations": [
                {
                    "name": "Christian Science ",
                    "description": "",
                    "tags": ["christ_scientist"]
                }
            ]
        },
        {
            "name": "Unity",
            "denominations": [
                {
                    "name": "Unity",
                    "description": "",
                    "tags": ["unity"]
                }
            ]
        },
        {
            "name": "Unknown",
            "denominations": [
                {
                    "name": "Unknown",
                    "description": "",
                    "tags": ["unknown"]
                }
            ]
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


    def updateRDFWithDenominations(self):

        g2 = self.setupRDFFile()


        for denCl in self.denominationClasses:

            name = denCl["name"]
            denClId = name.replace(" ", "").lower()
            denominationClass = self.n + denClId

            g2.add((denominationClass, RDF.type, self.OWL.NamedIndividual))
            g2.add((denominationClass, RDF.type, self.CC.DenominationClass))
            g2.add((denominationClass, self.RC.name, Literal(name)))

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