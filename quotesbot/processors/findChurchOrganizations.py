import json
import re
import base64
from io import BytesIO
from PIL import Image
import os
import urllib.parse
from urllib.parse import urlparse

from quotesbot.utilities.helpers import Helpers

from quotesbot.utilities.profileextractor import ProfileExtractor

from scrapy_splash import SplashRequest

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


import time
import requests

class FindChurchOrganizations:


    churches_file_path = "churches.json"
    with open(churches_file_path, "r") as file:
        churchesData = json.load(file)
    churches = churchesData["churches"]


    def findContact(self, church, name):

        contactRecord = None

        theorg = {}
        if "theorg" in church:
            theorg = church["theorg"]

        for contact in theorg["contacts"]:
            if contact["name"].lower() == name.lower():
                contactRecord = contact
                break

        return contactRecord

    def addToTheOrg(self, church, name, tag, value):

        theorg = {}
        if "theorg" in church:
            theorg = church["theorg"]

        if "contacts" not in theorg:
            theorg["contacts"] = []

        theorg["valid"] = "yes"

        contactRecord = None
        for contact in theorg["contacts"]:
            if contact["name"].lower() == name.lower():
                contactRecord = contact
                break

        if contactRecord == None:
            contact = {
                "name": name
            }
            theorg["contacts"].append(contact)

        if tag not in contact:
            contact[tag] = value

        church["theorg"] = theorg


    def findPersonInfo(self, church, name, orgChartUrl):

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)

        driver.get(orgChartUrl)

        # Wait for the page to load completely
        time.sleep(1)  # Increase this if necessary for your connection

        # Get the page source and parse it with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()

        #print("soup: ", soup)

        img = soup.find('img', class_="hLdhge")
        if img != None:
            imgSrc = img.get('src')

            print("photo: ", imgSrc)
            self.addToTheOrg(church, name, "photo", imgSrc)


        for linkedinInfo in soup.find_all('a', title="View on linkedIn"):

            href = linkedinInfo.get('href')
            print("linkedin href: ", href)
            self.addToTheOrg(church, name, "linkedin", href)

        print("************ loop through sub folks ************")
        for positionCard in soup.find_all('a', class_="iZOAPd"):

            print("****************  get next level down")

            positionCardTitle = positionCard.find('p', class_="dLmfce").get_text()
            positionCardName = positionCard.find('p', class_="hTySEN").get_text()

            href = positionCard.get('href')
            url = "https://theorg.com" + href
            print("href: ", url)

            print(" look for name: ", positionCardName)
            contact = self.findContact(church, positionCardName)
            if contact == None:
                print("name not found so add")
                self.addToTheOrg(church, positionCardName, "name", positionCardName)
                self.addToTheOrg(church, positionCardName, "title", positionCardTitle)
                self.addToTheOrg(church, positionCardName, "details", url)
                self.addToTheOrg(church, name, "linkedin", href)

                print("go to next level ........")
                self.findPersonInfo(church, positionCardName, url)

    def findChurchOrganizationStructure(self, church, orgChartUrl):

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)


        driver.get(orgChartUrl)

        # Wait for the page to load completely
        time.sleep(1)  # Increase this if necessary for your connection

        # Get the page source and parse it with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()

        #print("soup: ", soup)


        foundWebsite = False
        websiteUrl = None
        for websiteAnch in soup.find_all('a', title="View the website"):

            websiteUrl = websiteAnch.get('href')
            if websiteUrl.find("http://") >= 0:
                websiteUrl.replace("http://", "https://")

            print("found church url: ", websiteUrl)

            if church != None:

                link = church["link"]
                if link.find("http://") >= 0:
                    link = link.replace("http://", "https://")
                if link.find("https://") == -1:
                    link = "https://" + link

                parsed_url = urlparse(link)
                churchDomain = parsed_url.netloc.replace("www.", "")
                churchDomain = churchDomain.replace("/", "")

                if churchDomain.strip() != "" and websiteUrl.lower().find(churchDomain.lower()) >= 0:
                    foundWebsite = True
                    break

            else:

                for churchRec in self.churches:
                    if "link" in churchRec:

                        link = churchRec["link"]
                        if link.find("http://") >= 0:
                            link = link.replace("http://", "https://")
                        if link.find("https://") == -1:
                            link = "https://" + link

                        parsed_url = urlparse(link)
                        churchDomain = parsed_url.netloc.replace("www.", "")
                        churchDomain = churchDomain.replace("/", "")

                        if churchDomain.strip() != "" and websiteUrl.lower().find(churchDomain.lower()) >= 0:
                            print("link: ", link)
                            print("domain: >", churchDomain, "<")
                            print("matched org url: ", websiteUrl, " to church domain: >", churchDomain, "<")
                            church = churchRec
                            foundWebsite = True
                            break

        if foundWebsite:
            print("found church: ", church["name"], " for domain: ", websiteUrl)
            for positionCard in soup.find_all('div', class_="PositionCard_root__I4CrT"):

                cardNameAnch = positionCard.find('a', class_="PositionCard_info___JC8V")
                cardTitle = positionCard.find('div', class_="PositionCard_role__XNUly")
                cardReports = positionCard.find('div', class_="PositionCard_childIndicator__VsHgE")
                if cardNameAnch != None and cardTitle != None and cardReports != None:

                    positionCardName = cardNameAnch.get_text()

                    positionCardTitle = positionCard.find('div', class_="PositionCard_role__XNUly").get_text()
                    positionCardReports = positionCard.find('div', class_="PositionCard_childIndicator__VsHgE").get_text()
                    print("name: ", positionCardName, ", title: ", positionCardTitle, ", reports: ", positionCardReports)

                    href = cardNameAnch.get('href')
                    url = "https://theorg.com" + href
                    print("href: ", url)

                    self.addToTheOrg(church, positionCardName, "name", positionCardName)
                    self.addToTheOrg(church, positionCardName, "title", positionCardTitle)
                    self.addToTheOrg(church, positionCardName, "number-of-reports", positionCardReports)
                    self.addToTheOrg(church, positionCardName, "details", url)

                    self.findPersonInfo(church, positionCardName, url)


