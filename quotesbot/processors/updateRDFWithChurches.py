from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS
import json
import random
import string

class UpdateRDFWithChurches:

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


        glooOrgName = "gloo"
        glooOrgId = glooOrgName.replace(" ", "").lower()
        glooOrg = self.n + glooOrgId

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
        churchCenterBusinessSystem = self.n + churchCenterBusinessSystemId

        g2.add((churchCenterBusinessSystem, RDF.type, self.OWL.NamedIndividual))
        g2.add((churchCenterBusinessSystem, RDF.type, self.RC.ChurchmanagementSystem))
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
            print("problem converting: ", s)
            return 0

    def updateWithChurches(self):

        g2 = self.setupRDFFile()

        for church in self.churches:

            if "name" in church and "is-primary" in church and church["is-primary"] == "yes":

                glooOrgName = "gloo"
                glooOrgId = glooOrgName.replace(" ", "").lower()
                glooOrg = self.n + glooOrgId

                squarespaceBusinessSystemName = "squarespace"
                squarespaceBusinessSystemId = squarespaceBusinessSystemName.replace(" ", "").lower()
                squarespaceBusinessSystem = self.n + squarespaceBusinessSystemId

                churchCenterBusinessSystemName = "churchcenter"
                churchCenterBusinessSystemId = churchCenterBusinessSystemName.replace(" ", "").lower()
                churchCenterBusinessSystem = self.n + churchCenterBusinessSystemId

                if "latitude" in church and "longitude" in church and "uniqueId" in church:

                    churchOrgName = self.clean(church["name"])
                    churchOrgId = church["uniqueId"]
                    chOrg = self.n + churchOrgId

                    '''
                    query = """select ?church where { ?church rc:name ?churchName .
                                                FILTER(?church = <""" + str(chOrg) + """>) }
                                                """
    
                    results = g2.query(query)
    
                    if len(results) == 0:
                    '''

                    g2.add((chOrg, RDF.type, self.OWL.NamedIndividual))
                    g2.add((chOrg, RDF.type, self.CC.ChurchOrganization))
                    g2.add((chOrg, self.RC.name, Literal(churchOrgName)))

                    if "primarySource" in church:
                        primarySource = church["primarySource"]
                        g2.add((chOrg, self.RC.primarySource, Literal(primarySource)))
                    else:
                        primarySource = "unknown"
                        g2.add((chOrg, self.RC.primarySource, Literal(primarySource)))


                    if "primaryRace" in church:
                        primaryRace = church["primaryRace"]
                        g2.add((chOrg, self.CC.primaryRace, Literal(primaryRace)))
                    else:
                        primaryRace = "unknown"
                        g2.add((chOrg, self.CC.primaryRace, Literal(primaryRace)))


                    # update church with denomination
                    denomination = "unknown"
                    if "denomination" in church and church["denomination"] != "unknown":

                        denomination = church["denomination"]
                        if denomination == "edit denomination":
                            denomination = "unknown"

                    else:
                        if "openai" in church:
                            if "denomination" in church["openai"] and church["openai"]["denomination"] != '':
                                denomination = church["openai"]["denomination"]


                        if "mergeChurches" in church:
                            for mergeChurch in church["mergeChurches"]:
                                if "denomination" in mergeChurch:
                                    denomination = mergeChurch["denomination"]
                                    if denomination == "edit denomination":
                                        denomination = "unknown"
                                    break

                    print("??????????????????? query for denomination ")

                    # link church to denomination
                    query = """select ?denomination ?tag where { 
                                    ?denomination rdf:type cc:Denomination .  
                                    ?denomination cc:denominationTag ?tag . 
                                    ?tag rc:name ?tagName . 
                                    FILTER(STRSTARTS(LCASE( \"""" + denomination + """\"), LCASE(?tagName))) }
                                    """

                    try:
                        results = g2.query(query)

                        if len(results) > 0:
                            for row in results:
                                g2.add((chOrg, self.CC.denomination, row["denomination"]))
                                g2.add((chOrg, self.CC.denominationTag, row["tag"]))
                                break
                        else:
                            g2.add((chOrg, self.CC.denomination, "unknown"))
                            g2.add((chOrg, self.CC.denominationTag, '<cc:denominationTag rdf:resource="http://churchcore.io/frontrange#unknowntag"/>'))

                    except Exception as e:
                        print("get denomination err: ", e)



                    # link church to network
                    if "network" in church and church["network"] != "unknown":
                        networks = church["network"]

                        networkList = networks.split(',')
                        for network in networkList:
                            print("************ find network: ", network)
                            query = """select ?network ?tag where { 
                                            ?network rdf:type cc:Network .  
                                            ?network cc:networkTag ?tag . 
                                            ?tag rc:name ?tagName . 
                                            FILTER(STRSTARTS(LCASE( \"""" + network + """\"), LCASE(?tagName))) }
                                            """

                            try:
                                results = g2.query(query)

                                if len(results) > 0:
                                    print("****** found network **********", results)
                                    for row in results:

                                        print("***************  add network to org ***********")
                                        g2.add((chOrg, self.CC.network, row["network"]))
                                        g2.add((chOrg, self.CC.networkTag, row["tag"]))
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



                    if "org" in church:
                        orgName = church["org"]


                        orgChurchOrgName = self.clean(orgName)
                        orgChurchOrgId = orgChurchOrgName.replace(" ", "").lower()
                        orgChOrg = self.n + orgChurchOrgId

                        g2.add((orgChOrg, RDF.type, self.OWL.NamedIndividual))
                        g2.add((orgChOrg, RDF.type, self.CC.ChurchOrganization))
                        g2.add((orgChOrg, self.RC.name, Literal(orgChurchOrgName)))

                        g2.add((orgChOrg, self.RC.hasSubOrganization, chOrg))



                    churchSiteName = self.clean(church["name"]) + " Site"
                    churchSiteId = self.generate_random_string() # churchSiteName.replace(" ", "").lower()
                    chSite = self.n + churchSiteId

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
                        if "city" in church["addressInfo"] and "zipcode" in \
                                church["addressInfo"]:

                            print(".. add site address ..")

                            churchSiteAddressName = self.clean(church["name"]) + " Site Address"
                            churchSiteAddressId = self.generate_random_string() # churchSiteAddressName.replace(" ", "").lower()
                            chSiteAddress = self.n + churchSiteAddressId

                            g2.add((chSiteAddress, RDF.type, self.OWL.NamedIndividual))
                            g2.add((chSiteAddress, RDF.type, self.RC.PostalAddress))
                            g2.add((chSiteAddress, self.RC.name, Literal(churchSiteAddressName)))

                            if  "city" in church["addressInfo"] and \
                                "zipcode" in church["addressInfo"] and \
                                "street" in church["addressInfo"]:

                                chSiteCity = church["addressInfo"]["city"]
                                #chSiteCounty = church["addressInfo"]["county"]
                                chSiteZipcode = church["addressInfo"]["zipcode"]
                                address1 = church["addressInfo"]["street"]
                                g2.add((chSiteAddress, self.VCARD.locality, Literal(chSiteCity)))
                                #g2.add((chSiteAddress, self.VCARD.region, Literal(chSiteCounty)))
                                g2.add((chSiteAddress, self.VCARD.postalCode, Literal(chSiteZipcode)))
                                g2.add((chSiteAddress, self.VCARD.streetAddress, Literal(address1)))

                            if "latitude" in church and "longitude" in church:
                                chSiteAddressLat = church["latitude"]
                                chSiteAddressLong = church["longitude"]
                                g2.add((chSiteAddress, self.VCARD.latitude, Literal(chSiteAddressLat)))
                                g2.add((chSiteAddress, self.VCARD.longitude, Literal(chSiteAddressLong)))

                            g2.add((chSite, self.RC.hasSiteAddress, chSiteAddress))

                            # link church to city
                            query = """select ?city ?name where { ?city rdf:type rc:City .  ?city rc:name ?name . 
                                                                FILTER(LCASE(?name) = LCASE( \"""" + chSiteCity + """\")) }
                            
                                                              """
                            try:
                                results = g2.query(query)

                                if len(results) > 0:
                                    for row in results:
                                        print("row: ", row["city"])
                                        g2.add((chSite, self.RC.city, row["city"]))
                            except:
                                print("err getting city")


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
                                g2.add((chOrg, self.RC.hasChurchmanagementSystem, churchCenterBusinessSystem))

                    leadPastorName = None
                    leadPasterUniqueId = None
                    if "leadPastor" in church:
                        leadPastor = church["leadPastor"]
                        if "name" in leadPastor:

                            name = self.clean(leadPastor["name"])
                            leadPastorName = name
                            leadPasterUniqueId = self.generate_random_string()

                            personName = name
                            personId = leadPasterUniqueId # personName.replace(" ", "").lower()
                            person = self.n + personId

                            g2.add((person, RDF.type, self.OWL.NamedIndividual))
                            g2.add((person, RDF.type, self.RC.Person))
                            g2.add((person, self.RC.name, Literal(personName)))
                            g2.add((person, self.RC.title, Literal("lead pastor")))

                            g2.add((chOrg, self.RC.hasMember, person))

                            postName = churchOrgName + " Lead Pastor"
                            postId = self.generate_random_string() # postName.replace(" ", "").lower()
                            post = self.n + postId

                            g2.add((post, RDF.type, self.OWL.NamedIndividual))
                            g2.add((post, RDF.type, self.RC.Post))
                            g2.add((post, self.RC.name, Literal(postName)))
                            g2.add((post, self.RC.heldBy, person))

                            g2.add((chOrg, self.RC.hasPost, post))

                    if "contacts" in church:

                        memberCount = 0

                        contacts = church["contacts"]
                        for contact in contacts:

                            if "valid" in contact:

                                isValid = contact["valid"]
                                if isValid == "yes":

                                    memberCount = memberCount + 1

                                    name = self.clean(contact["name"])

                                    uniqueId = self.generate_random_string()
                                    if leadPastorName != None and leadPastorName.lower() == name.lower():
                                        uniqueId = leadPasterUniqueId

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
                        websiteUri = church["link"];
                        websiteId = self.generate_random_string() # self.clean(websiteUri.replace(" ", "").lower())
                        website = self.n + websiteId

                        g2.add((website, RDF.type, self.OWL.NamedIndividual))
                        g2.add((website, self.RC.type, self.RC.Website))
                        g2.add((website, self.RC.uri, Literal(websiteUri)))

                        g2.add((chOrg, self.RC.hasWebsite, website))



            #print(f"Graph has {len(g2)} triples.\n")
            print(".")

        self.saveRDFFile(g2)