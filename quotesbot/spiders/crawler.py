# -*- coding: utf-8 -*-
import scrapy
import re
from quotesbot.profilecheck import ProfileCheck
from quotesbot.groupcheck import GroupCheck
from quotesbot.churchfinder import ChurchFinder
import json
from urllib.parse import urlparse

churches_file_path = "churches.json"
with open(churches_file_path, "r") as file:
    churchesData = json.load(file)
churches = churchesData["churches"]

class DivCount:
    def __init__(self, div, level, className, count):
        self.div = div
        self.level = level
        self.className = className
        self.count = count

class ChurchCrawler(scrapy.Spider):
    name = "crawler"

    #crawl church sites
    '''
    start_urls = []

    i = 1
    for church in churches:

        if "pages" not in church:

            if i > 0:
                url = church["link"]
                start_urls.append(url)

                print('urls: ', str(url))

            if i > 10000:
                break

        i = i + 1

    '''

    '''
    # crawl church reference sites
    start_urls = []

    i = 1
    for church in churches:
        if "references" in church:
            references = church["references"]
            for reference in references:

                if i > 0:
                    site = reference["site"]
                    url = reference["url"]

                    if site == "faithstreet":
                        start_urls.append(url)
                        print('urls: ', str(url))

                if i > 100:
                    break

            i = i + 1

    '''
    #crawl specific url
    start_urls = [
        "https://www.faithstreet.com/church/impact-rock-church-erie-co",
    ]



    def checkCommonDiv(self, el1, el2):
        s1 = str(el1)
        s2 = str(el2)

        if (s1 == s2):
            return True
        return False
    def commonDivCount(self, el1, el2):

        ancestors1 = el1.xpath('ancestor::div')
        ancestors2 = el2.xpath('ancestor::div')

        # print('look for common div 1: ', ancestors1)
        # print('look for common div 2: ', ancestors2)

        common_ancestor_div = None
        count = 1
        for ancestor1 in ancestors1[::-1]:
            s1 = str(ancestor1)
            # print('look for common div 1: ', s1)
            for ancestor2 in ancestors2[::-1]:
                s2 = str(ancestor2)
                # print('look for common div 2: ', s2)
                if s1 == s2:
                    common_ancestor_div = ancestor1
                    break
            if common_ancestor_div:
                break

            count = count + 1

        cnt = 0
        if common_ancestor_div != None:
            cnt = len(ancestors1) - count

        return cnt

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
            previousClassName = ""
            for ancestor2 in ancestors2[::-1]:
                s2 = str(ancestor2)
                # print('look for common div 2: ', s2)

                if s1 == s2:
                    #print('s1: ', s1)
                    print('class ', previousClassName.split()[0])
                    common_ancestor_div = ancestor1
                    common_ancestor_class = previousClassName.split()[0]
                    break

                previousClassName = ancestor2.attrib.get("class", "")
            if common_ancestor_div:
                break

            count = count + 1

        cnt = 0
        if common_ancestor_div != None:
            common_ancestor_count = len(ancestors1) - count
            #common_ancestor_class = common_ancestor_div.xpath('//div/@class')

        print('classname: ', common_ancestor_class)
        return common_ancestor_div, common_ancestor_count, common_ancestor_class


    def getBoundingDiv(self, els):
        print("look for lowest common div")
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

        print("lowest: ", bestDivLevel)
        return bestDiv, bestClassName


    def getContact(self, contacts, name, email):

        for contact in contacts:
            if name != "" and contact["name"] == name:
                return contact
            if email != "" and contact["email"] == email:
                return contact

        return None

    def saveContact(self, currentChurch,
        currentProfilePhoto,
        currentProfileName,

        currentProfileTitle,
        currentProfileDepartment,
        currentProfileEmail,
        previousProfileEmail,

        currentProfilePhotoEl,
        currentProfileNameEl,

        currentProfileEmailEl,
        previousProfileEmailEl
    ):
        nameOffset = 0
        if currentProfileNameEl != "":
            nameOffset = self.commonDivCount(currentProfilePhotoEl, currentProfileNameEl)

        emailOffset = 0
        if currentProfileEmailEl != "":
            emailOffset = self.commonDivCount(currentProfilePhotoEl, currentProfileEmailEl)

        previousEmailOffset = 0
        if previousProfileEmailEl != "":
            previousEmailOffset = self.commonDivCount(currentProfilePhotoEl, previousProfileEmailEl)

        # get email before or after photo
        email = ""
        if previousEmailOffset <= emailOffset:
            email = currentProfileEmail
        else:
            email = previousProfileEmail

        # check that name is in email somewhere
        foundPart = False
        parts = currentProfileName.split()
        for part in parts:
            if email.lower().find(part.lower()) >= 0:
                foundPart = True
        if foundPart == False:
            email = ""

        # print("------- name offset: ", nameOffset)
        # print("------- email offset: ", emailOffset)
        # print("------- previous email offset: ", previousEmailOffset)

        contacts = []
        if "contacts" in currentChurch:
            contacts = currentChurch["contacts"]

        contact = self.getContact(contacts, currentProfileName, email)
        if contact is None:
            contact = {}
            contacts.append(contact)

        contact["name"] = currentProfileName
        if email is not None:
            contact["email"] = email
        if currentProfileTitle is not None:
            contact["title"] = currentProfileTitle
        if currentProfileDepartment is not None:
            contact["department"] = currentProfileDepartment
        if currentProfilePhoto is not None:
            contact["photo"] = currentProfilePhoto

        currentChurch["contacts"] = contacts
        self.saveChurch(currentChurch)

        print("")
        print("contact record:")
        print("name: ", currentProfileName)
        print("title: ", currentProfileTitle)
        print("department: ", currentProfileDepartment)

        print('photo: ', currentProfilePhoto)
        print('email: ', email)





    def saveEmailContact(self,
        currentChurch,
        currentProfileName,
        currentProfileEmail
    ):

        # check that name is in email somewhere
        foundPartInEmail = False
        parts = currentProfileName.split()
        for part in parts:
            if currentProfileEmail.lower().find(part.lower()) >= 0:
                foundPartInEmail = True


        if foundPartInEmail:

            contacts = []
            if "contacts" in currentChurch:
                contacts = currentChurch["contacts"]

            contact = self.getContact(contacts, currentProfileName, currentProfileEmail)
            if contact is None:
                contact = {}
                contacts.append(contact)

                contact["name"] = currentProfileName
                if currentProfileEmail is not None:
                    contact["email"] = currentProfileEmail


                currentChurch["contacts"] = contacts
                self.saveChurch(currentChurch)

            print("")
            print("contact record (email):")
            print("name: ", currentProfileName)
            print("email: ", currentProfileEmail)


    def replace_multiple_spaces(self, text):
        # Replace multiple spaces with just one space
        cleaned_text = re.sub(r'\s+', ' ', text)
        return cleaned_text

    def saveChurch(self, currentChurch):

        # save to churches file
        churchesData["churches"] = churches
        with open(churches_file_path, "w") as json_file:
            json.dump(churchesData, json_file, indent=4)


    def getPage(self, pages, type, url):

        for page in pages:
            if page["type"] == type and page["url"] == url:
                return page

        return None



    def crawlFaithStreet(self, currentChurch, response):

        print('**************** process page: ', response.url)
        # itemtype="https://schema.org/Church"
        non_visible_pattern = re.compile(
            r'[\t\n\r\f\v]')  # matches tabs, newlines, carriage returns, form feeds, vertical tabs, and whitespace


        churchName = response.xpath("//h1[@itemprop='name']/text()").extract()[0]
        churchName = non_visible_pattern.sub('', churchName)
        print("church name: ", churchName)

        description = response.xpath(
            "//div[@itemprop='description']//p/text()").extract()[0]
        description = non_visible_pattern.sub('', description)
        print("church description: ", description)

        # https://schema.org/PostalAddress
        streetAddress = response.xpath("//span[@itemprop='streetAddress']/text()").extract()[0]
        print("church streetAddress: ", streetAddress)

        addressLocality = response.xpath("//span[@itemprop='addressLocality']/text()").extract()[0]
        print("church addressLocality: ", addressLocality)

        addressRegion = response.xpath("//span[@itemprop='addressRegion']/text()").extract()[0]
        print("church addressRegion: ", addressRegion)

        postalCode = response.xpath("//span[@itemprop='postalCode']/text()").extract()[0]
        print("church postalCode: ", postalCode)

        latitude = response.xpath("//meta[@itemprop='latitude']/@content").extract()[0]
        print("church latitude: ", latitude)

        longitude = response.xpath("//meta[@itemprop='longitude']/@content").extract()[0]
        print("church longitude: ", longitude)

        vibes = response.xpath("//dt[text()='Vibe']/following-sibling::dd//a/text()").extract()
        vibesStr = ""
        for vibe in vibes:
            if vibesStr == "":
                vibesStr = vibesStr + vibe
            else:
                vibesStr = vibesStr + ", " + vibe
        print("church vibe: ", vibesStr)

        programs = response.xpath("//dt[text()='Programs']/following-sibling::dd//a/text()").extract()
        programsStr = ""
        for program in programs:
            if programsStr == "":
                programsStr = programsStr + program
            else:
                programsStr = programsStr + ", " + program
        print("church programs: ", programsStr)

        musics = response.xpath("//dt[text()='Music']/following-sibling::dd//a/text()").extract()
        musicStr = ""
        for music in musics:
            if musicStr == "":
                musicStr = musicStr + music
            else:
                musicStr = musicStr + ", " + music
        print("church music: ", musicStr)

        denominations = response.xpath("//dt[text()='Denomination']/following-sibling::dd//a/text()").extract()
        denominationsStr = ""
        for denomination in denominations:
            if denominationsStr == "":
                denominationsStr = denominationsStr + denomination
            else:
                denominationsStr = denominationsStr + ", " + denomination
        print("church denomination: ", denominationsStr)

        size = ""
        sizes = response.xpath("//dt[text()='Size']/following-sibling::dd/text()").extract()
        if len(sizes) > 0:
            size = sizes[0]
        print("church size: ", size)

        languages = response.xpath("//dt[text()='Language']/following-sibling::dd//a/text()").extract()
        languagesStr = ""
        for language in languages:
            if languagesStr == "":
                languagesStr = languagesStr + language
            else:
                languagesStr = languagesStr + ", " + language
        print("church language: ", languagesStr)



        founded = ""
        foundeds = response.xpath("//dt[text()='Founded']/following-sibling::dd/text()").extract()
        if len(foundeds) > 0:
            founded = foundeds[0]
        print("church founded: ", founded)


        siteUrl = ""
        url_href = response.xpath("//div[contains(@class, 'church__description')]//a[@class='text-link' and @target='_blank']/@href").extract()
        if url_href is not None and len(url_href) > 0:
            siteUrl = url_href[0]
            print('church site href: ', siteUrl)

        phone = ""
        phone_href = response.xpath(
            "//div[contains(@class, 'church__description')]//a[@class='text-link' and not(@target='_blank')]/@href").extract()
        if phone_href is not None and len(phone_href) > 0:
            phone = phone_href[0].replace("tel:", "")
            print('church phone href: ', phone)

        currentChurch["name"] = churchName
        if "description" not in currentChurch:
            currentChurch["description"] = description
        if "street" not in currentChurch:
            currentChurch["street"] = streetAddress
        if "city" not in currentChurch:
            currentChurch["city"] = addressLocality
        if "state" not in currentChurch:
            currentChurch["state"] = addressRegion
        if "zip" not in currentChurch:
            currentChurch["zip"] = postalCode
        if "latitude" not in currentChurch:
            currentChurch["latitude"] = latitude
        if "longitude" not in currentChurch:
            currentChurch["longitude"] = longitude

        currentChurch["vibe"] = vibesStr
        currentChurch["programs"] = programsStr
        currentChurch["music"] = musicStr
        currentChurch["denomination"] = denominationsStr
        currentChurch["size"] = size
        currentChurch["language"] = languagesStr
        currentChurch["founded"] = founded

        if "link" not in currentChurch:
            currentChurch["link"] = siteUrl
        if "phone" not in currentChurch:
            currentChurch["phone"] = phone

        self.saveChurch(currentChurch)



    def searchForContacts(self, currentChurch, response):
        #print('**************** process page: ', response.url)

        if response.url.find(".pdf") >= 0:
            return


        if response.url.find('staff') != -1 or \
                response.url.find('about') != -1 or \
                response.url.find('leader') != -1 or \
                response.url.find('team') != -1 or \
                response.url.find('leader') != -1 or \
                response.url.find('pastor') != -1:

            pages = []
            if "pages" in currentChurch:
                pages = currentChurch["pages"]

            page = self.getPage(pages, "staff", response.url)
            if page is None:
                page = {
                    "type": "staff",
                    "url": response.url
                }
                pages.append(page)

            print("--------- save page: ", response.url)
            currentChurch["pages"] = pages
            self.saveChurch(currentChurch)

            print("--------- parse page: ", response.url)
            profCheck = ProfileCheck()

            # track using photo as reset element
            currentProfilePhoto = ""
            currentProfileName = ""
            currentProfileTitle = ""
            currentProfileDepartment = ""
            currentProfileEmail = ""
            previousProfileEmail = ""

            currentProfilePhotoEl = ""
            currentProfileNameEl = ""

            currentProfileEmailEl = ""
            previousProfileEmailEl = ""

            # track using email as reset element
            trackEmailCurrentName = ""
            trackEmailCurrentEmail = ""

            path = response.xpath(
                '//p | //div[not(descendant::div)] | //a[starts-with(@href, "mailto:")] | //img | //h1 | //h2 | //h3 | //h4 | //h5 | //h6 |  //strong | //span ')
            for el in path:
                #print("el: ", el)

                #print("--------------- Look for Profile Info -----------------------")

                visible_text = el.xpath('.//text()[normalize-space()]').extract()
                text = self.replace_multiple_spaces(' '.join(visible_text))

                # text in visible_text:
                #    text = self.replace_multiple_spaces(text)

                shortText = text.strip()[:120]
                if len(shortText) > 5:
                    #print("short text: ", shortText)

                    personName = profCheck.isPersonName(shortText)
                    if personName is not None:

                        if currentProfileName == "":
                            currentProfileName = personName

                        trackEmailCurrentName = personName
                        #print("found profile name ", currentProfileName)

                    '''
                    email = profCheck.isEmailAddresses(shortText)
                    if email is not None:
                        currentProfileEmail = email

                        trackEmailCurrentEmail = email
                        if trackEmailCurrentName != "":
                            self.saveEmailContact(
                                trackEmailCurrentName,
                                currentProfileTitle,
                                currentProfileDepartment,
                                trackEmailCurrentEmail
                            )

                        print("found email: ", email)
                    '''

                    jobTitle = profCheck.isProfileJobTitle(shortText)
                    if jobTitle is not None:
                        if currentProfileTitle == "":
                            currentProfileTitle = jobTitle
                            #print("found profile jobtitle ", jobTitle)

                    department = profCheck.isProfileDepartment(shortText)
                    if department is not None:
                        if currentProfileDepartment == "":
                            currentProfileDepartment = department
                            #print("found profile department ", department)

                # for link in mailto_links:
                if el.xpath('@href').get():
                    email_address = el.xpath('@href').get().replace("mailto:", "")

                    #print("found profile email ", email_address)

                    currentProfileEmail = email_address
                    currentProfileEmailEl = el

                    trackEmailCurrentEmail = email_address
                    if trackEmailCurrentName != "":
                        self.saveEmailContact(
                            currentChurch,
                            trackEmailCurrentName,
                            trackEmailCurrentEmail
                        )

                        trackEmailCurrentName = ""
                        trackEmailCurrentName = ""






                # Look for profile photo's

                # Extract image URLs from the page
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
                        #print("add on domain: ", img_src)
                        img_src = "https://" + domain + img_src


                    if isCDN or img_src.find(domain.replace("www.", "")) >= 0:
                        #print("********** check photo ****** ", img_src)
                        if profCheck.isProfilePhoto(img_src):

                            #print("photo found: ", img_src)

                            if currentProfilePhoto != "" and currentProfileName != "":
                                self.saveContact(currentChurch,
                                                 currentProfilePhoto,
                                                 currentProfileName,#

                                                 currentProfileTitle,
                                                 currentProfileDepartment,
                                                 currentProfileEmail,
                                                 previousProfileEmail,

                                                 currentProfilePhotoEl,
                                                 currentProfileNameEl,

                                                 currentProfileEmailEl,
                                                 previousProfileEmailEl)

                            previousProfileEmail = currentProfileEmail
                            previousProfileEmailEl = currentProfileEmailEl

                            currentProfilePhoto = img_src
                            currentProfileName = ""
                            currentProfileTitle = ""
                            currentProfileDepartment = ""
                            currentProfileEmail = ""

                            currentProfilePhotoEl = el
                            currentProfileNameEl = ""
                            currentProfileEmailEl = ""



            if currentProfilePhoto != "" and currentProfileName != "":
                self.saveContact(currentChurch,
                                 currentProfilePhoto,
                                 currentProfileName,

                                 currentProfileTitle,
                                 currentProfileDepartment,
                                 currentProfileEmail,
                                 previousProfileEmail,

                                 currentProfilePhotoEl,
                                 currentProfileNameEl,

                                 currentProfileEmailEl,
                                 previousProfileEmailEl)


    def searchForGroups(self, response):

        groupCheck = GroupCheck()




        if response.url.find('group') != -1:
            print('**************** search group page: ', response.url)

            groupElements = []

            path = response.xpath('//h1 | //h2 | //h3 | //h4 | //strong | //p | //span ')
            for el in path:
                # print("--------------- Look for Profile Info -----------------------")

                visible_text = el.xpath('.//text()[normalize-space()]').extract()
                for text in visible_text:
                    #print("check text for group name: ", text)
                    #print("text: ", text[:50])
                    if groupCheck.isGroupName(text):
                        groupElements.append(el)
                        print("group name: ", text)

            if len(groupElements) > 1:
                #print("get bounding div: ", len(groupElements))
                boundingDiv, boundingClassName = self.getBoundingDiv(groupElements)
                html = str(boundingDiv)
                print('div class name: ', boundingClassName)
                groupCheck.lookForGroupNames(html, boundingClassName)

    def findCurrentChurch(self, url):
        currentChurch = None
        for church in churches:

            churchParse = urlparse(church["link"])
            churchDomain = churchParse.netloc

            urlParse = urlparse(url)
            urlDomain = urlParse.netloc

            if churchDomain == urlDomain:
                currentChurch = church
                break

        return currentChurch

    def findCurrentChurchReference(self, url):
        currentChurch = None
        for church in churches:

            if "references" in church:
                references = church["references"]
                for reference in references:
                    if "url" in reference:
                        if reference["url"] == url:
                            currentChurch = church
                            break

        return currentChurch

    def parse(self, response):

        if response.url.find(".pdf") >= 0 or \
           response.url.find(".zip") >= 0:
                return

        churchFinder = ChurchFinder()
        churchFinder.findChurchesUsingNonProfitData()
        #churchFinder.findCityDemographicsFromCensusData()
        #churchFinder.findCityDemographics()
        #churchFinder.findCities()
        #churchFinder.findChurches()

        #crawl reference urls
        print("parse site: ", response.url)
        currentChurch = self.findCurrentChurchReference(response.url)
        if currentChurch == None:
            print("not found church for url: ", response.url)
            return

        self.crawlFaithStreet(currentChurch, response)

        '''
        # crawl church urls
        #print("parse site: ", response.url)
        currentChurch = self.findCurrentChurch(response.url)
        if currentChurch == None:
            print("not found church for url: ", response.url)
            return

        self.searchForContacts(currentChurch, response)


        #self.searchForGroups(response)


        links = response.xpath('//a/@href').extract()
        for link in links:

            if link.find("https:") == -1 or link.find(response.url) >= 0:

                # Make sure the link is within the same domain to avoid crawling external sites
                pageLink = link.replace(response.url, "")
                count = pageLink.count("/")
                if pageLink != "" and \
                        pageLink != "/" and  \
                        pageLink.startswith('/') and  \
                        pageLink.find('?') == -1 and \
                        count < 4:

                    yield scrapy.Request(response.urljoin(pageLink), callback=self.parse)

        '''




