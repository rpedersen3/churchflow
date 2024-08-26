from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS
from urllib.parse import urlparse

import json
import random
import string

class UpdateRDFWithMultiCampusChurches:

    OWL = Namespace("http://www.w3.org/2002/07/owl#")
    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
    VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
    RC = Namespace("http://richcanvas.io/ns#")
    CC = Namespace("http://churchcore.io/ns#")
    FR = Namespace("http://churchcore.io/frontrange#")
    n = URIRef("http://churchcore.io/frontrange#")

    churches_file_path = "multiCampusChurches.json"
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

    def clean(self, txt):

        import re
        pattern = re.compile(r'[^\x00-\x7F]+')
        d1 = pattern.sub('', txt)
        d2 = re.sub(r'&#\d+;', '', d1)
        d3 = d2.replace('"', '').replace(',', '').replace('#', '')
        d4 = d3.replace('\n', '').replace('\r', '').replace('\t', '')


        return d3

    def generate_random_string(self):

        length = 12

        # Define the characters to choose from: lowercase, uppercase, digits, hyphens, underscores, and periods
        characters = string.ascii_letters + string.digits + '-_.'
        # Generate a random ID by selecting random characters from the character set
        random_id = ''.join(random.choice(characters) for _ in range(length))
        return random_id

    def convertToNumber(self, s):
        s = s.lower()
        s = s.replace(",", "")  # Remove commas

        try:
            if 'k' in s:
                return int(float(s.replace("k", "")) * 1_000)
            elif 'm' in s:
                return int(float(s.replace("m", "")) * 1_000_000)
            else:
                return int(s)
        except:
            #print("problem converting: ", s)
            return 0

    def updateWithMultiCampusChurches(self):

        g2 = self.setupRDFFile()

        for church in self.churches:

            if "name" in church:

                if "uniqueId" in church:

                    churchOrgName = self.clean(church["name"])
                    churchOrgId = church["uniqueId"]
                    chOrg = self.n + churchOrgId

                    g2.add((chOrg, RDF.type, self.OWL.NamedIndividual))
                    g2.add((chOrg, RDF.type, self.CC.ChurchOrganization))
                    g2.add((chOrg, self.RC.name, Literal(churchOrgName)))


                    # update church with denomination
                    denomination = "unknown"
                    if "denomination" in church and church["denomination"] != "unknown":
                        denomination = church["denomination"]
                        if denomination == "edit denomination":
                            denomination = "unknown"

                    # link church to denomination
                    query = """select ?denomination where { 
                                    ?denomination rdf:type cc:Denomination . 
                                    ?denomination rc:hasTag ?tag . 
                                    ?tag rc:name ?tagName . 
                                    FILTER(STRSTARTS(LCASE( \"""" + denomination + """\"), LCASE(?tagName))) }
                                    """

                    try:
                        results = g2.query(query)

                        if len(results) > 0:
                            for row in results:
                                g2.add((chOrg, self.CC.denomination, row["denomination"]))
                                #g2.add((chOrg, self.RC.Tag, row["tag"]))
                                break
                        #else:
                            #g2.add((chOrg, self.CC.denomination, "unknown"))
                            #g2.add((chOrg, self.RC.Tag, '<rc:Tag rdf:resource="http://churchcore.io/frontrange#unknowntag"/>'))

                    except Exception as e:
                        print("get denomination err 1: ", e)



                    # link church to network
                    if "network" in church and church["network"] != "unknown":
                        networks = church["network"]

                        networkList = networks.split(',')
                        for network in networkList:
                            #print("************ find network: ", network)
                            query = """select ?network ?tag where { 
                                            ?network rdf:type cc:Network .  
                                            ?network rc:hasTag ?tag . 
                                            ?tag rc:name ?tagName . 
                                            FILTER(STRSTARTS(LCASE( \"""" + network + """\"), LCASE(?tagName))) }
                                            """

                            try:
                                results = g2.query(query)

                                if len(results) > 0:
                                    #print("****** found network **********", results)
                                    for row in results:

                                        #print("***************  add network to org ***********")
                                        g2.add((chOrg, self.CC.network, row["network"]))
                                        #g2.add((chOrg, self.CC.networkTag, row["tag"]))
                                        break

                            except Exception as e:
                                print("get network err: ", e)



                    # church social networks
                    if "social" in church:
                        social = church["social"]


                        if "facebook" in social:

                            facebook = self.n + "facebook"

                            orgSocialNetworkName = self.clean(churchOrgName) + " facebook"
                            orgSocialNetworkId = self.generate_random_string()
                            orgSocialNetwork = self.n + orgSocialNetworkId

                            g2.add((orgSocialNetwork, RDF.type, self.OWL.NamedIndividual))
                            g2.add((orgSocialNetwork, RDF.type, self.RC.OrgSocialNetwork))
                            g2.add((orgSocialNetwork, self.RC.socialNetwork, facebook))
                            g2.add((orgSocialNetwork, self.RC.name, Literal(orgSocialNetworkName)))

                            g2.add((chOrg, self.RC.orgSocialNetwork, orgSocialNetwork))


                            if "url" in social["facebook"]:
                                g2.add((orgSocialNetwork, self.RC.uri, Literal(social["facebook"]["url"])))
                            elif "facebookUrl" in social:
                                g2.add((orgSocialNetwork, self.RC.uri, Literal(social["facebookUrl"])))

                            if "followers" in social["facebook"]:
                                followers = self.convertToNumber(social["facebook"]["followers"].replace("followers", "").strip())
                                g2.add((orgSocialNetwork, self.RC.socialFollowers, Literal(followers)))
                            if "likes" in social["facebook"]:
                                likes = self.convertToNumber(social["facebook"]["likes"].replace("likes", "").strip())
                                g2.add((orgSocialNetwork, self.RC.socialLikes, Literal(likes)))

                        if "youtube" in social:

                            youtube = self.n + "youtube"

                            orgSocialNetworkName = self.clean(churchOrgName) + " youtube"
                            orgSocialNetworkId = self.generate_random_string()
                            orgSocialNetwork = self.n + orgSocialNetworkId

                            g2.add((orgSocialNetwork, RDF.type, self.OWL.NamedIndividual))
                            g2.add((orgSocialNetwork, RDF.type, self.RC.OrgSocialNetwork))
                            g2.add((orgSocialNetwork, self.RC.socialNetwork, youtube))
                            g2.add((orgSocialNetwork, self.RC.name, Literal(orgSocialNetworkName)))

                            if "url" in social["youtube"]:
                                g2.add((orgSocialNetwork, self.RC.uri, Literal(social["youtube"]["url"])))
                            elif "youtubeUrl" in social:
                                g2.add((orgSocialNetwork, self.RC.uri, Literal(social["youtubeUrl"])))

                            if "subscribers" in social["youtube"]:
                                subscribers = self.convertToNumber(social["youtube"]["subscribers"].replace("subscribers", "").strip())
                                g2.add((orgSocialNetwork, self.RC.socialSubscribers, Literal(subscribers)))
                            if "views" in social["youtube"]:
                                views = self.convertToNumber(social["youtube"]["views"].replace("views", "").strip())
                                g2.add((orgSocialNetwork, self.RC.socialViews, Literal(views)))

                            g2.add((orgSocialNetwork, self.RC.socialNetwork, youtube))

                            g2.add((chOrg, self.RC.orgSocialNetwork, orgSocialNetwork))





                    if "chmss" in church:
                        for chms in church["chmss"]:

                            if chms["type"] == "squarespace":

                                # add business system
                                squarespaceBusinessSystemName = "squarespace"
                                squarespaceBusinessSystemId = squarespaceBusinessSystemName.replace(" ", "").lower()
                                squarespaceBusinessSystem = self.n + squarespaceBusinessSystemId

                                g2.add((chOrg, self.RC.hasBusinessSystem, squarespaceBusinessSystem))

                            if chms["type"] == "churchcenter":
                                # add business system
                                churchCenterBusinessSystemName = "churchcenter"
                                churchCenterBusinessSystemId = churchCenterBusinessSystemName.replace(" ", "").lower()
                                churchCenterBusinessSystem = self.n + churchCenterBusinessSystemId

                                g2.add((chOrg, self.RC.hasChurchmanagementSystem, churchCenterBusinessSystem))


                    if "contacts" in church:

                        memberCount = 0

                        contacts = church["contacts"]
                        for contact in contacts:

                            isValid = "yes"
                            if "valid" in contact:
                                isValid = contact["valid"]

                            if isValid == "yes":

                                memberCount = memberCount + 1

                                name = self.clean(contact["name"])

                                personName = name
                                personId = self.generate_random_string()
                                person = self.n + personId

                                g2.add((person, RDF.type, self.OWL.NamedIndividual))
                                g2.add((person, RDF.type, self.RC.Person))
                                g2.add((person, self.RC.name, Literal(personName)))

                                if "title" in contact:
                                    title = self.clean(contact["title"])
                                    g2.add((person, self.RC.title, Literal(title)))

                                if "photo" in contact:
                                    photo = contact["photo"]
                                    g2.add((person, self.RC.photo, Literal(photo)))

                                g2.add((chOrg, self.RC.hasMember, person))


                        if memberCount > 0:
                            g2.add((chOrg, self.RC.memberCount, Literal(str(memberCount))))


                    if "link" in church:

                        link = church["link"]
                        parsed_url = urlparse(link)
                        churchDomain = parsed_url.netloc.replace("www.", "")
                        churchDomain = churchDomain.replace("/", "").strip()

                        query = """select ?website where { 
                                                            ?website rdf:type rc:Website .  
                                                            ?website rc:uri ?uri . 
                                                            FILTER(STRSTARTS(LCASE( \"""" + churchDomain + """\"), LCASE(?uri))) }
                                                            """

                        results = g2.query(query)

                        websiteUri = churchDomain
                        websiteId = self.clean(churchDomain)
                        website = self.n + websiteId

                        if len(results) <= 0:
                            g2.add((website, RDF.type, self.OWL.NamedIndividual))
                            g2.add((website, self.RC.type, self.RC.Website))
                            g2.add((website, self.RC.uri, Literal(websiteUri)))


                        g2.add((chOrg, self.RC.hasWebsite, website))



            #print(f"Graph has {len(g2)} triples.\n")
            print(".")

        self.saveRDFFile(g2)