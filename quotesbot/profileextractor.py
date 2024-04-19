from quotesbot.profilecheck import ProfileCheck
from urllib.parse import urlparse
import re


class DivCount:
    def __init__(self, div, level, className, count):
        self.div = div
        self.level = level
        self.className = className
        self.count = count


class ProfileExtractor:
    name = "profileextractor"

    def addToElement(self, schemaStruct, attribute, elTagName, elClassName, elStyleName):

        #print("att: ", attribute, ", tag: ", elTagName, ", class: ", elClassName)

        #check if tag name is present and update count if it is
        elTag = None
        for tag in schemaStruct[attribute]["tags"]:
            if "name" in tag and tag["name"] == elTagName:
                found = True
                tag["count"] = tag["count"] + 1

                elTag = tag
                break

        # add tag if not present
        if elTag == None:
            elTag = {
                "name": elTagName,
                "count": 1
            }
            schemaStruct[attribute]["tags"].append(elTag)


        # add class to elTag schema
        if "classNames" not in elTag:
            elTag["classNames"] = []


        foundClassName = False
        for className in elTag["classNames"]:
            if className["name"] == elClassName:
                className["count"] = className["count"] + 1
                foundClassName = True

        if foundClassName == False:
            clss = {
                "name": elClassName,
                "count": 1
            }

            elTag["classNames"].append(clss)


        # add style to elTag schema
        if "styleNames" not in elTag:
            elTag["styleNames"] = []


        foundStyleName = False
        for styleName in elTag["styleNames"]:
            if styleName["name"] == elStyleName:
                styleName["count"] = styleName["count"] + 1
                foundStyleName = True

        if foundStyleName == False:
            styl = {
                "name": elStyleName,
                "count": 1
            }

            elTag["styleNames"].append(styl)


    def addFirst(self, schemaStruct, attribute, cLevel, cClassName):

        #print("first ----- att: ", attribute, ", level: ", cLevel, ", class: ", cClassName)

        #check if tag name is present and update count if it is
        elFirst = None
        for first in schemaStruct[attribute]["first"]:
            if "level" in first and first["level"] == cLevel and \
                    "class" in first and first["class"] == cClassName:

                first["count"] = first["count"] + 1
                elFirst = first
                break

        # add tag if not present
        if elFirst == None:
            elFirst = {
                "level": cLevel,
                "class": cClassName,
                "count": 1
            }
            schemaStruct[attribute]["first"].append(elFirst)



    def commonDiv(self, el1, el2):

        ancestors1 = el1.xpath('ancestor::div')
        ancestors2 = el2.xpath('ancestor::div')

        # print('look for common div 1: ', ancestors1)
        # print('look for common div 2: ', ancestors2)

        common_ancestor_div = None
        common_ancestor_count = None

        count = 1
        for ancestor1 in ancestors1[::-1]:
            s1 = str(ancestor1)
            # print('look for common div 1: ', s1)
            for ancestor2 in ancestors2[::-1]:
                s2 = str(ancestor2)
                # print('look for common div 2: ', s2)

                if s1 == s2:
                    #print('s1: ', s1)
                    #print('class ', previousClassName.split()[0])
                    common_ancestor_div = ancestor1
                    common_ancestor_class = ancestor2.attrib.get("class", "")
                    if len(common_ancestor_class.split()) > 0:
                        common_ancestor_class = common_ancestor_class.split()[0]
                    break

                #previousClassName = ancestor2.attrib.get("class", "")
            if common_ancestor_div:
                break

            count = count + 1

        cnt = 0
        if common_ancestor_div != None:
            common_ancestor_count = len(ancestors1) - count
            #common_ancestor_class = common_ancestor_div.xpath('//div/@class')

        #print('classname: ', common_ancestor_class)
        return common_ancestor_div, common_ancestor_count, common_ancestor_class

    def getBoundingDiv(self, els):
        #print("look for lowest common div")
        lastEl = None
        divCounts = []
        for el1 in els[:5]:
            if lastEl != None:
                cDiv, cDivLevel, cClassName = self.commonDiv(el1, lastEl)
                #cDivLevel = self.commonDivCount(el1, lastEl)

                divCount = DivCount(cDiv, cDivLevel, cClassName, 1)
                matching_items = [item for item in divCounts if item.level == cDivLevel and item.className == cClassName]
                if (len(matching_items) == 0):
                    divCounts.append(divCount)
                else:
                    matching_items[0].count = matching_items[0].count + 1

            lastEl = el1

        sortedDivCounts = sorted(divCounts, reverse=True,  key=lambda x: x.count)
        bestDivLevel = sortedDivCounts[0].level
        bestClassName = sortedDivCounts[0].className
        bestDiv = sortedDivCounts[0].div

        print("lowest: ", bestDivLevel, ", class name: ", bestClassName)
        return bestDiv, bestClassName


    def replace_multiple_spaces(self, text):
        # Replace multiple spaces with just one space
        cleaned_text = re.sub(r'\s+', ' ', text)
        return cleaned_text

    def getContact(self, contacts, name, email):

        for contact in contacts:
            if name != "" and contact["name"] == name:
                return contact
            if email != "" and contact["email"] == email:
                return contact

        return None

    def setChurchContact(self, currentChurch,
        photo,
        name,
        title,
        department,
        email
    ):

        if name == None or name == "":
            return


        # check that name is in email somewhere
        foundPart = False
        parts = name.split()
        for part in parts:
            if email.lower().find(part.lower()) >= 0:
                foundPart = True
        if foundPart == False:
            email = ""


        contacts = []
        if "contacts" in currentChurch:
            contacts = currentChurch["contacts"]

        contact = self.getContact(contacts, name, email)
        if contact is None:
            contact = {}
            contacts.append(contact)

        contact["name"] = name
        if email is not None:
            contact["email"] = email
        if title is not None:
            contact["title"] = title
        if department is not None:
            contact["department"] = department
        if photo is not None:
            contact["photo"] = photo


        print("")
        print("contact record:")
        print("name: ", name)
        print("title: ", title)
        print("department: ", department)

        print('photo: ', photo)
        print('email: ', email)


    def extractProfilesFromWebPage(self, currentChurch, response, boundaryLevel, boundaryClass):

        print('**************** extract profiles from webpage: ', response.url)

        print("--------- parse page: ", response.url)
        profCheck = ProfileCheck()

        schemaStructure = {
            "name": {
                "tags": []
            },
            "photo": {
                "tags": [],
                "first": []
            },
            "email": {
                "tags": []
            },
            "department": {
                "tags": []
            },
            "title": {
                "tags": []
            }
        }

        photoFirst_el = None

        hasHitBoundary = False
        profilePhoto = None
        profileName = None
        profileTitle = None
        profileDepartment = None
        profileEmail = None


        #path = response.xpath(
        #    '//p | //div[not(descendant::div)] | //a[starts-with(@href, "mailto:")] | //img | //h1 | //h2 | //h3 | //h4 | //h5 | //h6 |  //strong | //span ')
        path = response.xpath(
            '//p | //div | //a[starts-with(@href, "mailto:")] | //img | //h1 | //h2 | //h3 | //h4 | //h5 | //h6 |  //strong | //span ')
        for el in path:

            tagName = el.xpath('name()').extract()[0]
            className = el.attrib.get('class', '')
            styleName = el.attrib.get('style', '')

            if tagName == "div":
                ancestors = el.xpath('ancestor::div')
                descendants = el.xpath('descendant::div')

                ancestorLevel = len(ancestors)
                descendantLevel = len(descendants)


                #print("className: ", className, ", level an: ", ancestorLevel, ", level desc: ", descendantLevel)

                # if we hit boundary marker then set church contact
                if (className != "" and className.split()[0] == boundaryClass and ancestorLevel == boundaryLevel):

                    hasHitBoundary = True
                    print("hit boundary: ", className.split()[0], ", level: ", ancestorLevel)

                    self.setChurchContact(currentChurch, profilePhoto, profileName, profileTitle, profileDepartment, profileEmail)

                    profilePhoto = None
                    profileName = None
                    profileTitle = None
                    profileDepartment = None
                    profileEmail = None

                if descendantLevel > 1:
                    continue


            # get text inside element
            visible_text = el.xpath('.//text()[normalize-space()]').extract()
            text = self.replace_multiple_spaces(' '.join(visible_text))

            shortText = text.strip()[:120]
            if len(shortText) > 5:
                # print("short text: ", shortText)

                personName = profCheck.isPersonName(shortText)
                if personName is not None:

                    if profileName is None:
                        profileName = personName
                    self.addToElement(schemaStructure, "name", tagName, className, styleName)

                    if hasHitBoundary and photoFirst_el is not None:
                        cDiv, cDivLevel, cClassName = self.commonDiv(photoFirst_el, el)
                        self.addFirst(schemaStructure, "photo", cDivLevel, cClassName)



                jobTitle = profCheck.isProfileJobTitle(shortText)
                if jobTitle is not None:

                    if profileTitle is None:
                        profileTitle = jobTitle
                    self.addToElement(schemaStructure, "title", tagName, className, styleName)

                    if hasHitBoundary and photoFirst_el is not None:
                        cDiv, cDivLevel, cClassName = self.commonDiv(photoFirst_el, el)
                        self.addFirst(schemaStructure, "photo", cDivLevel, cClassName)

                department = profCheck.isProfileDepartment(shortText)
                if department is not None:

                    if profileDepartment is None:
                        profileDepartment = department
                    self.addToElement(schemaStructure, "department", tagName, className, styleName)

                    if hasHitBoundary and photoFirst_el is not None:
                        cDiv, cDivLevel, cClassName = self.commonDiv(photoFirst_el, el)
                        self.addFirst(schemaStructure, "photo", cDivLevel, cClassName)

            # get mailto inside elements
            if el.xpath('@href').get():

                email_address = el.xpath('@href').get().replace("mailto:", "")
                if email_address != "":

                    if profileEmail is None:
                        profileEmail = email_address
                    self.addToElement(schemaStructure, "email", tagName, className, styleName)

                    if  hasHitBoundary and photoFirst_el is not None:
                        cDiv, cDivLevel, cClassName = self.commonDiv(photoFirst_el, el)
                        self.addFirst(schemaStructure, "photo", cDivLevel, cClassName)


            # get photo inside elements
            if el.xpath('@src | @data-src | @srcset').get():

                img_src = el.xpath('@src | @data-src | @srcset').get()
                # print("***************************** img src found: ", img_src)

                isCDN = False
                if img_src.startswith("https://images.squarespace-cdn.com") or \
                        img_src.startswith("https://static.wixstatic.com") or \
                        img_src.startswith("https://thechurchco-production.s3.amazonaws.com") or \
                        img_src.startswith("https://s3.amazonaws.com/media.cloversites.com") or \
                        img_src.startswith("https://images.squarespace-cdn.com"):
                    isCDN = True

                parsed_url = urlparse(response.url)
                domain = parsed_url.netloc

                if img_src.startswith('/') == True and img_src.startswith('//') == False:
                    img_src = "https://" + domain + img_src

                if isCDN or img_src.find(domain.replace("www.", "")) >= 0:
                    # print("********** check photo ****** ", img_src)
                    if profCheck.isProfilePhoto(img_src):

                        tagName = el.xpath('name()').extract()[0]

                        if  hasHitBoundary and profilePhoto is None:
                            profilePhoto = img_src
                        self.addToElement(schemaStructure, "photo", tagName, className, styleName)

                        photoFirst_el = el


        if hasHitBoundary:
            self.setChurchContact(currentChurch, profilePhoto, profileName, profileTitle, profileDepartment,
                                  profileEmail)

        #print("schema", schemaStructure)


