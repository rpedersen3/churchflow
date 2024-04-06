# -*- coding: utf-8 -*-
import scrapy
import re
from quotesbot.profilecheck import ProfileCheck
from quotesbot.groupcheck import GroupCheck
from quotesbot.churchfinder import ChurchFinder

class DivCount:
    def __init__(self, div, level, className, count):
        self.div = div
        self.level = level
        self.className = className
        self.count = count

class ChurchCrawler(scrapy.Spider):
    name = "crawler"
    #siteurl = 'https://www.calvarygolden.net'

    siteurl = "https://www.missionhills.org"

    #siteurl = "https://centcov.org"

    #siteurl = "https://calvarybible.com"

    #siteurl = 'https://truelightonline.org'

    #siteurl = 'https://www.houseofhopeaurora.org'

    #siteurl = 'https://www.horizondenver.com'

    #siteurl = "https://www.convergerockymountain.org"

    #siteurl = "https://www.wellspring.thecalvary.org"

    #siteurl = "https://longmontcalvary.org"

    #siteurl = "https://www.trinitylittleton.com"



    start_urls = [
        #'https://www.calvarygolden.net'

        'https://www.missionhills.org/groupfinder/'
        #'https://www.missionhills.org'

        #'https://centcov.org'

        #"https://calvarybible.com/adults-groups/"
        #'https://calvarybible.com'

        #'https://truelightonline.org'

        #'https://www.houseofhopeaurora.org'

        #'https://www.horizondenver.com/index.php/about-us/our-team/'

        #'https://www.convergerockymountain.org'

        #'https://www.wellspring.thecalvary.org'

        #'https://longmontcalvary.org/about/our-staff'

        #"https://www.trinitylittleton.com/staff"
        #"https://www.trinitylittleton.com"


        #'https://www.horizondenver.com/index.php/about-us/our-team/'
        #'https://www.highlandsumc.com/staff/'
        #'https://harborchurch.life/staff-oversight/'
        #'https://www.convergerockymountain.org/staff/'
        #'https://www.wellspring.thecalvary.org/leadership/'
        #'https://centcov.org/staff-elders/'
        #'https://calvarybible.com/staff/'
        #'https://www.missionhills.org/im-new/staff-elders/',
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


    def saveContact(self,
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

        # print("------- name offset: ", nameOffset)
        # print("------- email offset: ", emailOffset)
        # print("------- previous email offset: ", previousEmailOffset)

        print("")
        print("contact record:")
        print("name: ", currentProfileName)
        print("title: ", currentProfileTitle)
        print("department: ", currentProfileDepartment)

        print('photo: ', currentProfilePhoto)

        if previousEmailOffset <= emailOffset:
            print("email: ", currentProfileEmail)
        else:
            print("email: ", previousProfileEmail)

    def searchForContacts(self, response):

        # print('**************** process page: ', response.url)
        if response.url.find('staff') != -1 or \
                response.url.find('team') != -1 or \
                response.url.find('leadership') != -1 or \
                response.url.find('pastor') != -1:

            print("--------- parse page: ", response.url)
            profCheck = ProfileCheck()

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

            path = response.xpath(
                '//div[not(descendant::div)] | //a[starts-with(@href, "mailto:")] | //img | //h1 | //h2 | //h3 | //strong | //p | //span ')
            for el in path:
                # print("--------------- Look for Profile Info -----------------------")

                visible_text = el.xpath('.//text()[normalize-space()]').extract()
                for text in visible_text:
                    shortText = text.strip()[:40]
                    # print("short text: ", shortText)
                    names = shortText.split()
                    for name in names:
                        # print("name check: ", name)
                        if profCheck.isProfileName(name):
                            # print("found name: ", name)
                            l1 = len(currentProfileName.split())
                            if l1 == 0:
                                currentProfileName = name
                                currentProfileNameEl = el
                            elif l1 == 1 and self.checkCommonDiv(currentProfileNameEl, el):
                                currentProfileName += " "
                                currentProfileName += name
                            # elif l1 == 2  and self.checkCommonDiv(currentProfileNameEl, divEl):
                            #    currentProfileName += " "
                            #    currentProfileName += name

                            # print("found profile name ", currentProfileName)

                    if profCheck.isProfileJobTitle(shortText):
                        if currentProfileTitle == "":
                            currentProfileTitle = shortText
                        # print("found profile jobtitle ", shortText)

                    if profCheck.isProfileDepartment(shortText):
                        currentProfileDepartment = shortText
                        # print("found profile department ", shortText)

                # mailto_links = divEl.xpath('.//a[starts-with(@href, "mailto:")]')
                # for link in mailto_links:
                if el.xpath('@href').get():
                    email_address = el.xpath('@href').get().replace("mailto:", "")
                    # print("found profile email ", email_address)

                    currentProfileEmail = email_address
                    currentProfileEmailEl = el

                    yield {
                        'email_address': email_address
                    }

                # Look for profile photo's

                # Extract image URLs from the page
                if el.xpath('@src | @data-src | @srcset').get():
                    img_src = el.xpath('@src | @data-src | @srcset').get()
                    # print("***************************** img src found: ", img_src)

                    isCDN = False
                    if img_src.startswith("https://images.squarespace-cdn.com") or \
                            img_src.startswith("https://static.wixstatic.com") or \
                            img_src.startswith("https://s3.amazonaws.com/media.cloversites.com"):
                        isCDN = True

                    if (isCDN or img_src.startswith(self.siteurl)) and \
                            profCheck.isProfilePhoto(img_src):

                        # print("photo found: ", img_src)
                        if currentProfilePhoto != "" and currentProfileName != "":
                            self.saveContact(currentProfilePhoto,
                                             currentProfileName,

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

                        yield {
                            'image_url': img_src
                        }

            if currentProfilePhoto != "" and currentProfileName != "":
                self.saveContact(currentProfilePhoto,
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

    def parse(self, response):

        churchFinder = ChurchFinder()
        churchFinder.findCityDemographics()
        #churchFinder.findCities()
        #churchFinder.findChurches()

        '''
        #self.searchForContacts(response)
        self.searchForGroups(response)

        links = response.xpath('//a/@href').extract()
        for link in links:
            #print("link: ", link)
            # Make sure the link is within the same domain to avoid crawling external sites

            pageLink = link.replace(self.siteurl, "")
            count = pageLink.count("/")
            if pageLink != "" and \
                    pageLink != "/" and  \
                    pageLink.startswith('/') and  \
                    pageLink.find('?') == -1 and \
                    count < 5:

               yield scrapy.Request(response.urljoin(pageLink), callback=self.parse)

        '''





