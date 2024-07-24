from quotesbot.groupcheck import GroupCheck
from urllib.parse import urlparse
import re
import os
from bs4 import BeautifulSoup
from bs4.element import Comment

class DivCount:
    def __init__(self, div, level, className, count):
        self.div = div
        self.level = level
        self.className = className
        self.count = count


class GroupExtractorBeautifulSoup:
    name = "groupextractor"

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

        ancestors1 = el1.find_parents('div')
        ancestors2 = el2.find_parents('div')

        # print('look for common div 1: ', ancestors1)
        # print('look for common div 2: ', ancestors2)

        common_ancestor_div = None
        common_ancestor_count = None
        common_ancestor_class = None

        count = 1
        for ancestor1 in ancestors1:
            s1 = str(ancestor1)
            for ancestor2 in ancestors2:
                s2 = str(ancestor2)

                if s1 == s2:

                    cls = None
                    if ancestor2.has_attr("class"):
                        cls = ancestor2.get("class")[0]

                    '''
                    if cls is None:
                        if ancestor2.has_attr("id"):
                            cls = ancestor2.get("id")[0]
                    if cls is None:
                        if ancestor2.has_attr("data-mesh-id"):
                            cls = ancestor2.get("data-mesh-id")[0]
                    '''

                    if cls is not None:

                        # print('s1: ', s1)
                        common_ancestor_div = ancestor1

                        if ancestor2.has_attr("class"):
                            common_ancestor_class = ancestor2.get("class")[0]

                        '''
                        if common_ancestor_class is None:
                            if ancestor2.has_attr("id"):
                                common_ancestor_class = ancestor2.get("id")[0]
                        if common_ancestor_class is None:
                            if ancestor2.has_attr("data-mesh-id"):
                                common_ancestor_class = ancestor2.get("data-mesh-id")[0]
                        '''

                        break

            if common_ancestor_div:
                break

            count = count + 1

        cnt = 0
        if common_ancestor_div != None:
            common_ancestor_count = len(ancestors1) - count

        return common_ancestor_div, common_ancestor_count, common_ancestor_class

    def commonLi(self, el1, el2):

        ancestors1 = el1.find_parents('li')
        ancestors2 = el2.find_parents('li')

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

        ancestors1 = el1.find_parents('article')
        ancestors2 = el2.find_parents('article')

        #print('look for common article 1: ', ancestors1)
        #print('look for common article 2: ', ancestors2)

        common_ancestor_article = None

        for ancestor1 in ancestors1:
            s1 = str(ancestor1)
            #print('look for common article 1: ', s1)
            for ancestor2 in ancestors2:
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

        ancestors1 = el1.find_parents('section')
        ancestors2 = el2.find_parents('section')

        #print('look for common section 1: ', ancestors1)
        #print('look for common section 2: ', ancestors2)

        common_ancestor_section = None

        for ancestor1 in ancestors1:
            s1 = str(ancestor1)
            #print('look for common section 1: ', s1)
            for ancestor2 in ancestors2:
                s2 = str(ancestor2)
                #print('look for common section 2: ', s2)

                if s1 == s2:
                    common_ancestor_section = ancestor1
                    #print('*********************** found common section ')
                    break

            if common_ancestor_section:
                break

        return common_ancestor_section

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

        heightStr = el.get('height')
        widthStr = el.get('width')

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
                print("set because of photo a: ", profileName)
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
                print("set because of profileName and email 1 a: name = ", profileName, ", email = ", profileEmail)
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


    def extractGroupsFromWebPageBeautifulSoup(self, currentChurch, url, soup: BeautifulSoup, boundaryAttribute,
                                            boundaryTag, boundaryClass):
        groupCheck = GroupCheck()

        hasHitBoundaryBefore = False
        groupName = None

        elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'strong', 'p', 'span'])
        for el in elements:

            processBoundarySection = False

            tagName = el.name
            # print("tag name: ", tagName)

            className = None
            classNames = el.get('class')
            if classNames != None and len(classNames) > 0:
                className = classNames[0].strip()

            if className is None or className == "":
                ids = el.get('id')
                if ids != None and len(ids) > 0:
                    className = ids[0]
                    # print("no class name but has id: ", className)

            if className is None or className == "":
                meshids = el.get('data-mesh-id')
                if meshids != None and len(meshids) > 0:
                    className = meshids[0]
                    # print("no class name but has data-mesh-id: ", className)

            styleName = None
            styleNames = el.get('style')
            if styleNames != None and len(styleNames) > 0:
                styleName = styleNames[0]
                # print("style name: ", styleName)

            evaluateBoundary = False

            # if we have boundary defined then don't process stuff until we hit boundary
            processBoundarySection = True
            if hasHitBoundaryBefore == False:
                processBoundarySection = False




            visible_text = ""
            for str in el.stripped_strings:
                visible_text = visible_text + " " + str

            # print("vis text: ", visible_text)

            shortText = visible_text.strip()[:120]
            if len(shortText) > 5:

                evaluateBoundary = False
                groupName = None

                # print("check text for group name: ", text)
                # print("text: ", text[:50])
                if groupCheck.isGroupName(shortText):
                    print("group name: ", shortText)
                    groupName = shortText
                    evaluateBoundary = True

                # check boundary condition and process
                if evaluateBoundary:

                    # make sure we are past first boundary before setting contact
                    if hasHitBoundaryBefore is not None:
                        print("----------------------  evaludate to add group: ", groupName,)
                        self.evaluateToSetChurchGroups(currentChurch, boundaryAttribute, groupName)

                    # print("----------  hit boundary before *************")
                    hasHitBoundaryBefore = True
                    processBoundarySection = True

                    groupName = None



            if processBoundarySection:

                visible_text = ""
                for str in el.stripped_strings:
                    visible_text = visible_text + " " + str

                if groupCheck.isGroupName(shortText):
                    print("group name: ", shortText)
                    groupName = shortText

                # print("vis text: ", visible_text)

                shortText = visible_text.strip()[:120]
                if len(shortText) > 5:

                    # print("short text: ", shortText)

                    personName = profCheck.isPersonName(shortText)
                    if personName is not None:

                        print(">> name: ", personName)
                        if profileName is None:
                            profileName = personName



                        # setup check for name first boundary
                        nameFirst_el = el

                    foundJobTitle = profCheck.isProfileJobTitle(shortText)
                    if foundJobTitle is not None:

                        # print(">> title: ", shortText)
                        if profileTitle is None:
                            profileTitle = shortText


                    foundDepartment = profCheck.isProfileDepartment(shortText)
                    if foundDepartment is not None:
                        #print(">> department: ", shortText)
                        if profileDepartment is None:
                            profileDepartment = shortText


                email_address = None
                if el.get('href') != None:

                    href = el.get('href')
                    # print("href: ", href)
                    if href.find("mailto:") >= 0:

                        # print('................... tttttttttxt: ', str(el))
                        email = href.replace("mailto:", "")
                        if email != "" and email_address is None:
                            email_address = email
                            print("add: ", email_address)


                if email_address != None:

                    print(">> email: ", email_address)
                    if profileEmail is None:
                        profileEmail = email_address


                # get image source
                img_src = None
                # get photo inside elements
                if el.get('src') != None:
                    img_src = el.get('src')

                    # if this is an svg thing like popupbox then set to None
                    if img_src.find("data:image/svg+xml") >= 0:
                        img_src = None

                if img_src is None and el.get('data-src'):
                    img_src = el.get('@data-src')

                    # if this is an svg thing like popupbox then set to None
                    if img_src.find("data:image/svg+xml") >= 0:
                        img_src = None

                if img_src is None and el.get('style') != None:
                    st = el.get('style')
                    if st.find("background:url") >= 0:
                        parts = re.findall(r'\((.*?)\)', st)
                        if len(parts) > 0:
                            img_src = parts[0]
                    elif st.find("background-image:url") >= 0:
                        parts = re.findall(r'\((.*?)\)', st)
                        if len(parts) > 0:
                            img_src = parts[0]

                if el.get('@data-src') != None:
                    img_src = el.get('@data-src')

                if el.get('@srcset') != None:
                    # get highest resolution image if one exists
                    img_src = el.get('@srcset')
                    imgEls = img_src.split(",")
                    img_src = imgEls[-1].split()[0]
                    # print("img src from source source set: ", img_src)

                if img_src is not None:

                    print('.................  img_src: ', img_src)

                    if self.isSmallerThan(el, 100) == True:
                        continue

                    print("***************************** img src found: ", img_src)

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

                    parsed_url = urlparse(url)
                    domain = parsed_url.netloc

                    img_src = img_src.replace("..", "")

                    if img_src.startswith('/') == True and img_src.startswith('//') == False:
                        img_src = "https://" + domain + img_src

                    # print("img src: ", img_src)

                    if isCDN or img_src.find(domain.replace("www.", "")) >= 0:

                        print("********** check photo ****** ", img_src)
                        foundPhoto, foundProfilePhoto = profCheck.isProfilePhoto(img_src, 2, 15)
                        if foundPhoto:

                            print("********* found photo: ", foundPhoto)
                            tagName = el.name

                            requirePhotoCheck = None
                            if foundProfilePhoto == False:
                                requirePhotoCheck = os.path.basename(img_src)
                                # requirePhotoCheck = img_src
                                # print("did not find person in photo: ", requirePhotoCheck)
                            # else:
                            # print("found person in photo: ", img_src )

                            print(">> photo: ", img_src)
                            print(">> requirePhotoCheck: ", requirePhotoCheck)

                            # if boundary has been hit and this is a photo boundary then clear everything
                            if hasHitBoundaryBefore is not None:
                                if profilePhoto is None:
                                    profilePhoto = img_src


        if hasHitBoundaryBefore is not None:
            self.evaluateToSetChurchContacts(currentChurch, boundaryAttribute, profilePhoto,
                                             requirePhotoCheck, profileName, profileTitle, profileDepartment,
                                             profileEmail, imageUrls)

    def constructSchema(self, currentChurch, url, soup: BeautifulSoup):

        groupCheck = GroupCheck()

        schemaStructure = {
            "name": {
                "tags": [],
                "first": []
            }
        }


        photoFirst_el = None
        nameFirst_el = None
        requirePhotoCheck = None
        profileName = None
        profileTitle = None
        profileEmail = None


        elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'strong', 'p', 'span'])
        for el in elements:

            tagName = el.name
            #print("tag name: ", tagName)

            className = None
            classNames = el.get('class')
            if classNames != None and len(classNames) > 0:
                className = classNames[0].strip()

            if className is None or className == "":
                ids = el.get('id')
                if ids != None and len(ids) > 0:
                    className = ids[0]
                    #print("no class name but has id: ", className)

            if className is None or className == "":
                meshids = el.get('data-mesh-id')
                if meshids != None and len(meshids) > 0:
                    className = meshids[0]
                    #print("no class name but has data-mesh-id: ", className)

            styleName = None
            styleNames = el.get('style')
            if styleNames != None and len(styleNames) > 0:
                styleName = styleNames[0]
                #print("style name: ", styleName)


            visible_text = ""
            for str in el.stripped_strings:
                visible_text = visible_text + " " + str

            #print("vis text: ", visible_text)


            shortText = visible_text.strip()[:120]
            if len(shortText) > 5:

                # print("check text for group name: ", text)
                # print("text: ", text[:50])
                if groupCheck.isGroupName(shortText):
                    print("group name: ", shortText)

                    self.addToElement(schemaStructure, "name", tagName, className, styleName)
                    self.addFirst(schemaStructure, "name", tagName, className, None)



        return schemaStructure



    def extractProfilesUsingSchema(self, currentChurch, url, soap, schemaStructure):

        print("+++++++++++++++++++++++++++++++++++++++++")
        print("+++++++++++++++++++++++++++++++++++++++++")
        print("+++++++++++++++++++++++++++++++++++++++++")
        print("schema", schemaStructure)

        if "first" in schemaStructure["name"] and len(schemaStructure["name"]["first"]) > 0:

            cls = None
            level = None

            sorted_data = sorted(schemaStructure["name"]["first"], key=lambda x: x['count'], reverse=True)

            processed = 0
            lastTag = None
            lastCls = None
            for tagData in sorted_data:

                count = tagData["count"]
                tag = tagData["tag"].strip()
                cls = tagData["class"].strip()

                print("name first boundary ===> tag: >", tag, "<, cls: >", cls, ", count, ", count)


                if tag == "div" and level is not None and level > 2 and count >= 1:
                    processed = processed + 1
                    print(">>>>>>>>>>>>>>>>>>>>>>>>  call name for boundary tag: ", tag, ", and class: ", cls)
                    self.extractGroupsFromWebPageBeautifulSoup(currentChurch, url, soap, "name", tag, cls)

                print("processed: ", processed)
                if processed >= 2:
                    break


                lastTag = tag
                lastCls = cls





