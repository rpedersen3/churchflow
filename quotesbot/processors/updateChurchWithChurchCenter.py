import json
import re
import base64
from io import BytesIO
from PIL import Image
import os
import urllib.parse

from quotesbot.utilities.helpers import Helpers

from quotesbot.utilities.profileextractor import ProfileExtractor

from scrapy_splash import SplashRequest

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


import time
import requests


class UpdateChurchWithChurchCenter:

    helpers = Helpers()


    def processChurchCenterForDomain(self, church):

        changed = False

        foundPage = None
        url = None

        if "link" in church:
            url = church["link"]

        if "chmss" in church:
            foundChurchCenter = False
            for chms in church["chmss"]:
                if "type" in chms and chms["type"] == "churchcenter":

                    foundChms = chms

                    if "pages" in chms:
                        for page in chms["pages"]:
                            foundPage = page
                            break

                    break

        if foundPage != None and url != None and url.find(".churchcenter.com") < 0:

            try:

                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service)

                url = url
                driver.get(url)

                # Wait for the page to load completely
                time.sleep(1)  # Increase this if necessary for your connection


                # Get the page source and parse it with BeautifulSoup
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                driver.quit()

                #print("soup: ", soup)
                churchcenterDomain = None
                a_tags = soup.find_all('a')
                hrefs = [a.get('href') for a in a_tags if a.get('href') is not None]
                for href in hrefs:
                    print("href: ", href)
                    if href.find("churchcenter.com") >= 0:
                        print("decode: ", href)
                        offset = href.find("https://")
                        if offset >= 0:
                            offset = offset + 8
                            churchCenterUrl = href[offset:]

                            offsetEnd = churchCenterUrl.find("churchcenter.com")
                            churchcenterDomain = "https://" + churchCenterUrl[:offsetEnd-1] + ".churchcenter.com"
                            print("found domain: ", churchcenterDomain)
                            break

                if churchcenterDomain != None:
                    print("update domain: ", churchcenterDomain)
                    foundPage["url"] = churchcenterDomain
                    changed = True

            except:
                print("error getting url content")

        return changed

    def processChurchCenterGroupDetails(self, church, ministryClassification, group,
                                        groupCategoryName, groupCategoryDescription, groupCategoryUrl,
                                        groupName, groupDescription, groupUrl):

        changed = False

        if groupUrl != None:

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service)

            url = groupUrl
            driver.get(url)

            # Wait for the page to load completely
            time.sleep(3)  # Increase this if necessary for your connection

            # Get the page source and parse it with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.quit()

            # print("soup: ", soup)

            groupNameEl = soup.find(class_='fs-0')
            if groupNameEl != None:
                gName = groupNameEl.get_text()

            detailedDescriptionEl1 = soup.find(class_='pr-4@md')
            if detailedDescriptionEl1 != None:
                detailedDescriptionEl2 = detailedDescriptionEl1.find(class_='mt-2')
                if detailedDescriptionEl2 != None:
                    detailedDescription = detailedDescriptionEl2.get_text()
                    group["description"] = detailedDescription
                    print("detailed description: ", detailedDescription)

            if "leaders" not in group:
                group["leaders"] = []
                groupLeadersEl1s = soup.find_all(class_='mb-3')
                for groupLeadersEl1 in groupLeadersEl1s:
                    groupLeadersEl2 = groupLeadersEl1.find(class_='mt-1')
                    if groupLeadersEl2 != None:
                        groupLEls = groupLeadersEl2.find_all(class_="fs-4")
                        for groupLEl in groupLEls:

                            leaderFirstName = groupLEl.get_text()
                            print("leader firstname: ", leaderFirstName)

                            leader = {
                                "name": leaderFirstName
                            }
                            group["leaders"].append(leader)

            if "tags" not in group:
                group["tags"] = []
                groupBadgeEls = soup.find_all(class_='badge')
                for groupBadgeEl in groupBadgeEls:
                    groupBadge = groupBadgeEl.get_text()
                    badgePieces = groupBadge.split(":")
                    print("badge: ", groupBadge)
                    if len(badgePieces) > 1:
                        badgeType = badgePieces[0].strip()
                        badgeValue = badgePieces[1].strip()
                        print("badge type: ", badgeType, ", badge value: ", badgeValue)

                        tag = {
                            "type": badgeType,
                            "name": badgeValue
                        }
                        group["tags"].append(tag)

            if "location" not in group:
                locationEl = soup.find(class_='mb-4')
                if locationEl != None:

                    location = {}
                    group["location"] = location

                    campusNameEl = locationEl.find("p")
                    if campusNameEl != None:
                        campusName = campusNameEl.get_text()
                        print("location: ", campusName)
                        location["name"] = campusName


                    addressEl = locationEl.find("a")
                    if addressEl != None:
                        address = addressEl.get_text()
                        print("address: ", address)
                        location["address"] = address

        return changed

    def processChurchCenterGroupCategory(self, church, groupCategoryName, groupCategoryDescription, groupCategoryUrl):

        changed = False


        if groupCategoryUrl != None:

            changed = True

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service)

            url = groupCategoryUrl
            driver.get(url)

            # Wait for the page to load completely
            time.sleep(3)  # Increase this if necessary for your connection


            # Get the page source and parse it with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.quit()

            #print("soup: ", soup)

            ministryClassification = {
                "name": groupCategoryName,
                "description": groupCategoryDescription,
                "uri": groupCategoryUrl
            }
            ministryClassifications = [
                ministryClassification
            ]

            if "ministryClassifications" in church:
                ministryClassifications = church["ministryClassifications"]
                foundMinistryClassification = False
                for ministryClassificationRec in ministryClassifications:
                    if ministryClassificationRec["name"].lower() == groupCategoryName.lower():
                        ministryClassification = ministryClassificationRec
                        break
                if foundMinistryClassification == False:
                    ministryClassifications.append(ministryClassification)
            else:
                church["ministryClassifications"] = ministryClassifications




            if "tags" not in ministryClassification:
                ministryClassification["tags"] = []

                buttonEls = soup.find_all("button")
                for buttonEl in buttonEls:
                    buttonId = buttonEl.get("id")
                    buttonName = buttonEl.get_text()

                    div_element = soup.find('div', {'aria-labelledby': buttonId})
                    itemEls = div_element.find_all('div', {'role': "menuitem"})
                    for itemEl in itemEls:
                        value = itemEl.get_text();
                        print("button name: ", buttonName, ", item value: ", value)

                        tag = {
                            "type": buttonName,
                            "name": value
                        }
                        ministryClassification["tags"].append(tag)

            groupEls = soup.find_all(class_='css-1k2ec0g')

            # Print the contents of each element with class 'card-list'
            for groupEl in groupEls:
                groupNameEl = groupEl.find(class_='fs-3')
                if groupNameEl != None:
                    groupName = groupNameEl.get_text()

                    groupDescription = ""
                    groupDescriptionEl = soup.find(class_='css-l49wdp')
                    if groupDescriptionEl != None:
                        groupDescription = groupDescriptionEl.get_text()

                    groupHrefEl = groupEl.find("a")
                    if groupHrefEl != None:

                        groupHref = groupHrefEl.get('href')

                        print("group: ", groupName, ", href: ", groupHref)

                        group = {
                            "name": groupName,
                            "ministryClassifications": [
                                groupCategoryName.lower()
                            ]
                        }
                        groups = [
                            group
                        ]
                        if "groups" in church:
                            groups = church["groups"]
                            foundGroup = False
                            for groupsRec in groups:
                                if groupsRec["name"].lower() == groupName.lower():
                                    group = groupsRec
                                    break
                            if foundGroup == False:
                                groups.append(group)
                        else:
                            church["groups"] = groups

                        self.processChurchCenterGroupDetails(church, ministryClassification, group, groupCategoryName, groupCategoryDescription, groupCategoryUrl,
                                        groupName, groupDescription, groupHref)




        return changed

    def processChurchCenterGroups(self, church):

        changed = False


        url = None
        if "chmss" in church:
            foundChurchCenter = False
            for chms in church["chmss"]:
                if "type" in chms and chms["type"] == "churchcenter":
                    if "pages" in chms:
                        for page in chms["pages"]:
                            if "url" in page:
                                if page["url"].find(".churchcenter.com") >= 0:
                                    url = page["url"]
                                    break


        processor = "extract-groups-from-churchcenter-chromedriver"
        needsToBeProcessed = self.helpers.checkIfNeedsProcessing(church, processor, url)

        if needsToBeProcessed == True:

            if url != None and "ministryClassifications" not in church:

                changed = True

                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service)

                url = url + "/groups"
                driver.get(url)

                # Wait for the page to load completely
                time.sleep(3)  # Increase this if necessary for your connection


                # Get the page source and parse it with BeautifulSoup
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                driver.quit()

                #print("soup: ", soup)

                card_list_elements = soup.find_all(class_='card-list-item__wrapper-link')

                # Print the contents of each element with class 'card-list'
                for categoryEl in card_list_elements:
                    categoryNameEl = categoryEl.find('h2')
                    if categoryNameEl != None:
                        categoryName = categoryNameEl.get_text()

                        categoryDescriptionEl = soup.find(class_='fs-4')
                        if categoryDescriptionEl != None:
                            categoryDescription = categoryDescriptionEl.get_text()

                        categoryHref = categoryEl.get('href')

                        print("cat: ", categoryName, ", href: ", categoryHref)

                        self.processChurchCenterGroupCategory(church, categoryName, categoryDescription, categoryHref)



        return changed