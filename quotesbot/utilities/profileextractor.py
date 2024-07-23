from quotesbot.profilecheck import ProfileCheck
from urllib.parse import urlparse
import re
import os

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


    def addFirst(self, schemaStruct, attribute, tag, cClassName, cLevel):

        if tag is None:
            return

        tag = tag.strip()

        if cClassName is not None:
            cClassName = cClassName.strip()


        #print("first ----- att: ", attribute, ", level: ", cLevel, ", class: ", cClassName)


        #check if tag name is present and update count if it is
        if cClassName is not None:
            elFirst = None
            for first in schemaStruct[attribute]["first"]:
                if "level" in first and first["level"] == cLevel and \
                        "class" in first and first["class"] == cClassName and \
                        "tag" in first and first["tag"] == tag:

                    first["count"] = first["count"] + 1
                    elFirst = first
                    break

            # add tag if not present
            if elFirst == None:
                elFirst = {
                    "tag": tag,
                    "level": cLevel,
                    "class": cClassName,
                    "count": 1
                }
                schemaStruct[attribute]["first"].append(elFirst)

        else:
            elFirst = None
            for first in schemaStruct[attribute]["first"]:
                if "level" in first and first["level"] == cLevel and \
                        "tag" in first and first["tag"] == tag:
                    first["count"] = first["count"] + 1
                    elFirst = first
                    break

            # add tag if not present
            if elFirst == None:
                elFirst = {
                    "tag": tag,
                    "level": cLevel,
                    "class": "",
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
        common_ancestor_class = None

        count = 1
        for ancestor1 in ancestors1[::-1]:
            s1 = str(ancestor1)
            # print('look for common div 1: ', s1)
            for ancestor2 in ancestors2[::-1]:
                s2 = str(ancestor2)
                # print('look for common div 2: ', s2)

                if s1 == s2:
                    cls = ancestor2.attrib.get("class", "")
                    if cls is None or cls == "":
                        cls = ancestor2.attrib.get("id", "")
                    if cls is None or cls == "":
                        cls = ancestor2.attrib.get("data-mesh-id", "")

                    if len(cls.split()) > 0:
                        # print('s1: ', s1)
                        common_ancestor_div = ancestor1
                        common_ancestor_class = ancestor2.attrib.get("class", "")
                        if common_ancestor_class is None or common_ancestor_class == "":
                            common_ancestor_class = ancestor2.attrib.get("id", "")
                        if common_ancestor_class is None or common_ancestor_class == "":
                            common_ancestor_class = ancestor2.attrib.get("data-mesh-id", "")

                        common_ancestor_class = common_ancestor_class.split()[0].strip()
                        #print("common ancestor class: ", common_ancestor_class)

                        break

            if common_ancestor_div:
                break

            count = count + 1

        cnt = 0
        if common_ancestor_div != None:
            common_ancestor_count = len(ancestors1) - count

        return common_ancestor_div, common_ancestor_count, common_ancestor_class

    def commonLi(self, el1, el2):

        ancestors1 = el1.xpath('ancestor::li')
        ancestors2 = el2.xpath('ancestor::li')

        # print('look for common li 1: ', ancestors1)
        # print('look for common li 2: ', ancestors2)

        common_ancestor_li = None
        common_ancestor_class = None

        for ancestor1 in ancestors1[::-1]:
            s1 = str(ancestor1)
            # print('look for common li 1: ', s1)
            for ancestor2 in ancestors2[::-1]:
                s2 = str(ancestor2)
                # print('look for common li 2: ', s2)

                if s1 == s2:
                    # print('s1: ', s1)
                    # print('class ', previousClassName.split()[0])
                    common_ancestor_li = ancestor1
                    common_ancestor_class = ancestor2.attrib.get("class", "")
                    if common_ancestor_class is None or common_ancestor_class == "":
                        common_ancestor_class = ancestor2.attrib.get("id", "")
                    if common_ancestor_class is None or common_ancestor_class == "":
                        common_ancestor_class = ancestor2.attrib.get("data-mesh-id", "")

                    if len(common_ancestor_class.split()) > 0:
                        common_ancestor_class = common_ancestor_class.split()[0].strip()
                    break

                # previousClassName = ancestor2.attrib.get("class", "")
            if common_ancestor_li:
                break

        # print('classname: ', common_ancestor_class)
        return common_ancestor_li, common_ancestor_class

    def commonArticle(self, el1, el2):

        ancestors1 = el1.xpath('ancestor::article')
        ancestors2 = el2.xpath('ancestor::article')

        #print('look for common article 1: ', ancestors1)
        #print('look for common article 2: ', ancestors2)

        common_ancestor_article = None

        for ancestor1 in ancestors1[::-1]:
            s1 = str(ancestor1)
            #print('look for common article 1: ', s1)
            for ancestor2 in ancestors2[::-1]:
                s2 = str(ancestor2)
                #print('look for common article 2: ', s2)

                if s1 == s2:
                    common_ancestor_article = ancestor1
                    #print('*********************** found common article ')
                    break

            if common_ancestor_article:
                break

        return common_ancestor_article


    def commonSection(self, el1, el2):

        ancestors1 = el1.xpath('ancestor::section')
        ancestors2 = el2.xpath('ancestor::section')

        #print('look for common section 1: ', ancestors1)
        #print('look for common section 2: ', ancestors2)

        common_ancestor_section = None

        for ancestor1 in ancestors1[::-1]:
            s1 = str(ancestor1)
            #print('look for common section 1: ', s1)
            for ancestor2 in ancestors2[::-1]:
                s2 = str(ancestor2)
                #print('look for common section 2: ', s2)

                if s1 == s2:
                    common_ancestor_section = ancestor1
                    #print('*********************** found common section ')
                    break

            if common_ancestor_section:
                break

        return common_ancestor_section

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
            if name != None and name != "" and "name" in contact and contact["name"] == name:
                return contact
            if email != None and email != "" and "email" in contact and contact["email"] == email:
                return contact

        return None

    def setChurchContact(self, currentChurch,
        name,
        title,
        department,
        email,
        photo
    ):

        if name is None or name == "":
            return


        # check that name is in email somewhere
        if email is not None:
            foundPart = False
            parts = name.split()
            for part in parts:
                part = part.strip()
                if email.lower().find(part.lower()) >= 0:
                    foundPart = True
            if foundPart == False:
                email = None


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

        currentChurch["contacts"] = contacts


        print("****************************")
        print("contact record:")
        print("name: ", name)
        print("title: ", title)
        print("department: ", department)

        print('photo: ', photo)
        print('email: ', email)
        print("****************************")

    def isSmallerThan(self, el, maxSize):

        heightStr = el.xpath('@height').get()
        widthStr = el.xpath('@width').get()

        try:
            height = int(heightStr)
            width = int(widthStr)

            if height < maxSize and width < maxSize:
                return True
            else:
                return False
        except Exception:
            return False

        return False


    def extractProfilesUsingSchema(self, currentChurch, response, schemaStructure):

        print("+++++++++++++++++++++++++++++++++++++++++")
        print("+++++++++++++++++++++++++++++++++++++++++")
        print("+++++++++++++++++++++++++++++++++++++++++")
        print("schema", schemaStructure)

        if "first" in schemaStructure["photo"] and len(schemaStructure["photo"]["first"]) > 0:

            cls = None
            level = None

            sorted_data = sorted(schemaStructure["photo"]["first"], key=lambda x: x['count'], reverse=True)
            #sorted_data = sorted(schemaStructure["photo"]["first"], key=lambda x: (x['class'], x['level']), reverse=True)

            processed = 0
            lastTag = None
            lastCls = None
            for tagData in sorted_data:

                count = tagData["count"]
                tag = tagData["tag"].strip()
                cls = tagData["class"].strip()
                level = tagData["level"]

                print("PHOTO first boundary ===> tag: >", tag, "<, cls: >", cls, "<, level: ", level, ", count, ", count)

                #if lastTag is not None and lastCls is not None and \
                #    lastTag == tag and lastCls == cls:
                #    print("continue ....... ")
                #    continue

                if tag == "div" and level is not None and level > 2 and count >= 1:
                    # get different article counts
                    pathQuery = '//div[contains(@class, "' + cls + '")]'
                    path = response.xpath(pathQuery)
                    pathCount = len(path)
                    print("photo div path count: ", pathCount, ", count: ", count)
                    if pathCount >= count/4:
                        processed = processed + 1
                        print(">>>>>>>>>>>>>>>>>>>>>>>>  call photo for boundary tag: ", tag, ", and class: ", cls)
                        self.extractProfilesFromWebPage(currentChurch, response, "photo", tag, cls, level)

                if tag == "li" and count > 1:
                    processed = processed + 1
                    print(">>>>>>>>>>>>>>>>>>>>>>>>  call photo for boundary tag: ", tag, ", and class: ", cls)
                    self.extractProfilesFromWebPage(currentChurch, response, "photo", tag, cls, level)

                if tag == "article" and count > 1:
                    # get different article counts
                    path = response.xpath('//article')
                    pathCount = len(path)
                    print("photo article path count: ", pathCount, ", count: ", count)
                    if pathCount >= count/4:
                        processed = processed + 1
                        print(">>>>>>>>>>>>>>>>>>>>>>>>  call photo for boundary tag: ", tag, ", and class: ", cls)
                        self.extractProfilesFromWebPage(currentChurch, response, "photo", tag, cls, level)

                if tag == "section" and count > 1:
                    # get different section counts
                    path = response.xpath('//section')
                    pathCount = len(path)
                    print("photo section path count: ", pathCount, ", count: ", count)
                    if pathCount >= count/4:
                        processed = processed + 1
                        print(">>>>>>>>>>>>>>>>>>>>>>>>  call photo for boundary tag: ", tag, ", and class: ", cls)
                        self.extractProfilesFromWebPage(currentChurch, response, "photo", tag, cls, level)

                print("processed: ", processed)
                if processed >= 2:
                    break


                lastTag = tag
                lastCls = cls

        if "first" in schemaStructure["name"] and len(schemaStructure["name"]["first"]) > 0:

            processed = 0
            cls = None
            level = None

            #sorted_data = sorted(schemaStructure["name"]["first"], key=lambda x: (x['class'], x['level']), reverse=True)
            sorted_data = sorted(schemaStructure["name"]["first"], key=lambda x: x['count'], reverse=True)


            lastTag = None
            lastCls = None
            for tagData in sorted_data:

                count = tagData["count"]
                tag = tagData["tag"]
                cls = tagData["class"]
                level = tagData["level"]

                print("NAME first boundary ===> tag: >", tag, "<, cls: >", cls, "<, level: ", level, ", count, ", count)

                #if lastTag is not None and lastCls is not None and \
                #        lastTag == tag and lastCls == cls:
                #    print("continue ....... ")
                #    continue

                if count >= 1:

                    pathQuery = '//' + tag
                    if cls != None and cls != '':
                        pathQuery = '//div[contains(@class, "' + cls + '")]'

                    print("path query: ", pathQuery)
                    path = response.xpath(pathQuery)
                    pathCount = len(path)
                    print("name path count: ", pathCount, ", count: ", count)
                    if pathCount >= count/4:
                        processed = processed + 1
                        print(">>>>>>>>  call name for boundary tag: ", tag, ", and class: ", cls)
                        self.extractProfilesFromWebPage(currentChurch, response, "name", tag, cls, level)

                if processed >= 2:
                    break


                lastTag = tag
                lastCls = cls

    def evaluateToSetChurchContacts(self, currentChurch, boundaryAttribute, profilePhoto, requirePhotoCheck, profileName, profileTitle, profileDepartment, profileEmail, imageUrls):

        if (boundaryAttribute == "photo" and profilePhoto is not None and profileName is not None):
            print("-------------- boundary found")

            # if we didn't find a person in photo then check that name is in photo url
            validMatch = False
            if requirePhotoCheck == None:
                #print("found profile photo so not check required")
                validMatch = True
            else:
                #print("check the parts: ", profileName, ", in ", requirePhotoCheck)
                for part in profileName.lower().split():
                    part = part.strip()
                    if len(part) > 2 and requirePhotoCheck.lower().find(part) >= 0:
                        print("image url matches name: ", part)
                        validMatch = True
                        break



            if validMatch:
                #print("set because of photo a: ", profileName)
                self.setChurchContact(currentChurch, profileName, profileTitle, profileDepartment,
                                      profileEmail, profilePhoto)

        if (boundaryAttribute == "photo" and profileName is not None and profileEmail is not None):

            # check that name is in email somewhere
            validMatch = False
            if profileEmail is not None:
                foundPart = False
                parts = profileName.split()
                for part in parts:
                    part = part.strip()
                    if profileEmail.lower().find(part.lower()) >= 0:
                        validMatch = True

            if validMatch:
                # print("set because of profileName and email 1 a: name = ", profileName, ", email = ", profileEmail)
                self.setChurchContact(currentChurch, profileName, profileTitle, profileDepartment,
                                      profileEmail, profilePhoto)

        if (boundaryAttribute == "name" and (profileName is not None and profileEmail is not None)):
            print("................. name and email found: ", profileName, ", email: ", profileEmail)
            # check that name is in email somewhere
            validMatch = False
            if profileEmail is not None:
                foundPart = False
                parts = profileName.split()
                for part in parts:
                    part = part.strip()
                    if profileEmail.lower().find(part.lower()) >= 0:
                        print("found email match")
                        validMatch = True



            # look for photo in style sheets
            if profilePhoto is None:
                #print("look for with name: ", profileName)
                for part in profileName.lower().split():
                    part = part.strip()
                    #print("look for photo for >", part, "<")
                    for imageUrl in imageUrls:
                        if len(part) > 2 and imageUrl.lower().find(part) >= 0:
                            #print("image url in list matches name: ", part)
                            profilePhoto = imageUrl
                            break

                    if profilePhoto is not None:
                        break

            if validMatch:
                print("set because of profileName and email 2 a: ", profileName)
                self.setChurchContact(currentChurch, profileName, profileTitle, profileDepartment,
                                      profileEmail, profilePhoto)


    def extractProfilesFromWebPage(self, currentChurch, response, boundaryAttribute, boundaryTag, boundaryClass, boundaryLevel):

        #print('**************** extract profiles from webpage: ', response.url)
        #if boundaryClass is not None:
        #    print("we are looking for class: ", boundaryClass, ", and level: ", boundaryLevel)


        # remove svg and replace strong with the internal text
        svg_elements = response.xpath("//svg")
        svg_elements.drop()




        #print("--------- parse page: ", response.url)
        #print("body: ", response.body)
        profCheck = ProfileCheck()

        schemaStructure = {
            "name": {
                "tags": [],
                "first": []
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


        nameFirst_el = None

        profilePhoto = None
        requirePhotoCheck = None

        profileName = None
        requireNameCheck = None

        profileTitle = None
        profileDepartment = None
        profileEmail = None

        hasHitBoundaryBefore = False


        # Get the text content of the style element
        css_lines = str(response.body)
        imageUrls = re.findall(r"url\(['\"]?([^'\")]+)", css_lines)


        path = response.xpath(
            '//p | //div | //li | //article | //section | //a | //img | //h1 | //h2 | //h3 | //h4 | //h5 | //h6 ')

        for el in path:

            tagName = el.xpath('name()').extract()[0]

            className = el.attrib.get('class', '')
            if className is not None and className != "":
                className = className.split()[0].strip()
                className = className.strip()

            if className is None or className == "":
                className = el.attrib.get('id', '')
                #print("no class name but has id: ", className)

            if className is None or className == "":
                className = el.attrib.get('data-mesh-id', '')
                #print("no class name but has data-mesh-id: ", className)

            styleName = el.attrib.get('style', '')

            evaluateBoundary = False
            processBoundarySection = True

            # if we have boundary defined then don't process stuff until we hit boundary
            if boundaryAttribute is not None and hasHitBoundaryBefore == False:
                processBoundarySection = False


            # look boundary marker hit then evaluate adding church
            if tagName == "div" or tagName == "li" or tagName == "article" or tagName == "section":

                if tagName == "div":

                    ancestors = el.xpath('ancestor::div')
                    descendants = el.xpath('descendant::div')

                    ancestorLevel = len(ancestors)
                    descendantLevel = len(descendants)



                    #print("className: ", className, ", level an: ", ancestorLevel, ", level desc: ", descendantLevel)


                    # if we hit boundary marker then set church contact
                    #print("check boundary: tag: ", tagName, " == ", boundaryTag, ", class: ", className, " == ", className, ", level ", ancestorLevel, " == ", boundaryLevel)
                    if (tagName == boundaryTag and className != "" and className.split()[0].strip() == boundaryClass and ancestorLevel == boundaryLevel):
                        evaluateBoundary = True
                        print("hit div boundary 1: ------------------------------------------------------ ", className.split()[0].strip(), ", level: ", ancestorLevel)


                    # if  div has no children div then process this div
                    if descendantLevel > 1:
                        processBoundarySection = False

                if tagName == "li":

                    if (tagName == boundaryTag and className != "" and className.split()[0].strip() == boundaryClass):
                        evaluateBoundary = True

                        print("hit li boundary 2: ------------------------------------------------------ ",
                              className.split()[0].strip())

                    # don't process "li" sections
                    processBoundarySection = False

                if tagName == "article":

                    if (tagName == boundaryTag):
                        evaluateBoundary = True

                        print("hit article boundary 3: ------------------------------------------------------ ")

                    # don't process "article" sections
                    processBoundarySection = False

                if tagName == "section":

                    if (tagName == boundaryTag):
                        evaluateBoundary = True

                        print("hit section boundary 4: ------------------------------------------------------ ")

                    # don't process "section" sections
                    processBoundarySection = False


                #check boundary condition and process
                if evaluateBoundary:

                    # make sure we are past first boundary before setting contact
                    if hasHitBoundaryBefore is not None:

                        self.evaluateToSetChurchContacts(currentChurch, boundaryAttribute, profilePhoto,
                                                        requirePhotoCheck, profileName, profileTitle, profileDepartment,
                                                        profileEmail, imageUrls)

                    #print("----------  hit boundary before *************")
                    hasHitBoundaryBefore = True

                    profilePhoto = None
                    requirePhotoCheck = None

                    profileName = None
                    requireNameCheck = None

                    profileTitle = None
                    profileDepartment = None
                    profileEmail = None


            if processBoundarySection:

                # get strong and span elements, so we can not add spaces between those elements
                strongTxts = []
                strong_elements = response.xpath(".//strong")
                for strong in strong_elements:
                    strong_text = ''.join(strong.xpath('.//text()').extract())
                    strongTxts.append(strong_text)

                span_elements = response.xpath(".//span")
                for span in span_elements:
                    span_text = ''.join(span.xpath('.//text()').extract())
                    strongTxts.append(span_text)

                # extract text from elements and put spaces between pieces
                txts = el.xpath('.//text()').extract()

                visible_text = ""
                if len(txts) < 8:
                    for text in txts:
                        if len(text) < 120:
                            if visible_text == "":
                                visible_text = text
                            else:

                                #if visible_text in strongTxts:
                                if text in strongTxts:
                                    #don't add space if element is a strong type
                                    #print("dont add spaces: >", text, "<")
                                    visible_text = visible_text + text
                                else:
                                    #print("add spaces: >", text, "<")
                                    visible_text = visible_text + " " + text

                #print("vis text: ", visible_text)


                #text = self.replace_multiple_spaces(' '.join(visible_text)).strip()
                #print('visible_text: ', text)

                shortText = visible_text.strip()[:120]
                if len(shortText) > 5:
                    #print("short text: ", shortText)

                    personName = profCheck.isPersonName(shortText)
                    if personName is not None:

                        print(">> name: ", personName)
                        if profileName is None:
                            profileName = personName

                        # if we are building schema then do this part
                        if boundaryAttribute is None:
                            self.addToElement(schemaStructure, "name", tagName, className, styleName)

                            if photoFirst_el is not None:

                                # if we didn't find a person in photo then check that name is in photo url
                                validMatch = False
                                if requirePhotoCheck == None:
                                    #print("found profile photo so not check required")
                                    validMatch = True
                                else:
                                    #print("check the parts: ", personName, ", in ", requirePhotoCheck)
                                    for part in personName.lower().split():
                                        part = part.strip()
                                        if len(part) > 2 and requirePhotoCheck.lower().find(part) >= 0:
                                            print("image url matches name: ", part)
                                            validMatch = True
                                            break

                                if validMatch:

                                    #print("found match............")

                                    cDiv, cDivLevel, cClassName = self.commonDiv(photoFirst_el, el)
                                    self.addFirst(schemaStructure, "photo", "div", cClassName, cDivLevel)

                                    cLi, cClassName = self.commonLi(photoFirst_el, el)
                                    if cLi is not None:
                                        self.addFirst(schemaStructure, "photo", "li", cClassName, None)

                                    cArticle  = self.commonArticle(photoFirst_el, el)
                                    if cArticle is not None:
                                        #print("-------------------  add first article ----------------")
                                        self.addFirst(schemaStructure, "photo", "article", None, None)

                                    cSection = self.commonSection(photoFirst_el, el)
                                    if cSection is not None:
                                        #print("-------------------  add first section ----------------")
                                        self.addFirst(schemaStructure, "photo", "section", None, None)


                            # setup check for name first boundary
                            nameFirst_el = el


                    jobTitle = profCheck.isProfileJobTitle(shortText)
                    if jobTitle is not None:

                        #print(">> title: ", jobTitle)
                        if profileTitle is None:
                            profileTitle = jobTitle

                        # if we are building schema then do this part
                        if boundaryAttribute is None:
                            self.addToElement(schemaStructure, "title", tagName, className, styleName)


                    department = profCheck.isProfileDepartment(shortText)
                    if department is not None:

                        #print(">> department: ", department)
                        if profileDepartment is None:
                            profileDepartment = department

                        # if we are building schema then do this part
                        if boundaryAttribute is None:
                            self.addToElement(schemaStructure, "department", tagName, className, styleName)




                email_address = None
                if el.xpath('@href').get():

                    href = el.xpath('@href').get()
                    #print("href: ", href)
                    if href.find("mailto:") >= 0:

                        #print('................... tttttttttxt: ', str(el))
                        email = href.replace("mailto:", "")
                        if email != "" and email_address is None:
                            email_address = email
                            #print("add: ", email_address)

                        '''
                        # check if there is text displayed,  problem is something there is just a mail symbol
                        email_text = ''
                        email_texts = el.xpath('text()').extract()
                        if len(email_texts) > 0:
                            email_text = email_texts[0].strip()

                        if email_text == '':
                            print("----------- no email text")

                        if email_text != '':
                            email = href.replace("mailto:", "")
                            if email != "" and email_address is None:
                                print("add: ", email_address)
                                email_address = email
                                break
                        '''


                # get mailto inside elements
                if email_address is None:
                    email_elements = el.xpath('.//text()[contains(., "@")]')
                    for emailEl in email_elements:
                        email = emailEl.get().strip()
                        #print("email text: ", email)
                        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                        emails = re.findall(email_pattern, email)
                        if len(emails) > 0:
                            # set email but don't use this to define a schema element
                            email_address = emails[0]
                            #print("******** found email from text: ", email_address)


                if email_address != None:

                    print(">> email: ", email_address)
                    if profileEmail is None:
                        profileEmail = email_address

                        # if we are building schema then do this part
                        if boundaryAttribute is None:
                            self.addToElement(schemaStructure, "email", tagName, className, styleName)

                            if nameFirst_el is not None:

                                cDiv, cDivLevel, cClassName = self.commonDiv(nameFirst_el, el)
                                self.addFirst(schemaStructure, "name", "div", cClassName, cDivLevel)

                                cLi, cClassName = self.commonLi(nameFirst_el, el)
                                if cLi is not None:
                                    self.addFirst(schemaStructure, "name", "li", cClassName, None)

                                cArticle = self.commonArticle(nameFirst_el, el)
                                if cArticle is not None:
                                    # print("-------------------  add first article ----------------")
                                    self.addFirst(schemaStructure, "name", "article", None, None)

                                cSection = self.commonSection(nameFirst_el, el)
                                if cSection is not None:
                                    # print("-------------------  add first section ----------------")
                                    self.addFirst(schemaStructure, "name", "section", None, None)




                # get image source
                img_src = None
                # get photo inside elements
                if el.xpath('@src').get():
                    img_src = el.xpath('@src').get()

                    # if this is an svg thing like popupbox then set to None
                    if img_src.find("data:image/svg+xml") >= 0:
                        img_src = None

                if img_src is None and el.xpath('@data-src').get():
                    img_src = el.xpath('@data-src').get()

                    # if this is an svg thing like popupbox then set to None
                    if img_src.find("data:image/svg+xml") >= 0:
                        img_src = None

                if img_src is None and el.xpath('@style').get():
                    st = el.xpath('@style').get()
                    if st.find("background:url") >= 0:
                        parts = re.findall(r'\((.*?)\)', st)
                        if len(parts) > 0:
                            img_src = parts[0]
                    elif st.find("background-image:url") >= 0:
                        parts = re.findall(r'\((.*?)\)', st)
                        if len(parts) > 0:
                            img_src = parts[0]


                if el.xpath('@data-src').get():
                    img_src = el.xpath('@data-src | @srcset').get()

                if el.xpath('@srcset').get():
                    # get highest resolution image if one exists
                    img_src = el.xpath('@srcset').get()
                    imgEls = img_src.split(",")
                    img_src = imgEls[-1].split()[0]
                    #print("img src from source source set: ", img_src)


                if img_src is not None:

                    #print('.................  img_src: ', img_src)

                    if self.isSmallerThan(el, 100) == True:
                        continue


                    #print("***************************** img src found: ", img_src)

                    isCDN = False
                    if img_src.startswith("https://images.squarespace-cdn.com") or \
                            img_src.find("cloudfront.net") > 0 or \
                            img_src.find("smushcdn.com") > 0 or \
                            img_src.startswith("https://storage2.snappages.site") or \
                            img_src.startswith("https://cdn.monkplatform.com") or \
                            img_src.startswith("https://static.wixstatic.com") or \
                            img_src.startswith("https://cdn.monkplatform.com") or \
                            img_src.find("exactdn.com") > 0 or \
                            img_src.startswith("https://static.wixstatic.com") or \
                            img_src.find("s3.amazonaws.com") > 0 or \
                            img_src.startswith("https://s3.amazonaws.com/media.cloversites.com"):
                        isCDN = True


                    parsed_url = urlparse(response.url)
                    domain = parsed_url.netloc

                    img_src = img_src.replace("..", "")

                    if img_src.startswith('/') == True and img_src.startswith('//') == False:
                        img_src = "https://" + domain + img_src

                    #print("img src: ", img_src)

                    if isCDN or img_src.find(domain.replace("www.", "")) >= 0:

                        #print("********** check photo ****** ", img_src)
                        foundPhoto, foundProfilePhoto = profCheck.isProfilePhoto(img_src, 2, 15)
                        if foundPhoto:

                            tagName = el.xpath('name()').extract()[0]

                            requirePhotoCheck = None
                            if foundProfilePhoto == False:
                                requirePhotoCheck = os.path.basename(img_src)
                                #requirePhotoCheck = img_src
                                #print("did not find person in photo: ", requirePhotoCheck)
                            #else:
                                #print("found person in photo: ", img_src )


                            print(">> photo: ", img_src)
                            print(">> requirePhotoCheck: ", requirePhotoCheck)

                            # if boundary has been hit and this is a photo boundary then clear everything
                            if  hasHitBoundaryBefore is not None:
                                if profilePhoto is None:
                                    profilePhoto = img_src

                            # if we are building schema then do this part
                            if boundaryAttribute is None:
                                self.addToElement(schemaStructure, "photo", tagName, className, styleName)

                                photoFirst_el = el

                                # if we are building schema then do this part
                                if nameFirst_el is not None:

                                    cDiv, cDivLevel, cClassName = self.commonDiv(nameFirst_el, el)
                                    self.addFirst(schemaStructure, "name", "div", cClassName, cDivLevel)

                                    cLi, cClassName = self.commonLi(nameFirst_el, el)
                                    if cLi is not None:
                                        self.addFirst(schemaStructure, "name", "li", cClassName, None)

                                    cArticle = self.commonArticle(nameFirst_el, el)
                                    if cArticle is not None:
                                        # print("-------------------  add first article ----------------")
                                        self.addFirst(schemaStructure, "name", "article", None, None)

                                    cSection = self.commonSection(nameFirst_el, el)
                                    if cSection is not None:
                                        # print("-------------------  add first section ----------------")
                                        self.addFirst(schemaStructure, "name", "section", None, None)



        if hasHitBoundaryBefore is not None:

            self.evaluateToSetChurchContacts(currentChurch, boundaryAttribute, profilePhoto,
                                             requirePhotoCheck, profileName, profileTitle, profileDepartment,
                                             profileEmail, imageUrls)




        return schemaStructure



