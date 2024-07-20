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

class FindChurchOrganizations:


    churches_file_path = "churches.json"
    with open(churches_file_path, "r") as file:
        churchesData = json.load(file)
    churches = churchesData["churches"]



    def addToTheOrg(self, church, name, tag, value):

        theorg = {}
        if "theorg" in church:
            theorg = church["theorg"]

        if "contacts" not in theorg:
            theorg["contacts"] = []

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
        imgSrc = img.get('src')

        print("photo: ", imgSrc)
        self.addToTheOrg(church, name, "photo", imgSrc)


        for positionCard in soup.find_all('a', title="View on linkedIn"):

            href = positionCard.get('href')
            print("linkedin href: ", href)
            self.addToTheOrg(church, name, "linkedin", href)



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



        for positionCard in soup.find_all('div', class_="PositionCard_root__I4CrT"):

            cardNameAnch = positionCard.find('a', class_="PositionCard_info___JC8V")
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

            self.findPersonInfo(church, positionCardName, "https://theorg.com" + href)


